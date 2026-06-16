import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
ui/order_dialog.py — fixed: unique button keys
"""
import streamlit as st
from agents.checkout_agent import run as place_order


def render(key_suffix: str = ""):
    """
    key_suffix: pass a unique string per call site to avoid duplicate key errors.
    """
    if not st.session_state.get("show_order_dialog"):
        return

    product = st.session_state.get("order_product")
    if not product:
        return

    st.divider()
    st.markdown("## 🛒 Confirm Your Order")

    with st.container(border=True):
        st.markdown(f"**Product:** {product['name']}")
        if product.get("is_organic"):
            st.caption("🌿 Organic")
        st.markdown(f"**Price:** ₹{product['price']:.2f}")
        st.markdown(f"**Category:** {product.get('category', '—').title()}")
        st.divider()
        st.markdown("**Would you like to place this order?**")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, Place Order", type="primary",
                         use_container_width=True,
                         key=f"confirm_order{key_suffix}"):
                result = place_order(
                    product_id   = product["id"],
                    product_name = product["name"],
                    price        = product["price"],
                )
                if result["success"]:
                    st.session_state["show_order_dialog"] = False
                    st.session_state["order_product"]     = None
                    st.session_state["last_order"]        = result["order"]
                    st.session_state["order_success"]     = True
                    st.rerun()
                else:
                    st.error(result["message"])
        with c2:
            if st.button("❌ Cancel", use_container_width=True,
                         key=f"cancel_order{key_suffix}"):
                st.session_state["show_order_dialog"] = False
                st.session_state["order_product"]     = None
                st.rerun()


def render_order_success():
    if not st.session_state.get("order_success"):
        return
    order = st.session_state.get("last_order", {})
    st.success(
        f"✅ **Order Placed Successfully!**\n\n"
        f"- **Order #:** {order.get('id')}\n"
        f"- **Product:** {order.get('product_name')}\n"
        f"- **Price:** ₹{order.get('price', 0):.2f}\n"
        f"- **Placed at:** {order.get('ordered_at')}"
    )
    if st.button("Continue Shopping", type="primary", key="continue_shopping"):
        st.session_state["order_success"] = False
        st.session_state["last_order"]    = None
        st.rerun()
