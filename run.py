import subprocess
import sys
import time
import signal
import os

# Run: python run.py

BACKEND_APP = "backend.main:app"
WEBUI_PATH = "webui/app.py"
DASH_PATH = "backend/engine/visualization/graph_dash_app.py"



def start_backend():
    print("🚀 Starting FastAPI backend on port 8000...")
    return subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            BACKEND_APP,
            "--host", "0.0.0.0",
            "--port", "8000",
        ]
    )


def start_dash():
    print("📊 Starting Dash Cytoscape on port 8050...")
    return subprocess.Popen(
        [sys.executable, DASH_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def start_webui():
    print("🖥️  Starting NiceGUI web UI on port 8080...")
    return subprocess.Popen(
        [sys.executable, WEBUI_PATH]
    )


def main():
    print("========================================")
    print("  MAS AUTOMATION SYSTEM — STARTING")
    print("========================================\n")

    backend_proc = start_backend()
    time.sleep(2)

    dash_proc = start_dash()
    time.sleep(1)

    webui_proc = start_webui()

    print("\n🎉 System is running!")
    print("➡ Backend: http://localhost:8000/docs")
    print("➡ Dash:    http://localhost:8050/dash")
    print("➡ Web UI:  http://localhost:8080")
    print("\nPress CTRL+C to stop everything.\n")

    try:
        backend_proc.wait()
        dash_proc.wait()
        webui_proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping processes...")
        for proc in (backend_proc, dash_proc, webui_proc):
            proc.terminate()
        print("✅ All processes stopped.")


if __name__ == "__main__":
    main()
