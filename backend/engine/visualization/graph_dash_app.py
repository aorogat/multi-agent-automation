from dash import Dash, html, dcc, Input, Output, State, no_update
import dash_cytoscape as cyto
from flask import Flask, jsonify, request


# --------------------------------------------------
# Flask server (shared with Dash)
# --------------------------------------------------
server = Flask(__name__)

# Shared graph state
# `version` is the KEY for preventing unnecessary updates
GRAPH_DATA = {
    "version": 0,
    "elements": [
        {"data": {"id": "a", "label": "Agent A", "color": "#2563eb"}},
        {"data": {"id": "b", "label": "Agent B", "color": "#10b981"}},
        {"data": {"id": "c", "label": "Agent C", "color": "#7c3aed"}},
        {"data": {"source": "a", "target": "b"}},
        {"data": {"source": "b", "target": "c"}},
    ]
}


# --------------------------------------------------
# Flask API endpoints
# --------------------------------------------------
@server.route("/graph-data")
def get_graph():
    return jsonify(GRAPH_DATA)


@server.route("/update-graph", methods=["POST"])
def update_graph():
    new_elements = request.json.get("elements", [])

    # Update ONLY if graph actually changed
    GRAPH_DATA["elements"] = new_elements
    GRAPH_DATA["version"] += 1

    print(f"Update Graph data → version {GRAPH_DATA['version']}")
    return jsonify({"status": "ok", "version": GRAPH_DATA["version"]})


# --------------------------------------------------
# Helper: style nodes based on graph size (PRESERVE data.color)
# --------------------------------------------------
def style_elements_by_size(elements):
    """
    If number of nodes < 10:
        - big rectangle
        - label inside
    Else:
        - small circle
        - label outside

    IMPORTANT:
    - Coloring MUST come from the incoming graph data: data.color
    - So we DO NOT overwrite or derive colors here.
    """
    # Count nodes only (exclude edges)
    nodes = [e for e in elements if "source" not in e["data"]]
    small_graph = len(nodes) < 10

    styled_elements = []

    for e in elements:
        if "source" in e["data"]:
            # Edge → unchanged
            styled_elements.append(e)
        else:
            # Node → assign class only (do NOT modify color)
            e = e.copy()
            e["classes"] = "big-node" if small_graph else "small-node"

            # Safety fallback: if a node arrives without color, assign a default
            # (This does NOT override existing colors.)
            if "color" not in e.get("data", {}):
                e["data"] = dict(e.get("data", {}))
                e["data"]["color"] = "#64748b"

            styled_elements.append(e)

    return styled_elements


# --------------------------------------------------
# Dash app
# --------------------------------------------------
app = Dash(__name__, server=server, url_base_pathname="/dash/")

app.layout = html.Div([
    html.H4("", style={"textAlign": "center"}),

    # Polling trigger (cheap, but safe)
    dcc.Interval(
        id="graph-refresh",
        interval=1000,  # ms
        n_intervals=0
    ),

    # Store last-seen version (client-side)
    dcc.Store(id="graph-version", data=-1),

    cyto.Cytoscape(
        id="cytoscape-graph",
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px"},
        elements=style_elements_by_size(GRAPH_DATA["elements"]),
        stylesheet=[
            # ---------------------------------
            # BIG RECTANGLE (few nodes)
            # ---------------------------------
            {
                "selector": ".big-node",
                "style": {
                    "shape": "rectangle",
                    "width": "120px",
                    "height": "60px",

                    # ✅ COLOR COMES FROM GRAPH DATA
                    "background-color": "data(color)",

                    "label": "data(label)",
                    "color": "#ffffff",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "12px",
                    "text-wrap": "wrap",
                    "text-max-width": "100px",
                },
            },

            # ---------------------------------
            # SMALL CIRCLE (many nodes)
            # ---------------------------------
            {
                "selector": ".small-node",
                "style": {
                    "shape": "ellipse",
                    "width": "20px",
                    "height": "20px",

                    # ✅ COLOR COMES FROM GRAPH DATA
                    "background-color": "data(color)",

                    "label": "data(label)",
                    "color": "#111827",
                    "font-size": "9px",
                    "text-valign": "top",
                    "text-halign": "center",
                    "text-margin-y": "-10px",
                },
            },

            # ---------------------------------
            # EDGES
            # ---------------------------------
            {
                "selector": "edge",
                "style": {
                    "width": 1,
                    "line-color": "#9aa0a6",
                    "target-arrow-color": "#9aa0a6",
                    "target-arrow-shape": "triangle",
                    "curve-style": "bezier",
                },
            },
        ],
    )

])


# --------------------------------------------------
# Dash callback — UPDATE ONLY ON VERSION CHANGE
# --------------------------------------------------
@app.callback(
    Output("cytoscape-graph", "elements"),
    Output("graph-version", "data"),
    Input("graph-refresh", "n_intervals"),
    State("graph-version", "data"),
)
def refresh_graph(_, last_seen_version):
    current_version = GRAPH_DATA["version"]

    # No change → do NOT re-render → no layout jitter
    if current_version == last_seen_version:
        return no_update, last_seen_version

    # Graph changed → update once (with adaptive node styling)
    return style_elements_by_size(GRAPH_DATA["elements"]), current_version


# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    print("Starting Dash on port 8050...")
    app.run_server(
        host="0.0.0.0",
        port=8050,
        debug=False,
        use_reloader=False,
    )
