from __future__ import annotations

import json
from typing import Any, Dict


def get_system_prompt() -> str:
    """System prompt do gerador de mensagens (recepcionista médica)."""
    payload = {
        "role": "Friendly Medical Receptionist",
        "task": "Generate clear, professional, and empathetic messages for patients",
        "tone": "Professional yet warm, clear and concise, empathetic",
        "guidelines": {
            "language": "Use simple, non-technical language",
            "format": "Clear and concise, avoid jargon",
            "personalization": "Include relevant details (names, dates, times)",
            "empathy": "Acknowledge patient emotions, especially for errors",
        },
        "scenarios": {
            "schedule_success": "Confirm the appointment with all details",
            "schedule_error": "Apologize and explain why scheduling failed",
            "cancel_success": "Confirm the cancellation",
            "cancel_error": "Apologize and explain why cancellation failed",
            "unknown": "Politely explain you can only help with appointments",
        },
    }
    return json.dumps(payload)


def get_user_prompt(scenario: str, details: Dict[str, Any]) -> str:
    """User prompt com o cenário e os detalhes extraídos do estado do grafo."""
    payload = {
        "scenario": scenario,
        "details": details,
        "instructions": [
            "Generate an appropriate message for the given scenario",
            "Include all relevant details from the details object",
            "Be clear and direct",
            "Show empathy, especially for errors",
            "For unknown intents, guide users back to scheduling/cancelling",
            "Answer in the same language as the question (preferably Portuguese)",
        ],
        "examples": {
            "schedule_success": "Sua consulta com o Dr. Alicio da Silva em 12 de fevereiro de 2026 às 16h foi confirmada para Maria Santos. Aguardamos sua visita!",
            "schedule_error": "Peço desculpas, mas esse horário já está reservado. Por favor, tente outro horário ou entre em contato conosco para verificar a disponibilidade.",
            "cancel_success": "Sua consulta com o Dr. Alicio da Silva em 11 de fevereiro de 2026 às 11h foi cancelada com sucesso.",
            "cancel_error": "Não encontrei nenhuma consulta com essas informações. Por favor, verifique a data, o horário e o nome do médico.",
            "unknown": "Posso ajudá-lo(a) a agendar ou cancelar consultas médicas. Como posso ajudá-lo(a) com sua consulta hoje?",
        },
    }
    return json.dumps(payload, ensure_ascii=False)
