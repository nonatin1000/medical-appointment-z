from __future__ import annotations

import logging
from typing import Any, Dict, Callable
from app.services.appointment_service import AppointmentService
from datetime import datetime

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS = {
    "professional_id": "Professional ID is required",
    "datetime": "Appointment datetime is required",
    "patient_name": "Patient name is required",
}


def create_scheduler_node(appointment_service: AppointmentService) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Cria um nó de agendamento de consulta."""
    logger.info("Creating scheduler node...")

    def scheduler_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule an appointment.
        """
        logger.info("Scheduling appointment...")

        try:
            errors = [message for field, message in _REQUIRED_FIELDS.items() if not state.get(field)]
            if errors:
                error_messages = ", ".join(errors)
                logger.warning("Validation failed: %s", error_messages)
                return {**state, "action_success": False, "action_error": error_messages}

            appt_date = datetime.fromisoformat(state["datetime"].replace("Z", "+00:00"))
            appointment = appointment_service.book_appointment(
                professional_id=int(state["professional_id"]),
                date=appt_date,
                patient_name=state["patient_name"],
                reason=state.get("reason") or "general consultation",
            )
            logger.info("Appointment scheduled successfully")
            return {**state, "action_success": True, "appointment_data": appointment}
        except Exception as e:
            logger.error(f"Error scheduling appointment: {e}")
            return {
                **state,
                "action_success": False,
                "action_error": str(e) or "Scheduling failed",
            }
            
    return scheduler_node