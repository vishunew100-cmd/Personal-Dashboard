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
