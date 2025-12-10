✅ 1. Create a Python virtual environment
cd multi-agent-automation
python3 -m venv auto


Activate it:

source auto/bin/activate

✅ 2. Upgrade pip
pip install --upgrade pip

✅ 3. Install required packages

For your current UI (NiceGUI + FastAPI for future backend):

pip install nicegui fastapi uvicorn


If you plan to add visualization using CytoscapeJS, no Python install is needed — it loads from CDN.

📌 Optional useful packages (but not required now):
pip install pydantic python-dotenv httpx langchain openai

✅ 4. Run the UI app

Navigate to webui:

cd webui


Then run:

python app.py


NiceGUI will start a local server:

Running on http://localhost:8080

