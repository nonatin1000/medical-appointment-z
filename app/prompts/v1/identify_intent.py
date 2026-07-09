from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from typing import Iterable, Dict, Any
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)


def get_system_prompt(professionals: Iterable[Dict[str, Any]]) -> str:
    """
    Get the system prompt for the identify intent.
    """

    logger.info(f"Getting system prompt for professionals: {json.dumps(professionals)}")

    payload = {
        "role": "Intent Classifier for Medical Appointments",
        "task": "Identify user intent and extract all appointment-related details",
        "professionals": [
            {"id": p["id"], "name": p["name"], "specialty": p["specialty"]}
            for p in professionals
        ],
        "current_date": datetime.now(timezone.utc).isoformat(),
        "rules": {
            "schedule": {
                "description": "User wants to book/schedule a new appointment",
                "keywords": ["schedule", "book", "appointment", "I want to", "make an appointment"],
                "required_fields": ["professional_id", "datetime", "patient_name"],
                "optional_fields": ["reason"],
            },
            "cancel": {
                "description": "User wants to cancel an existing appointment",
                "keywords": ["cancel", "remove", "delete", "cancel my appointment"],
                "required_fields": ["professional_id", "datetime", "patient_name"],
            },
            "unknown": {
                "description": "Anything not related to scheduling or cancelling appointments",
                "examples": ["weather questions", "general info", "unrelated queries"],
            },
        },
        "extraction_instructions": {
            "professional_id": "Match the professional name mentioned in the question to the ID from the professionals list. Use fuzzy matching.",
            "professional_name": "Extract the professional name as mentioned by the user",
            "datetime": "Parse relative dates (today, tomorrow) and times. Convert to ISO format. Use current_date as reference.",
            "patient_name": "Extract the patient name from the question or context",
            "reason": "Extract the reason/purpose for the appointment (only for scheduling)",
        },
        "examples": [
            {
                "input": "I want to schedule with Dr. Alicio da Silva for tomorrow at 4pm for a check-up",
                "output": {
                    "intent": "schedule",
                    "professional_id": 1,
                    "professional_name": "Dr. Alicio da Silva",
                    "datetime": "2026-02-12T16:00:00.000Z",
                    "reason": "check-up",
                },
            },
            {
                "input": "Cancel my appointment with Dr. Ana Pereira today at 11am",
                "output": {
                    "intent": "cancel",
                    "professional_id": 2,
                    "professional_name": "Dr. Ana Pereira",
                    "datetime": "2026-02-11T11:00:00.000Z",
                },
            },
            {
                "input": "What is the weather today?",
                "output": {"intent": "unknown"},
            },
        ],
    }

    logger.info(f"System prompt payload: {json.dumps(payload)}")

    return json.dumps(payload)


USER_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["question"],
    template_format="jinja2",
    template=json.dumps(
        {
            "question": "{{ question }}",
            "instructions": [
                "Carefully analyze the question to determine the user intent",
                "Extract all relevant appointment details",
                "Convert dates and times to ISO format",
                "Match professional names to their IDs",
                "Return only the fields that are present in the question",
            ],
        }
    ),
)
