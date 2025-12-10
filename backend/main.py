from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.engine.mas_engine import MASAutomationEngine


app = FastAPI()
engine = MASAutomationEngine()

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

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply, graph, spec = engine.process(req.message, req.history)
    return ChatResponse(reply=reply, graph=graph, spec=spec)
