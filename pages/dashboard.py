# app/pages/dashboard.py
import streamlit as st
from app.utils.data_loader import load_profile
from app.utils.plot_utils import (
    balance_by_creditor,
    account_type_pie,
    render_identity_card
)

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Dashboard")
data_text = st.text_area("Paste parsed JSON", value="")
if st.button("Load sample"):
    data = load_profile("app/data/sample_profile.json")
else:
    if not data_text:
        st.info("Paste parsed JSON or click Load sample")
        st.stop()
    data = load_profile(data_text)

# -------------------------------
# Identity Card
# -------------------------------
st.markdown("### Identity Information")
identity_html = render_identity_card(data["identity"])
st.markdown(identity_html, unsafe_allow_html=True)

# -------------------------------
#  KPIs
# -------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Open Accounts", data["kpis"].get("open_accounts", 0))
k2.metric("Closed Accounts", data["kpis"].get("closed_accounts", 0))
k3.metric("Total Limit", f"${data['kpis'].get('total_credit_limit', 0):,}")
k4.metric("Total Balance", f"${data['kpis'].get('current_total_balance', 0):,}")

# -------------------------------
#  Plots
# -------------------------------
plots = {}
if data.get("accounts"):
    plots["balance"] = balance_by_creditor(data["accounts"])
    plots["types"] = account_type_pie(data["accounts"])
    plots["personal_info"] = data.get("personal_info", {})


if plots.get("balance"): 
    st.plotly_chart(plots["balance"], use_container_width=True)
if plots.get("types"): 
    st.plotly_chart(plots["types"], use_container_width=True)


