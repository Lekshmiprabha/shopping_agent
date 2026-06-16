"""
ui/order_history_tab.py
────────────────────────
Streamlit component: displays all past orders from the orders table.
"""
import pandas as pd
import streamlit as st
from agents.checkout_agent import get_all_orders


def render():
    st.markdown("### 📋 Order History")

    orders = get_all_orders()

    if not orders:
        st.info("No orders placed yet. Search for a product and place your first order!")
        return

    df = pd.DataFrame(orders)
    df = df.rename(columns={
        "id":           "Order #",
        "product_name": "Product",
        "price":        "Price (₹)",
        "ordered_at":   "Placed At",
    })
    df = df.drop(columns=["product_id"], errors="ignore")
    df["Price (₹)"] = df["Price (₹)"].apply(lambda x: f"₹{x:.2f}")

    st.markdown(f"**Total orders: {len(orders)}**")
    st.dataframe(df, use_container_width=True, hide_index=True)
