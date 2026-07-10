from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, List


@dataclass
class Appointment:
    date: str
    patient_name: str
    reason: str
    professional_id: int


def _today_at_11_utc() -> datetime:
    """
    Get the current date and time in UTC at 11:00 AM.
    """
    now = datetime.now(timezone.utc)
    return now.replace(hour=11, minute=0, second=0, microsecond=0)


def _tomorrow_at_14_utc() -> datetime:
    """
    Get the current date and time in UTC at 14:00 PM.
    """
    now = datetime.now(timezone.utc)
    return now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)


professionals: List[dict] = [
    {"id": 1, "name": "Dr. Alicio da Silva", "specialty": "Cardiologia"},
    {"id": 2, "name": "Dra. Ana Pereira", "specialty": "Dermatologia"},
    {"id": 3, "name": "Dra. Carol Gomes", "specialty": "Neurologia"},
]
_appointments: List[dict] = [
    {
        "date": _today_at_11_utc().isoformat(),
        "patient_name": "Joao da Silva",
        "reason": "check-up regular",
        "professional_id": professionals[0]["id"],
    },
    {
        "date": _tomorrow_at_14_utc().isoformat(),
        "patient_name": "Luana Costa",
        "reason": "Erupção cutânea",
        "professional_id": professionals[1]["id"],
    },
]


class AppointmentService:

    def get_appointment(self, professional_id: int, date: datetime, patient_name: Optional[str] = None) -> Optional[Appointment]:
        for appointment in _appointments:
            if (
                appointment["professional_id"] == professional_id
                and appointment["date"] == date.isoformat()
                and (not patient_name or appointment["patient_name"] == patient_name)
            ):
                return Appointment(**appointment)
        return None

    def check_availability(self, professional_id: int, date: datetime) -> bool:
        return self.get_appointment(professional_id, date) is None

    def book_appointment(self, professional_id: int, date: datetime, patient_name: str, reason: str) -> dict:
        if not self.check_availability(professional_id, date):
            raise ValueError("Horário indisponível para este profissional")

        new_appointment = {
            "date": date.isoformat(),
            "patient_name": patient_name,
            "reason": reason,
            "professional_id": professional_id,
        }
        _appointments.append(new_appointment)
        return new_appointment

    def cancel_appointment(self, professional_id: int, patient_name: str, date: datetime) -> bool:
        for index, appointment in enumerate(_appointments):
            if (
                appointment["professional_id"] == professional_id
                and appointment["date"] == date.isoformat()
                and appointment["patient_name"] == patient_name
            ):
                del _appointments[index]
                return True
        raise ValueError("Agendamento não encontrado para cancelamento")
