import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
ui/product_card.py — fixed: unique button keys + product_source_tab tracking
"""
import streamlit as st
from agents.product_details_agent import run as get_details


def _star_bar(rating: float | None) -> str:
    if rating is None:
        return "No ratings yet"
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty + f"  {rating:.1f}"


def render_product_card(product: dict, source_tab: str = "search"):
    """
    source_tab: "search" | "image" — ensures button keys are unique across tabs.
    """
    with st.container(border=True):
        if product.get("is_organic"):
            st.markdown("🌿 **Organic**")

        st.markdown(f"**{product['name']}**")
        st.caption(f"Category: {product.get('category', '—').title()}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### ₹{product['price']:.2f}")
        with c2:
            rating = product.get("avg_rating")
            count  = product.get("review_count", 0)
            st.markdown(_star_bar(rating))
            if count:
                st.caption(f"{count} review{'s' if count != 1 else ''}")

        desc = product.get("description", "")
        st.caption(desc[:90] + "..." if len(desc) > 90 else desc)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("View Details",
                         key=f"detail_{source_tab}_{product['id']}",
                         use_container_width=True):
                st.session_state["selected_product"]   = product["id"]
                st.session_state["product_source_tab"] = source_tab
                st.session_state["active_tab"]         = "details"
                st.rerun()
        with b2:
            if st.button("🛒 Order",
                         key=f"order_{source_tab}_{product['id']}",
                         use_container_width=True, type="primary"):
                st.session_state["order_product"]      = product
                st.session_state["show_order_dialog"]  = True
                st.session_state["product_source_tab"] = source_tab
                st.rerun()


def render_product_detail(product_id: int):
    result = get_details(product_id)
    if not result["found"]:
        st.error(result["message"])
        return

    product = result["product"]
    reviews = result["reviews"]

    if st.button("← Back to results", key="back_to_results"):
        st.session_state["selected_product"]   = None
        st.session_state["product_source_tab"] = None
        st.session_state["active_tab"]         = "search"
        st.rerun()

    st.divider()

    col1, col2 = st.columns([3, 1])
    with col1:
        if product.get("organic_label"):
            st.markdown("🌿 **Organic Product**")
        st.markdown(f"## {product['name']}")
        st.caption(f"Category: {product.get('category', '—').title()}")
        st.markdown(f"### ₹{product['price']:.2f}")
    with col2:
        rating = product.get("avg_rating")
        st.metric(label="Avg Rating", value=f"{rating:.1f} / 5" if rating else "N/A")
        st.caption(f"{product.get('review_count', 0)} reviews")

    st.markdown(f"**Description:** {product.get('description', '—')}")
    st.divider()

    if st.button("🛒 Order this product", type="primary",
                 use_container_width=True, key="order_from_detail"):
        st.session_state["order_product"]     = product
        st.session_state["show_order_dialog"] = True
        st.rerun()

    st.divider()
    st.markdown(f"### Customer Reviews ({len(reviews)})")
    if not reviews:
        st.info("No reviews yet for this product.")
        return

    for rev in reviews:
        with st.container(border=True):
            rc1, rc2 = st.columns([3, 1])
            with rc1:
                st.markdown(f"**{rev.get('reviewer_name', 'Anonymous')}**")
                st.write(rev.get("review_text", ""))
            with rc2:
                stars = "★" * int(rev.get("rating", 0))
                st.markdown(f"**{stars}** {rev.get('rating', 0):.1f}")
