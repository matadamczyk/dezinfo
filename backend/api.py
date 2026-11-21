import sys
from pathlib import Path
from contextlib import asynccontextmanager

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.classifier import analyze_style, get_model_and_tokenizer
from src.graph_rag import verify_and_rewrite, get_knowledge_base


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_model_and_tokenizer()
        get_knowledge_base()
    except Exception:
        pass
    yield


app = FastAPI(
    title="Hybrid GraphRAG Disinformation & Toxicity Analysis API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Treść tweeta lub wypowiedzi do analizy",
    )


class StyleModel(BaseModel):
    sentiment: str
    toxicity_score: float
    is_toxic: bool


class FactCheckModel(BaseModel):
    verdict: str
    explanation: str
    censored_text: str
    neutralized_text: str
    subgraph_edges: list[list[str]]


class AnalyzeResponse(BaseModel):
    style: StyleModel
    fact_check: FactCheckModel
    original_text: str
    text: str | None = None
    sentiment: str | None = None
    toxicity_score: float | None = None
    is_toxic: bool | None = None
    verdict: str | None = None
    explanation: str | None = None
    censored_text: str | None = None
    neutralized_text: str | None = None
    subgraph_edges: list[list[str]] | None = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_tweet(payload: AnalyzeRequest):
    try:
        style_res = analyze_style(payload.text)
        rag_res = verify_and_rewrite(payload.text)

        raw_edges = rag_res.get("subgraph_edges", [])
        subgraph_edges = [list(edge) for edge in raw_edges]

        fact_check_data = {
            "verdict": rag_res["verdict"],
            "explanation": rag_res["explanation"],
            "censored_text": rag_res["censored_text"],
            "neutralized_text": rag_res["neutralized_text"],
            "subgraph_edges": subgraph_edges,
        }

        style_data = {
            "sentiment": style_res["sentiment"],
            "toxicity_score": style_res["toxicity_score"],
            "is_toxic": style_res["is_toxic"],
        }

        return {
            "style": style_data,
            "fact_check": fact_check_data,
            "original_text": payload.text,
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
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Błąd podczas przeprowadzania analizy: {str(exc)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
