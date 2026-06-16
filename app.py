"""
app.py — AI Shopping Assistant
Run with:  streamlit run app.py
"""
import sys, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
from config.settings import APP_TITLE, APP_ICON
from db.database import init_db
from vector_store.embeddings import build_index

from ui.search_tab import render as render_search
from ui.image_search_tab import render as render_image_search
from ui.product_card import render_product_detail
from ui.order_dialog import render as render_order_dialog, render_order_success
from ui.order_history_tab import render as render_order_history

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

@st.cache_resource(show_spinner="Setting up database and search index ...")
def startup():
    init_db()
    build_index()
    return True

startup()

defaults = {
    "active_tab":           "search",
    "last_query":           "",
    "search_done":          False,
    "selected_product":     None,
    "product_source_tab":   None,   # "search" | "image"
    "show_order_dialog":    False,
    "order_product":        None,
    "order_success":        False,
    "last_order":           None,
    "img_search_results":   [],
    "img_identified_query": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.markdown(f"# {APP_ICON} {APP_TITLE}")
st.caption("Search our store · View product details & ratings · Place orders")
st.divider()

render_order_success()

tab_search, tab_image, tab_history = st.tabs(
    ["🔍 Search Products", "🖼️ Image Search", "📋 Order History"]
)

source = st.session_state.get("product_source_tab")

with tab_search:
    if st.session_state.get("selected_product") and source == "search":
        render_product_detail(st.session_state["selected_product"])
        render_order_dialog(key_suffix="_search_detail")
    elif st.session_state.get("show_order_dialog") and source == "search":
        render_search()
        render_order_dialog(key_suffix="_search")
    else:
        render_search()

with tab_image:
    if st.session_state.get("selected_product") and source == "image":
        render_product_detail(st.session_state["selected_product"])
        render_order_dialog(key_suffix="_image_detail")
    elif st.session_state.get("show_order_dialog") and source == "image":
        render_image_search()
        render_order_dialog(key_suffix="_image")
    else:
        render_image_search()

with tab_history:
    render_order_history()
