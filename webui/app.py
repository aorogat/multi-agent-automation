from nicegui import ui
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# ---------------------------------------------
# Load environment and init OpenAI client
# ---------------------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in .env")

client = OpenAI(api_key=api_key)

ui.colors(primary='#3b82f6', secondary='#8b5cf6', accent='#10b981')

conversation_history = []
thinking_indicator = None

BACKEND_URL = "http://localhost:8000/chat"


# -----------------------------------------------------
# UNIVERSAL SPEC RENDERER — WORKS WITH ANY SCHEMA SHAPE
# -----------------------------------------------------
def pretty_value(v):
    """Recursively pretty-render ANY JSON value."""
    if v is None:
        return ui.label("—").classes("text-slate-500 text-xs")
    
    # Primitive
    if isinstance(v, (str, int, float, bool)):
        return ui.label(str(v)).classes("text-xs text-slate-700")
    
    # List
    if isinstance(v, list):
        with ui.column().classes("gap-1"):
            for item in v:
                with ui.row().classes("gap-1 items-center"):
                    ui.icon("chevron_right", size="10px").classes("text-slate-400")
                    pretty_value(item)
        return
    
    # Dict (structured object)
    if isinstance(v, dict):
        with ui.column().classes("gap-1 bg-slate-50 rounded-md p-1 border border-slate-200"):
            for key, val in v.items():
                with ui.row().classes("gap-1 items-start"):
                    ui.label(f"{key}:").classes("text-[10px] font-bold text-slate-600")
                    pretty_value(val)
        return

    # fallback (should not happen)
    return ui.label(str(v)).classes("text-xs text-slate-700")


def render_spec_cards(spec: dict):
    """Render ANY spec into dynamic cards based on schema, no hardcoding."""
    spec_footer.clear()
    
    if not spec or all(v in [None, "", [], {}] for v in spec.values()):
        with spec_footer:
            with ui.row().classes('w-full h-full items-center justify-center'):
                ui.label('💡 No specification yet. Start chatting to build your system!').classes(
                    'text-slate-400 text-sm italic'
                )
        return

    with spec_footer:
        # Changed to grid layout for responsive cards
        with ui.element('div').classes("w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2"):

            for field, value in spec.items():

                # Skip empty values
                if value in [None, "", [], {}]:
                    continue

                # Card styling (dynamic)
                with ui.card().classes(
                    "w-full bg-white border border-slate-200 rounded-lg shadow-sm p-2"
                ):
                    # Title row
                    with ui.row().classes("items-center gap-1 mb-1"):
                        ui.icon("label", size="14px").classes("text-blue-600")
                        ui.label(field.title()).classes(
                            "text-[11px] font-bold text-slate-800"
                        )

                    # Render value dynamically
                    pretty_value(value)


# -----------------------------------------------------
# SEND MESSAGE HANDLER
# -----------------------------------------------------
async def send_message():
    global thinking_indicator

    text = user_input.value.strip()
    if not text:
        return
        
    # Clear input and show message immediately
    user_input.value = ''
    add_user_message(text)
    conversation_history.append({"role": "user", "content": text})

    add_thinking_message()

    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                BACKEND_URL,
                json={"message": text, "history": conversation_history}
            )
            data = response.json()

        # Remove thinking bubble
        if thinking_indicator:
            thinking_indicator.delete()
            thinking_indicator = None

        # Show assistant message
        reply = data["reply"]
        add_assistant_message(reply)
        conversation_history.append({"role": "assistant", "content": reply})

        # Update GRAPH
        graph_data = data.get("graph", [])
        if graph_data:
            ui.run_javascript(f"updateGraph({json.dumps(graph_data)})")

        # Update SPEC with fancy cards
        render_spec_cards(data.get("spec", {}))

    except Exception as e:
        if thinking_indicator:
            thinking_indicator.delete()
            thinking_indicator = None
        add_error_message(str(e))


# -----------------------------------------------------
# CHAT PANEL UI
# -----------------------------------------------------
with ui.column().classes(
    'absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-b from-slate-50 to-slate-100 shadow-2xl'
):

    # HEADER
    with ui.row().classes('w-full p-4 bg-white border-b border-slate-200 shadow-sm items-center gap-3'):
        ui.icon('smart_toy', size='28px').classes('text-blue-600')
        with ui.column().classes('gap-0'):
            ui.label('MAS Automation').classes('text-xl font-bold text-slate-800')
            ui.label('Multi-Agent System Designer').classes('text-xs text-slate-500')

    # CHAT AREA
    chat_scroll = ui.scroll_area().classes('flex-grow px-3 py-3')
    with chat_scroll:
        chat_container = ui.column().classes('w-full gap-3')

    # INPUT AREA
    with ui.column().classes('w-full p-3 bg-white border-t border-slate-200'):
        with ui.row().classes('w-full gap-2 items-end'):
            user_input = ui.input(
                placeholder='Describe your multi-agent system...'
            ).props('outlined dense').classes('flex-grow')

            send_button = ui.button(icon='send').props('flat round').classes(
                'bg-blue-600 text-white hover:bg-blue-700'
            )


    # ---------------------------------------------
    # MESSAGE HELPERS
    # ---------------------------------------------
    def add_user_message(text: str):
        with chat_container:
            with ui.row().classes('w-full justify-end items-start'):
                with ui.card().classes(
                    'max-w-[70%] bg-blue-600 text-white p-2 rounded-lg shadow text-xs'
                ):
                    ui.label(text).classes('leading-snug')
        chat_scroll.scroll_to(pixels=999999)

    def add_thinking_message():
        global thinking_indicator
        with chat_container:
            thinking_indicator = ui.row().classes('w-full justify-start items-start gap-2')
            with thinking_indicator:
                ui.icon('psychology', size='18px').classes('text-purple-600 mt-1')
                with ui.card().classes(
                    'max-w-[70%] bg-purple-100 border border-purple-200 shadow-sm p-2 rounded-lg text-xs'
                ):
                    with ui.row().classes('items-center gap-2'):
                        ui.spinner(size='xs', color='purple')
                        ui.label('Analyzing...').classes('text-purple-800')
        chat_scroll.scroll_to(pixels=999999)

    def add_assistant_message(text: str):
        safe_text = text.replace("<", "&lt;").replace(">", "&gt;")
        with chat_container:
            with ui.row().classes('w-full justify-start items-start gap-2'):
                ui.icon('smart_toy', size='18px').classes('text-green-600 mt-1')
                with ui.card().classes(
                    'max-w-[70%] bg-white border border-slate-200 shadow p-2 rounded-lg text-xs'
                ):
                    ui.markdown(safe_text).classes("text-xs leading-tight")
        chat_scroll.scroll_to(pixels=999999)

    def add_error_message(text: str):
        with chat_container:
            with ui.row().classes('w-full justify-start items-start gap-2'):
                ui.icon('error_outline', size='18px').classes('text-red-600 mt-1')
                with ui.card().classes(
                    'max-w-[70%] bg-red-50 border border-red-200 shadow-sm p-2 rounded-lg text-xs'
                ):
                    ui.label(f"Error: {text}").classes('text-red-700')
        chat_scroll.scroll_to(pixels=999999)


    # ---------------------------------------------
    # BIND EVENT HANDLERS
    # ---------------------------------------------
    user_input.on('keydown.enter', send_message)
    send_button.on('click', send_message)


# ---------------------------------------------
# VISUALIZATION PANEL (GRAPH + SPEC FOOTER)
# ---------------------------------------------
with ui.column().classes('absolute left-0 top-0 bottom-0 w-2/3 bg-slate-50 p-4'):
    
    # Header
    with ui.row().classes('w-full mb-3 items-center gap-2'):
        ui.icon('account_tree', size='28px').classes('text-blue-600')
        ui.label('System Visualization').classes('text-xl font-bold text-slate-800')

    # GRAPH AREA (takes most space)
    graph_container = ui.element('div').classes('w-full bg-white border-2 border-slate-200 rounded-xl shadow-lg').style(
        'height: calc(100% - 230px);'
    )
    
    with graph_container:
        ui.html(
            '''
            <div id="cy" style="width:100%; height:100%; border-radius:10px;"></div>
            ''',
            sanitize=False,
        )

    # SPEC FOOTER (fancy cards section)
    with ui.column().classes('w-full mt-3 bg-white border border-slate-200 rounded-xl shadow-lg p-4').style(
        'height: 280px; overflow-y: auto;'
    ):
        with ui.row().classes('w-full items-center gap-2 mb-2 pb-2 border-b border-slate-200'):
            ui.icon('description', size='22px').classes('text-slate-600')
            ui.label('System Specification').classes('text-base font-bold text-slate-800')
        
        spec_footer = ui.column().classes('w-full')
        
        # Initial state
        with spec_footer:
            with ui.row().classes('w-full h-full items-center justify-center'):
                ui.label('💡 No specification yet. Start chatting to build your system!').classes(
                    'text-slate-400 text-sm italic'
                )


# JS for Cytoscape
ui.add_body_html("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
<script>
    var cy = cytoscape({
        container: document.getElementById('cy'),
        elements: [],
        style: [
            { selector: 'node', style: {
                'background-color': '#3b82f6',
                'label': 'data(label)',
                'color': '#fff',
                'font-size': '11px',
                'font-weight': 'bold',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': '60px',
                'height': '60px',
                'border-width': '3px',
                'border-color': '#1e40af',
                'text-wrap': 'wrap',
                'text-max-width': '50px'
            }},
            { selector: 'edge', style: {
                'width': 2,
                'line-color': '#94a3b8',
                'target-arrow-shape': 'triangle',
                'target-arrow-color': '#64748b',
                'curve-style': 'bezier',
                'arrow-scale': 1.2
            }}
        ],
        layout: { name: 'cose', animate: true, animationDuration: 500 }
    });

    window.updateGraph = function(data) {
        cy.json({ elements: data });
        cy.layout({
            name: 'cose',
            animate: true,
            animationDuration: 500,
            padding: 40
        }).run();
    };
</script>
""")

ui.run(host='0.0.0.0', port=8080)