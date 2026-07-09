from __future__ import annotations

import logging
from typing import Any, Dict
from app.services.appointment_service import AppointmentService
from datetime import datetime

logger = logging.getLogger(__name__)


def scheduler_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Schedule an appointment.
    """
    logger.info("Scheduling appointment...")
    required_fields = ["professional_id", "patient_name", "datetime"]

    try:
        if any(not state.get(field) for field in required_fields):
            return {**state, "action_success": False}
            
        service = AppointmentService()
        appt_date = datetime.fromisoformat(state["datetime"].replace("Z", "+00:00"))
        appointment = service.book_appointment(
            professional_id=int(state.get("professional_id", 0)),
            date=appt_date,
            patient_name=state.get("patient_name", ""),
            reason=state.get("reason", ""),
        )
        state["appointment"] = appointment
        logger.info("Appointment scheduled successfully")
        return {**state, "action_success": True, "appointment_data": appointment}
    except Exception as e:
        logger.error(f"Error scheduling appointment: {e}")
        return {
            **state,
            "action_success": False,
            "action_error": str(e) or "Scheduling failed",
        }