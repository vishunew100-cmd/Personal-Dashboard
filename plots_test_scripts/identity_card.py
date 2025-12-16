import streamlit as st
import json
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from pyvis.network import Network


st.set_page_config(layout="wide", page_title="Financial & Background Dashboard")
st.title("📊 Financial & Background Dashboard")

# -----------------------------------------------------
# LOAD JSON
# -----------------------------------------------------
uploaded_file = st.file_uploader("Upload JSON Report", type=["json"])

if not uploaded_file:
    st.info("Upload a JSON file to generate the dashboard.")
    st.stop()

data = json.load(uploaded_file)


# -----------------------------------------------------
# IDENTITY CARD 
# -----------------------------------------------------
identity = data["identity"]
usernames = data["username"]
criminal = data.get("criminal_history", {})
contacts = data["contacts"]

identity_card_html = f"""
<div style="
    background: linear-gradient(145deg, #1c1c1c, #242424);
    border-radius: 18px;
    padding: 25px;
    border: 1px solid #333;
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
">

    <!-- NAME (CENTERED) -->
    <h2 style="text-align:center; font-size:32px; margin-top:0;">
        🧍 {identity['name']}
    </h2>

    <div style="display:flex; gap:30px; justify-content:space-between;">

        <!-- LEFT COLUMN -->
        <div style="width:48%; font-size:16px; line-height:1.7;">

            <p><strong>🪪 SSN:</strong> {identity['ssn']}</p>

            <p><strong>📅 DOB | Age:</strong> {identity['dob']} | {identity['age']}</p>

            <p><strong>📍 Address:</strong><br>{identity['current_address']}</p>

            <p><strong>🗂 Aliases:</strong><br>{", ".join(identity['aliases'])}</p>

            <p><strong>🎫 DL:</strong> {identity.get('DL', 'NA')}</p>
            <p><strong>👩 MMN:</strong> {identity.get('MMN', 'NA')}</p>
        </div>

        <!-- RIGHT COLUMN -->
        <div style="width:48%;">

            <!-- USERNAMES -->
            <details style="margin-bottom:12px; background:#2a2a2a; padding:10px; border-radius:10px;">
                <summary style="cursor:pointer; font-size:18px;">👤 Usernames</summary>
                <div style="margin-top:10px;">
                    {"<br>".join(["• " + u for u in usernames])}
                </div>
            </details>

            <!-- CRIMINAL HISTORY -->
            <details style="margin-bottom:12px; background:#2a2a2a; padding:10px; border-radius:10px;">
                <summary style="cursor:pointer; font-size:18px;">⚖️ Criminal History</summary>
                <div style="margin-top:10px;">
                    <p><strong>Case #:</strong> {", ".join(criminal.get("cases", []))}</p>
                    <p><strong>Crime:</strong> {criminal.get("crime", "NA")}</p>

                </div>
            </details>

            <!-- CONTACTS -->
            <details style="background:#2a2a2a; padding:10px; border-radius:10px;">
                <summary style="cursor:pointer; font-size:18px;">☎️ Contacts</summary>

                <div style="display:flex; gap:20px; margin-top:10px;">

                    <!-- Phones -->
                    <div style="width:50%;">
                        <strong>📞 Phones</strong><br>
                        {"<br>".join(["• " + p for p in contacts["phones"]])}
                    </div>

                    <!-- Emails -->
                    <div style="width:50%;">
                        <strong>📧 Emails</strong><br>
                        {"<br>".join(["• " + e for e in contacts["emails"]])}
                    </div>

                </div>
            </details>

        </div>

    </div>

</div>
"""

# Render inside Streamlit
components.html(identity_card_html, height=550, scrolling=True)



# -----------------------------------------------------
# ADVANCED ACCOUNT PIE CHART VISUALIZATION
# -----------------------------------------------------
open_acc = pd.DataFrame(data["open_accounts"])
closed_acc = pd.DataFrame(data["closed_accounts"])


open_acc["creditor"] = open_acc["creditor"].fillna("Unknown Creditor")
closed_acc["creditor"] = closed_acc["creditor"].fillna("Unknown Creditor")

# ------------------------------------------------------------
# 1️⃣ PIE — Total Number of OPEN Accounts
# ------------------------------------------------------------

# Build hover text grouped by creditor
def build_open_group_hover(df):
    groups = {}
    for creditor, sub in df.groupby("creditor"):
        text = f"<b>{creditor}</b><br>"
        for _, row in sub.iterrows():
            text += (
                f"Opened: {row['opened']} |" +"<br>" +
                f"current_balance: ${row['current_balance']} | " +"<br>" +
                f"credit_limit: ${row['credit_limit']} | " +"<br>" +
                f"last_payment: {row.get('last_payment','-')} | " +"<br>" +
                f"Updated: {row.get('updated','-')} | " +"<br>" +
                f"past_due: {row.get('past_due','-')} | " +"<br>" +
                f"high_balance: ${row.get('high_balance','-')} | " +"<br>" +
                f"Status: {row['status']}|<br>" +"<br>" 
            )
        groups[creditor] = text
    return groups

hover_map = build_open_group_hover(open_acc)

# grouped df for the pie
open_count = (
    open_acc.groupby("creditor")
    .size()
    .reset_index(name="Count")
)

# attach hover text to grouped dataframe
open_count["hover_text"] = open_count["creditor"].map(hover_map)

fig_open_count = px.pie(
    open_count,
    names="creditor",
    values="Count"
)

fig_open_count.update_traces(
    customdata=open_count[["hover_text"]],
    hovertemplate="%{customdata[0]}<extra></extra>",
    textinfo="value",
    pull=[0.05] * len(open_count)
)

# ------------------------------------------------------------
# 2️⃣ PIE — Number of CLOSED Accounts by Creditor
# ------------------------------------------------------------
# Build grouped hover text
def build_closed_group_hover(df):
    groups = {}
    for creditor, sub in df.groupby("creditor"):
        text = f"<b>{creditor}</b><br>"
        for _, row in sub.iterrows():
            text += (
                f"Opened: {row.get('opened','-')} | "+"<br>" +
                f"Closed: {row.get('closed','-')} | "+"<br>" +
                f"Type: {row.get('type', row.get('loan type','-'))} | "+"<br>" +
                f"Balance: ${row.get('balance','-')} | "+"<br>" +
                f"credit_limit: ${row.get('credit_limit','-')} | "+"<br>" +
                f"Status: {row.get('paymant status','-')} | "+"<br>" +
                f"Remarks: {row.get('remarks','-')}|<br>"+"<br>" 
            )
        groups[creditor] = text
    return groups

closed_hover_map = build_closed_group_hover(closed_acc)

# Group for pie
closed_count = (
    closed_acc.groupby("creditor")
    .size()
    .reset_index(name="Count")
)

# Attach grouped hover text
closed_count["hover_text"] = closed_count["creditor"].map(closed_hover_map)

# Build pie chart
fig_closed_count = px.pie(
    closed_count,
    names="creditor",
    values="Count"
)

fig_closed_count.update_traces(
    customdata=closed_count[["hover_text"]],
    hovertemplate="%{customdata[0]}<extra></extra>",
    textinfo="value",
    pull=[0.05] * len(closed_count)
)

# ------------------------------------------------------------
# 3️⃣ PIE — Total credit_limit (OPEN Accounts) by Creditor
# ------------------------------------------------------------
credit_limit_sum = (
    open_acc.groupby("creditor")["credit_limit"]
    .sum()
    .reset_index(name="credit_limit")
)

fig_credit_limit = px.pie(
    credit_limit_sum,
    names="creditor",
    values="credit_limit"
)

fig_credit_limit.update_traces(
    textinfo="value",
    pull=[0.05] * len(credit_limit_sum),
)

# ------------------------------------------------------------
# 4️⃣ PIE — Total Balance (OPEN Accounts) by Creditor
# ------------------------------------------------------------
balance_sum = (
    open_acc.groupby("creditor")["current_balance"]
    .sum()
    .reset_index(name="Balance")
)

fig_balance_sum = px.pie(
    balance_sum,
    names="creditor",
    values="Balance"
)

fig_balance_sum.update_traces(
    textinfo="value",
    pull=[0.05] * len(balance_sum),
)

# ------------------------------------------------------------
# DISPLAY CHARTS
# ------------------------------------------------------------
k = data["kpis"]
with st.expander("💳 Account Summary KPIs", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total OPEN Accounts", k["open_accounts"])
    c1.plotly_chart(fig_open_count, use_container_width=True)
    c2.metric("Total CLOSED Accounts", k["closed_accounts"])
    c2.plotly_chart(fig_closed_count, use_container_width=True)
    c3.metric("Total credit_limit", f"${k['total_credit_limit']:,}")
    c3.plotly_chart(fig_credit_limit, use_container_width=True)
    c4.metric("Total BALANCE", f"${k['current_total_balance']:,}")
    c4.plotly_chart(fig_balance_sum, use_container_width=True)


# -----------------------------------------------------
# JOBS + EDUCATION
# -----------------------------------------------------
colA, colB = st.columns(2)

with colA:
    with st.expander("💼 Employment History", expanded=True):
        st.dataframe(pd.DataFrame(data["jobs"]))

with colB:
    with st.expander("🎓 Education History", expanded=True):
        st.dataframe(pd.DataFrame(data["education"]))


# -----------------------------------------------------
# ADDRESS TIMELINE (FIXED DATE CLEANING)
# -----------------------------------------------------
st.subheader("📍 Address Timeline")

df_addr = pd.DataFrame(data["addresses_timeline"])

def clean_date(x):
    if x in ["-", "NA", "", None]:
        return None
    if isinstance(x, str) and x.lower().startswith("present"):
        return pd.Timestamp.today()
    try:
        if len(x) == 4 and x.isdigit():  
            return pd.to_datetime(f"{x}-01-01")
        return pd.to_datetime(x)
    except:
        return None

df_addr["start_dt"] = df_addr["started"].apply(clean_date)
df_addr["end_dt"] = df_addr["left"].apply(clean_date)

df_clean = df_addr.dropna(subset=["start_dt", "end_dt"])

if df_clean.empty:
    st.info("No valid timeline dates available for plotting.")
else:
    fig_addr = px.timeline(
        df_clean,
        x_start="start_dt",
        x_end="end_dt",
        y="place",
        color="remarks",
        title="Address History Timeline"
    )
    st.plotly_chart(fig_addr, use_container_width=True)

# -----------------------------------------------------
# 🌳 HIERARCHICAL RELATIONSHIP NETWORK GRAPH (Improved)
# -----------------------------------------------------
st.subheader("🌳 Hierarchical Relationship Network Graph")

net = Network(
    height="650px",
    width="100%",
    bgcolor="#222",
    font_color="white",
    directed=False
)

# =====================================================
# ROOT NODE
# =====================================================
person_name = identity["name"]
net.add_node(
    "ROOT",
    label=person_name,
    title=f"<b>Primary Person:</b> {person_name}",
    color="#3b82f6",
    size=40,
    font={"size": 24}
)

# =====================================================
# SECOND-LAYER: GROUP NODES
# =====================================================
groups = [
    ("FAMILY", "Family", "#16a34a"),
    ("CORE_FAMILY", "Core Family", "#22c55e"),
    ("EXTENDED_FAMILY", "Extended Family", "#86efac"),
    ("ASSOCIATES", "Associates", "#fbbf24"),
    ("NEIGHBORS", "Neighbors", "#f87171"),
]

for group_id, label, color in groups:
    net.add_node(group_id, label=label, color=color, shape="box", size=30)
    
# Attach hierarchy
net.add_edge("ROOT", "FAMILY")
net.add_edge("FAMILY", "CORE_FAMILY")
net.add_edge("FAMILY", "EXTENDED_FAMILY")
net.add_edge("ROOT", "ASSOCIATES")
net.add_edge("ROOT", "NEIGHBORS")

# =====================================================
# THIRD-LAYER — CORE FAMILY MEMBERS
# =====================================================
for f in data["family"]["core"]:
    node_id = f"{f['name']}_core"

    hover = (
        f"<b>Name:</b> {f['name']}<br>"
        f"<b>Relation:</b> {f['relation']}<br>"
        f"<b>Age:</b> {f['age']}"
    )

    net.add_node(
        node_id,
        label=f"{f['relation']}",
        title=hover,
        color="#4ade80",
        font={"face": "Arial", "size": 12, "multi": False},
        width_constraint={"maximum": 200}
    )
    net.add_edge("CORE_FAMILY", node_id)

# =====================================================
# EXTENDED FAMILY MEMBERS
# =====================================================
for f in data["family"]["extended"]:
    node_id = f"{f['name']}_extended"

    hover = (
        f"<b>Name:</b> {f['name']}<br>"
        f"<b>Relation:</b> {f['relation']}<br>"
        f"<b>Age:</b> {f['age']}"
    )

    net.add_node(
        node_id,
        label=f"{f['relation']}",
        title=hover,
        color="#86efac",
        font={"face": "Arial", "size": 12, "multi": False},
        width_constraint={"maximum": 200}
    )
    net.add_edge("EXTENDED_FAMILY", node_id)

# =====================================================
# ASSOCIATES
# =====================================================
for a in data["associates"]:
    node_id = f"{a['name']}_associate"

    hover = (
        f"<b>Name:</b> {a['name']}<br>"
        f"<b>Relation:</b> Associate<br>"
        f"<b>Age:</b> {a.get('age','NA')}<br>"
        f"<b>Location:</b> {a.get('location','NA')}"
    )

    net.add_node(
    node_id,
    label=f"{a['name']}",
    title=hover,
    color="#fde047",
    font={"face": "Arial", "size": 12, "multi": False},
    width_constraint={"maximum": 200}
    )

    net.add_edge("ASSOCIATES", node_id)

# =====================================================
# NEIGHBORS
# =====================================================
for n in data["neighbors"]:
    node_id = f"{n['name']}_neighbor"

    hover = (
        f"<b>Name:</b> {n['name']}<br>"
        f"<b>Relation:</b> Neighbor<br>"
        f"<b>Age:</b> {n.get('age','NA')}<br>"
        f"<b>Address:</b> {n.get('address','NA')}"
    )

    net.add_node(
        node_id,
        label=f"{n['name']}",
        title=hover,
        color="#fca5a5",
        font={"face": "Arial", "size": 12, "multi": False},
        width_constraint={"maximum": 200}
    )
    net.add_edge("NEIGHBORS", node_id)

# =====================================================
# HIERARCHICAL TREE LAYOUT OPTIONS (VALID JSON)
# =====================================================
net.set_options("""
{
  "layout": {
    "hierarchical": {
      "enabled": true,
      "levelSeparation": 180,
      "nodeSpacing": 400,
      "direction": "UD",
      "sortMethod": "directed"
    }
  },
  "nodes": {
    "shape": "dot",
    "size": 18,
    "font": { "color": "white", "size": 16, "face": "Arial"}
  },
  "edges": {
    "color": "#999",
    "smooth": true
  }
}
""")

# Render graph
net.save_graph("network_tree.html")
components.html(open("network_tree.html").read(), height=650)
