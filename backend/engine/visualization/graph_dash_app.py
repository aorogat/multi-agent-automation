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
        {"data": {"id": "a", "label": "Agent A"}},
        {"data": {"id": "b", "label": "Agent B"}},
        {"data": {"id": "c", "label": "Agent C"}},
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
# Dash app
# --------------------------------------------------
app = Dash(__name__, server=server, url_base_pathname="/dash/")

app.layout = html.Div([
    html.H4("Current System Graph", style={"textAlign": "center"}),

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
        elements=GRAPH_DATA["elements"],
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

    # Graph changed → update once
    return GRAPH_DATA["elements"], current_version


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
