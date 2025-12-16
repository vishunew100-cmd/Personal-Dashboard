# app/utils/plot_utils.py
import plotly.express as px
import pandas as pd

def balance_by_creditor(accounts):
    df = pd.DataFrame(accounts)
    if df.empty: return None
    fig = px.bar(df, x="creditor", y="balance", title="Balance by Creditor")
    return fig

def account_type_pie(accounts):
    df = pd.DataFrame(accounts)
    if "type" not in df.columns: return None
    fig = px.pie(df, names="type", title="Account Types")
    return fig

# -------------------------------------------
# Identity Card Renderer (HTML-based)
# -------------------------------------------

def render_identity_card(identity: dict) -> str:
    """
    Returns an HTML block styled as an identity card.
    Streamlit will render it via st.markdown(..., unsafe_allow_html=True)
    """

    name = identity.get("name", "N/A")
    dob = identity.get("dob", "N/A")
    age = identity.get("age", "N/A")
    current_address = identity.get("current_address", "N/A")
    aliases = identity.get("aliases", [])
    ssn = identity.get("ssn_masked", "N/A")

    alias_text = ", ".join(aliases) if aliases else "None"

    html = f"""
    <div style="
        background: #1e1e1e;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333;
        color: white;
        width: 100%;
        margin-bottom: 20px;
    ">
        <h2 style="margin-top: 0; margin-bottom: 10px;">🧍 Identity</h2>

        <p><strong>Name:</strong> {name}</p>
        <p><strong>Date of Birth:</strong> {dob}</p>
        <p><strong>Age:</strong> {age}</p>
        <p><strong>Current Address:</strong> {current_address}</p>
        <p><strong>Aliases:</strong> {alias_text}</p>
        <p><strong>SSN (masked):</strong> {ssn}</p>
    </div>
    """

    return html
