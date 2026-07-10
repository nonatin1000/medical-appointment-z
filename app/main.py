from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field, model_validator

from app.config import configure_langsmith
from app.graph.factory import build_graph

configure_langsmith()

logger = logging.getLogger(__name__)

app = FastAPI()
graph = build_graph()


class ChatRequest(BaseModel):
    """Body alinhado ao TS (`question`), com `message` como alias opcional."""

    question: Optional[str] = Field(default=None, min_length=10)
    message: Optional[str] = Field(default=None, min_length=10)
    professionals: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_question_or_message(self) -> "ChatRequest":
        if not (self.question or self.message):
            raise ValueError("question is required")
        return self

    @property
    def text(self) -> str:
        return self.question or self.message or ""


@app.post("/chat")
def chat(payload: ChatRequest):
    """Chat with the appointment graph."""
    initial_state = {
        "messages": [HumanMessage(content=payload.text)],
        "professionals": payload.professionals,
    }

    try:
        return graph.invoke(
            initial_state,
            config={"run_name": "medical-appointment-graph"},
        )
    except Exception:
        logger.exception("Error processing chat request")
        return JSONResponse(
            status_code=500,
            content={"error": "An error occurred while processing your request."},
        )
