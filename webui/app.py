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
# FORMAT SPEC INTO FANCY CARDS
# -----------------------------------------------------
def render_spec_cards(spec: dict):
    """Render spec as fancy info cards."""
    spec_footer.clear()
    
    if not spec or all(not v for v in spec.values()):
        with spec_footer:
            with ui.row().classes('w-full h-full items-center justify-center'):
                ui.label('💡 No specification yet. Start chatting to build your system!').classes(
                    'text-slate-400 text-sm italic'
                )
        return
    
    with spec_footer:
        with ui.row().classes('w-full gap-2 items-stretch'):
            # Task Card
            if spec.get('task'):
                with ui.card().classes('flex-1 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 shadow-sm p-2'):
                    with ui.row().classes('items-center gap-1 mb-1'):
                        ui.icon('task_alt', size='16px').classes('text-blue-600')
                        ui.label('Task').classes('text-xs font-bold text-blue-900')
                    ui.label(spec['task']).classes('text-xs text-slate-700 leading-tight')
            
            # Goal Card
            if spec.get('goal'):
                with ui.card().classes('flex-1 bg-gradient-to-br from-green-50 to-green-100 border-green-200 shadow-sm p-2'):
                    with ui.row().classes('items-center gap-1 mb-1'):
                        ui.icon('flag', size='16px').classes('text-green-600')
                        ui.label('Goal').classes('text-xs font-bold text-green-900')
                    ui.label(spec['goal']).classes('text-xs text-slate-700 leading-tight')
            
            # Agents Card
            if spec.get('agents'):
                with ui.card().classes('flex-1 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200 shadow-sm p-2'):
                    with ui.row().classes('items-center gap-1 mb-1'):
                        ui.icon('groups', size='16px').classes('text-purple-600')
                        ui.label('Agents').classes('text-xs font-bold text-purple-900')
                    if isinstance(spec['agents'], list):
                        for agent in spec['agents']:
                            with ui.row().classes('gap-1 items-center'):
                                ui.icon('android', size='12px').classes('text-purple-500')
                                ui.label(agent).classes('text-xs text-slate-700')
                    else:
                        ui.label(str(spec['agents'])).classes('text-xs text-slate-700')
            
            # Tools Card
            if spec.get('tools'):
                with ui.card().classes('flex-1 bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200 shadow-sm p-2'):
                    with ui.row().classes('items-center gap-1 mb-1'):
                        ui.icon('build', size='16px').classes('text-amber-600')
                        ui.label('Tools').classes('text-xs font-bold text-amber-900')
                    if isinstance(spec['tools'], list):
                        for tool in spec['tools']:
                            with ui.row().classes('gap-1 items-center'):
                                ui.icon('construction', size='12px').classes('text-amber-500')
                                ui.label(tool).classes('text-xs text-slate-700')
                    else:
                        ui.label(str(spec['tools'])).classes('text-xs text-slate-700')
        
        # Second row for additional properties
        if spec.get('communication') or spec.get('topology') or spec.get('constraints'):
            with ui.row().classes('w-full gap-3 items-start mt-3'):
                # Communication
                if spec.get('communication'):
                    with ui.card().classes('flex-1 bg-gradient-to-br from-cyan-50 to-cyan-100 border-cyan-200 shadow-sm'):
                        with ui.row().classes('items-center gap-2 mb-1'):
                            ui.icon('forum', size='18px').classes('text-cyan-600')
                            ui.label('Communication').classes('text-xs font-bold text-cyan-900')
                        ui.label(str(spec['communication'])).classes('text-xs text-slate-700 leading-snug')
                
                # Topology
                if spec.get('topology'):
                    with ui.card().classes('flex-1 bg-gradient-to-br from-pink-50 to-pink-100 border-pink-200 shadow-sm'):
                        with ui.row().classes('items-center gap-2 mb-1'):
                            ui.icon('hub', size='18px').classes('text-pink-600')
                            ui.label('Topology').classes('text-xs font-bold text-pink-900')
                        ui.label(str(spec['topology'])).classes('text-xs text-slate-700 leading-snug')
                
                # Constraints
                if spec.get('constraints'):
                    with ui.card().classes('flex-1 bg-gradient-to-br from-red-50 to-red-100 border-red-200 shadow-sm'):
                        with ui.row().classes('items-center gap-2 mb-1'):
                            ui.icon('gpp_maybe', size='18px').classes('text-red-600')
                            ui.label('Constraints').classes('text-xs font-bold text-red-900')
                        ui.label(str(spec['constraints'])).classes('text-xs text-slate-700 leading-snug')


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