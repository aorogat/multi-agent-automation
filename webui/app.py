from nicegui import ui
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx
import time
import traceback


# ---------------------------------------------------------
# LOAD LLM
# ---------------------------------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in .env")

client = OpenAI(api_key=api_key)

ui.colors(primary='#3b82f6', secondary='#8b5cf6', accent='#10b981')

conversation_history = []
thinking_indicator = None
dash_iframe = None

BACKEND_URL = "http://localhost:8000/chat"
GUIDANCE_URL = "http://localhost:8000/generate-guidance"
DOWNLOAD_BASE_URL = "http://localhost:8000/download-guidance"


# ---------------------------------------------------------
# SPEC RENDERING HELPERS
# ---------------------------------------------------------
def reload_graph():
    """
    Force reload Dash iframe by updating src with cache buster
    Uses JavaScript to update src directly (no DOM replacement = no flicker)
    """
    if not dash_iframe:
        return

    # Use JavaScript to update iframe src directly (preserves zoom/pan state better)
    ui.timer(
        0.05,  # 50ms delay to ensure DOM is ready
        lambda: dash_iframe.run_javascript(
            f"""
            const iframe = document.getElementById("dash-frame");
            if (iframe) {{
                iframe.src = "http://localhost:8050/dash?ts={int(time.time())}";
            }}
            """
        ),
        once=True,
    )


def pretty_value(v):
    if v is None:
        return ui.label("—").classes("text-slate-500 text-xs")

    if isinstance(v, (str, int, float, bool)):
        return ui.label(str(v)).classes("text-xs text-slate-700")

    if isinstance(v, list):
        with ui.column().classes("gap-1"):
            for item in v:
                with ui.row().classes("gap-1 items-center"):
                    ui.icon("chevron_right", size="10px").classes("text-slate-400")
                    pretty_value(item)
        return

    if isinstance(v, dict):
        with ui.column().classes("gap-1 bg-slate-50 rounded-md p-1 border border-slate-200"):
            for key, val in v.items():
                with ui.row().classes("gap-1 items-start"):
                    ui.label(f"{key}:").classes("text-[10px] font-bold text-slate-600")
                    pretty_value(val)
        return

    return ui.label(str(v)).classes("text-xs text-slate-700")


def render_spec_cards(spec: dict):
    spec_footer.clear()

    if not spec or all(v in [None, "", [], {}] for v in spec.values()):
        with spec_footer:
            with ui.row().classes('w-full h-full items-center justify-center'):
                ui.label('💡 No specification yet. Start chatting to build your system!').classes(
                    'text-slate-400 text-sm italic'
                )
        return

    with spec_footer:
        with ui.element('div').classes("w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2"):
            for field, value in spec.items():

                if value in [None, "", [], {}]:
                    continue

                with ui.card().classes(
                    "w-full bg-white border border-slate-200 rounded-lg shadow-sm p-2"
                ):
                    with ui.row().classes("items-center gap-1 mb-1"):
                        ui.icon("label", size="14px").classes("text-blue-600")
                        ui.label(field.title()).classes("text-[11px] font-bold text-slate-800")

                    pretty_value(value)


# ---------------------------------------------------------
# SEND MESSAGE
# ---------------------------------------------------------
async def send_message():
    global thinking_indicator

    text = user_input.value.strip()
    if not text:
        return

    user_input.value = ''
    add_user_message(text)
    conversation_history.append({"role": "user", "content": text})
    add_thinking_message()

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client_http:
            response = await client_http.post(
                BACKEND_URL,
                json={"message": text, "history": conversation_history}
            )
            data = response.json()

        if thinking_indicator:
            thinking_indicator.delete()
            thinking_indicator = None

        reply = data["reply"]
        add_assistant_message(reply)
        conversation_history.append({"role": "assistant", "content": reply})

        # ✅ Update spec
        render_spec_cards(data.get("spec", {}))

        # ✅ Reload graph ONLY if backend explicitly says it changed
        if data.get("graph_updated"):
            reload_graph()

    except Exception as e:
        if thinking_indicator:
            thinking_indicator.delete()
            thinking_indicator = None
        add_error_message(traceback.format_exc())


# ---------------------------------------------------------
# CHAT UI
# ---------------------------------------------------------
with ui.column().classes(
    'absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-b from-slate-50 to-slate-100 shadow-2xl'
):

    with ui.row().classes('w-full p-4 bg-white border-b border-slate-200 shadow-sm items-center gap-3'):
        ui.icon('smart_toy', size='28px').classes('text-blue-600')
        with ui.column().classes('gap-0 flex-grow'):
            ui.label('MAS Automation').classes('text-xl font-bold text-slate-800')
            ui.label('Multi-Agent System Designer').classes('text-xs text-slate-500')
        
        # Generate Guidance Button
        guidance_button = ui.button(
            'Generate Guidance Report',
            icon='description'
        ).props('outlined').classes('bg-green-600 text-white hover:bg-green-700')

    chat_scroll = ui.scroll_area().classes('flex-grow px-3 py-3')
    with chat_scroll:
        chat_container = ui.column().classes('w-full gap-3')

    with ui.column().classes('w-full p-3 bg-white border-t border-slate-200'):
        with ui.row().classes('w-full gap-2 items-end'):

            user_input = ui.input(
                placeholder='Describe your multi-agent system...'
            ).props('outlined dense').classes('flex-grow')

            send_button = ui.button(icon='send').props(
                'flat round'
            ).classes('bg-blue-600 text-white hover:bg-blue-700')


    def add_user_message(t):
        with chat_container:
            with ui.row().classes('w-full justify-end items-start'):
                with ui.card().classes(
                    'max-w-[70%] bg-blue-600 text-white p-2 rounded-lg shadow text-xs'
                ):
                    ui.label(t).classes('leading-snug')
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

    def add_assistant_message(t):
        safe = t.replace("<", "&lt;").replace(">", "&gt;")
        with chat_container:
            with ui.row().classes('w-full justify-start items-start gap-2'):
                ui.icon('smart_toy', size='18px').classes('text-green-600 mt-1')
                with ui.card().classes(
                    'max-w-[70%] bg-white border border-slate-200 shadow p-2 rounded-lg text-xs'
                ):
                    ui.markdown(safe).classes("text-xs leading-tight")
        chat_scroll.scroll_to(pixels=999999)

    def add_error_message(t):
        with chat_container:
            with ui.row().classes('w-full justify-start items-start gap-2'):
                ui.icon('error_outline', size='18px').classes('text-red-600 mt-1')
                with ui.card().classes(
                    'max-w-[70%] bg-red-50 border border-red-200 shadow-sm p-2 rounded-lg text-xs'
                ):
                    ui.label(f"Error: {t}").classes('text-red-700')
        chat_scroll.scroll_to(pixels=999999)

    async def generate_guidance_report():
        """Generate guidance report (PDF and JSON) from current specification."""
        global thinking_indicator
        
        # Show thinking indicator
        add_thinking_message()
        thinking_indicator_text = "Generating guidance report..."
        if thinking_indicator:
            # Update the thinking message
            with thinking_indicator:
                thinking_indicator.clear()
                ui.icon('description', size='18px').classes('text-green-600 mt-1')
                with ui.card().classes(
                    'max-w-[70%] bg-green-100 border border-green-200 shadow-sm p-2 rounded-lg text-xs'
                ):
                    with ui.row().classes('items-center gap-2'):
                        ui.spinner(size='xs', color='green')
                        ui.label(thinking_indicator_text).classes('text-green-800')
        
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client_http:  # 5 min timeout for guidance generation
                response = await client_http.post(GUIDANCE_URL)
                data = response.json()
            
            if thinking_indicator:
                thinking_indicator.delete()
                thinking_indicator = None
            
            if data.get("success"):
                # Show success message with download links
                json_url = data.get("json_url")
                pdf_url = data.get("pdf_url")
                
                with chat_container:
                    with ui.row().classes('w-full justify-start items-start gap-2'):
                        ui.icon('check_circle', size='18px').classes('text-green-600 mt-1')
                        with ui.card().classes(
                            'max-w-[70%] bg-green-50 border border-green-200 shadow-sm p-2 rounded-lg text-xs'
                        ):
                            ui.label("✅ Guidance report generated successfully!").classes('text-green-800 font-bold mb-2')
                            with ui.column().classes('gap-1 mt-2'):
                                if json_url:
                                    ui.link(
                                        '📄 Download JSON Report',
                                        f"{DOWNLOAD_BASE_URL}/{json_url.split('/')[-1]}",
                                        new_tab=True
                                    ).classes('text-blue-600 hover:text-blue-800 text-xs')
                                if pdf_url:
                                    ui.link(
                                        '📑 Download PDF Report',
                                        f"{DOWNLOAD_BASE_URL}/{pdf_url.split('/')[-1]}",
                                        new_tab=True
                                    ).classes('text-blue-600 hover:text-blue-800 text-xs')
                
                chat_scroll.scroll_to(pixels=999999)
            else:
                error_msg = data.get("message", "Unknown error")
                add_error_message(f"Failed to generate guidance: {error_msg}")
                
        except Exception as e:
            if thinking_indicator:
                thinking_indicator.delete()
                thinking_indicator = None
            add_error_message(f"Error generating guidance report: {str(e)}")
            chat_scroll.scroll_to(pixels=999999)

    user_input.on('keydown.enter', send_message)
    send_button.on('click', send_message)
    guidance_button.on('click', generate_guidance_report)


# ---------------------------------------------------------
# LEFT PANEL — DASH GRAPH + SPEC
# ---------------------------------------------------------
with ui.column().classes('absolute left-0 top-0 bottom-0 w-2/3 bg-slate-50 p-4'):

    ui.label("System Visualization (Dash Cytoscape)").classes("text-xl font-bold mb-2")

    # 👇 iframe reference (IMPORTANT)
    dash_iframe = ui.html(
        """
        <iframe id="dash-frame"
            src="http://localhost:8050/dash"
            scrolling="no"
            class="w-full h-[600px] block border-none rounded-xl overflow-hidden">
        </iframe>
        """,
        sanitize=False,
    ).classes(
        'w-full border-none rounded-xl block'
    ).style('height: 100%; overflow-y: auto;')

    with ui.column().classes(
        'w-full mt-3 bg-white border border-slate-200 rounded-xl shadow-lg p-4'
    ).style('height: 280px; overflow-y: auto;'):

        with ui.row().classes('w-full items-center gap-2 mb-2 pb-2 border-b border-slate-200'):
            ui.icon('description', size='22px').classes('text-slate-600')
            ui.label('System Specification').classes('text-base font-bold text-slate-800')

        spec_footer = ui.column().classes('w-full')

        with spec_footer:
            with ui.row().classes('w-full h-full items-center justify-center'):
                ui.label('💡 No specification yet. Start chatting to build your system!').classes(
                    'text-slate-400 text-sm italic'
                )


ui.run(host='0.0.0.0', port=8080)