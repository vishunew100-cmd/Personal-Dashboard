# app/utils/graph_utils.py
from pyvis.network import Network
import tempfile

def build_pyvis_html(network_data, height="600px"):
    net = Network(height=height, width="100%", bgcolor="#ffffff", font_color="#222")
    net.force_atlas_2based()
    for a in network_data.get("addresses", []):
        net.add_node(a["id"], label=a.get("label",""), shape="dot", color="#1f8f4a", size=28)
    for p in network_data.get("people", []):
        net.add_node(p["id"], label=p.get("label",""), shape="icon", icon={"face":"FontAwesome","code":"\uf007"}, color="#e6f2ff", size=18)
    for e in network_data.get("edges", []):
        net.add_edge(e["from"], e["to"], width=1, color="#888")
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        net.show(tmp.name)
        return open(tmp.name, encoding="utf-8").read()
