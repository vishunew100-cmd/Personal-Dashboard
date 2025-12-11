import streamlit as st
from streamlit.components.v1 import html
from app.utils.data_loader import load_profile
from app.utils.graph_utils import build_pyvis_html

st.title("Network Graph")

txt = st.text_area("Paste JSON or click Load Sample")

if st.button("Load Sample"):
    data = load_profile()
else:
    if not txt:
        st.stop()
    data = load_profile(txt)

graph_html = build_pyvis_html(data["network"])
html(graph_html, height=650, scrolling=True)
