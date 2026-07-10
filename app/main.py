from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from app.config import configure_langsmith
from app.graph.graph import build_appointment_graph

configure_langsmith()

logger = logging.getLogger(__name__)

app = FastAPI()
graph = build_appointment_graph()


class ChatRequest(BaseModel):
    message: str
    professionals: List[Dict[str, Any]] = Field(default_factory=list)


@app.post("/chat")
def chat(payload: ChatRequest):
    """Chat with the appointment graph."""
    initial_state = {
        "messages": [HumanMessage(content=payload.message)],
        "professionals": payload.professionals,
    }

    try:
        result = graph.invoke(
            initial_state,
            config={"run_name": "medical-appointment-graph"},
        )
        return {"state": result}
    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request.",
        ) from e
