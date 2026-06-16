import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
ui/image_search_tab.py — passes source_tab="image" to render_product_card
"""
import streamlit as st
from agents.image_search_agent import run as image_search
from ui.product_card import render_product_card

_SUPPORTED = ("image/jpeg", "image/png", "image/webp", "image/gif")


def render():
    st.markdown("### 🖼️ Search by Image")
    st.markdown("Upload a product photo **or** paste an image URL — we'll find it in our store.")

    mode = st.radio(
        "Input method",
        ["📁 Upload image", "🔗 Image URL"],
        horizontal=True,
        label_visibility="collapsed",
    )

    image_bytes = None
    media_type  = "image/jpeg"
    image_url   = ""
    preview_src = None

    if mode == "📁 Upload image":
        uploaded = st.file_uploader(
            "Upload a product image",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            label_visibility="collapsed",
        )
        if uploaded:
            image_bytes = uploaded.read()
            media_type  = uploaded.type if uploaded.type in _SUPPORTED else "image/jpeg"
            preview_src = image_bytes
    else:
        image_url = st.text_input(
            "Image URL",
            placeholder="https://example.com/product.jpg",
            label_visibility="collapsed",
        )
        if image_url.strip():
            preview_src = image_url.strip()

    if preview_src:
        st.image(preview_src, caption="Your image", width=260)

    search_clicked = st.button(
        "🔍 Find similar products",
        type="primary",
        disabled=not (image_bytes or image_url.strip()),
    )

    if search_clicked:
        with st.spinner("Analysing image with Claude Vision …"):
            result = image_search(
                image_bytes=image_bytes,
                media_type=media_type,
                image_url=image_url.strip(),
            )

        if not result["found"]:
            st.warning(result["message"])
            st.session_state["img_search_results"]    = []
            st.session_state["img_identified_query"]  = ""
            return

        st.session_state["img_search_results"]   = result["results"]
        st.session_state["img_identified_query"] = result.get("identified_query", "")
        st.session_state["selected_product"]     = None
        st.session_state["product_source_tab"]   = None

    # ── Show persisted results ────────────────────────────
    products = st.session_state.get("img_search_results", [])
    if not products:
        return

    identified = st.session_state.get("img_identified_query", "")
    if identified:
        st.info(f"🤖 Claude identified: **{identified}**")
    st.success(f"Found **{len(products)}** product(s) matching **'{identified}'**")
    st.divider()

    cols = st.columns(3)
    for i, product in enumerate(products):
        with cols[i % 3]:
            render_product_card(product, source_tab="image")
