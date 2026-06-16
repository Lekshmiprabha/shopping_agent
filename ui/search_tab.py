import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
ui/search_tab.py — passes source_tab="search" to render_product_card
"""
import streamlit as st
from agents.text_search_agent import run as search
from ui.product_card import render_product_card


def render():
    st.markdown("### 🔍 Search Products")
    st.markdown("Search our store by name, category, or description.")

    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            label="search_input",
            placeholder="e.g.  organic honey,  dark roast coffee,  chia seeds ...",
            label_visibility="collapsed",
        )
    with col2:
        search_clicked = st.button("Search", use_container_width=True, type="primary")

    with st.expander("Filters", expanded=False):
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            organic_only = st.checkbox("🌿 Organic only")
        with fcol2:
            categories = ["All", "honey", "oil", "coffee", "tea",
                          "nuts", "seeds", "grains", "dairy-alt", "snacks"]
            selected_cat = st.selectbox("Category", categories)

    if search_clicked and query.strip():
        st.session_state["last_query"]        = query.strip()
        st.session_state["search_done"]       = True
        st.session_state["selected_product"]  = None
        st.session_state["product_source_tab"] = None

    if st.session_state.get("search_done") and st.session_state.get("last_query"):
        with st.spinner("Searching ..."):
            result = search(st.session_state["last_query"])

        if not result["found"]:
            st.warning(result["message"])
            return

        products = result["results"]
        if organic_only:
            products = [p for p in products if p.get("is_organic")]
        if selected_cat != "All":
            products = [p for p in products if p.get("category") == selected_cat]

        if not products:
            st.warning("No products match the selected filters.")
            return

        st.success(f"Found **{len(products)}** product(s) for **'{st.session_state['last_query']}'**")
        st.divider()

        cols = st.columns(3)
        for i, product in enumerate(products):
            with cols[i % 3]:
                render_product_card(product, source_tab="search")
