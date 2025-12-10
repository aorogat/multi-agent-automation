import subprocess
import sys
import time
import signal
import os

# Paths
BACKEND_PATH = "backend/main.py"
WEBUI_PATH = "webui/app.py"


def start_backend():
    print("🚀 Starting FastAPI backend on port 8000...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
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
    time.sleep(2)  # wait to avoid race condition

    webui_proc = start_webui()

    print("\n🎉 System is running!")
    print("➡ Backend: http://localhost:8000/docs")
    print("➡ Web UI:  http://localhost:8080\n")
    print("Press CTRL+C to stop everything.\n")

    try:
        # Wait for both processes
        backend_proc.wait()
        webui_proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping processes...")
        backend_proc.terminate()
        webui_proc.terminate()
        print("✅ All processes stopped.")


if __name__ == "__main__":
    main()
