import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.engine.mas_engine import MASAutomationEngine
from backend.engine.guidance_agent import GuidanceAgent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
engine = MASAutomationEngine()

# Initialize guidance agent with config from .env
guidance_output_dir = os.getenv("GUIDANCE_OUTPUT_DIR", None)
if guidance_output_dir:
    guidance_agent = GuidanceAgent(output_dir=guidance_output_dir)
else:
    # Default to reports directory in project root
    project_root = Path(__file__).parent.parent
    guidance_agent = GuidanceAgent(output_dir=str(project_root / "reports"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list

class ChatResponse(BaseModel):
    reply: str
    graph: list
    spec: dict

class GuidanceResponse(BaseModel):
    success: bool
    message: str
    json_path: str = None
    pdf_path: str = None
    json_url: str = None
    pdf_url: str = None

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply, graph, spec = engine.process(req.message, req.history)
    return ChatResponse(reply=reply, graph=graph, spec=spec)

@app.post("/generate-guidance", response_model=GuidanceResponse)
async def generate_guidance():
    """
    Generate guidance report (PDF and JSON) from current MAS specification.
    """
    try:
        # Get current specification from the engine
        current_spec = engine.spec.to_dict()
        
        # Check if spec has required fields
        if not current_spec.get("task") or not current_spec.get("goal"):
            return GuidanceResponse(
                success=False,
                message="Specification is incomplete. Please provide at least task and goal before generating guidance."
            )
        
        # Generate the report
        result = guidance_agent.generate_report(
            requirements_spec=current_spec,
            additional_context=None,
            base_filename=None  # Will generate timestamped filename
        )
        
        report_data = result.get("report_data", {})
        json_path = result.get("json_path", "")
        pdf_path = result.get("pdf_path", "")
        
        # Generate URLs for file access
        json_filename = Path(json_path).name if json_path else None
        pdf_filename = Path(pdf_path).name if pdf_path else None
        
        json_url = f"/download-guidance/{json_filename}" if json_filename else None
        pdf_url = f"/download-guidance/{pdf_filename}" if pdf_filename else None
        
        return GuidanceResponse(
            success=True,
            message="Guidance report generated successfully!",
            json_path=json_path,
            pdf_path=pdf_path,
            json_url=json_url,
            pdf_url=pdf_url
        )
        
    except Exception as e:
        return GuidanceResponse(
            success=False,
            message=f"Error generating guidance report: {str(e)}"
        )

@app.get("/download-guidance/{filename}")
async def download_guidance(filename: str):
    """
    Download a generated guidance report file (JSON or PDF).
    """
    try:
        # Get the output directory
        output_dir = guidance_agent._report_generator.output_dir
        file_path = output_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type
        if filename.endswith(".json"):
            media_type = "application/json"
        elif filename.endswith(".pdf"):
            media_type = "application/pdf"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")
