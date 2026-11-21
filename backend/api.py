import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.classifier import analyze_style
from src.graph_rag import verify_and_rewrite

app = FastAPI(
    title="Hybrid GraphRAG Disinformation & Toxicity Analysis API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Treść tweeta lub wypowiedzi do analizy")


class AnalyzeResponse(BaseModel):
    text: str
    sentiment: str
    toxicity_score: float
    is_toxic: bool
    verdict: str
    explanation: str
    censored_text: str
    neutralized_text: str
    subgraph_edges: list[list[str]]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_tweet(payload: AnalyzeRequest):
    style_res = analyze_style(payload.text)
    rag_res = verify_and_rewrite(payload.text)

    raw_edges = rag_res.get("subgraph_edges", [])
    subgraph_edges = [list(edge) for edge in raw_edges]

    return {
        "text": payload.text,
        "sentiment": style_res["sentiment"],
        "toxicity_score": style_res["toxicity_score"],
        "is_toxic": style_res["is_toxic"],
        "verdict": rag_res["verdict"],
        "explanation": rag_res["explanation"],
        "censored_text": rag_res["censored_text"],
        "neutralized_text": rag_res["neutralized_text"],
        "subgraph_edges": subgraph_edges,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
