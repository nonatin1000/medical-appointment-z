from app.graph.graph import build_appointment_graph
from app.services.appointment_service import AppointmentService
from app.services.open_router_service import OpenRouterService


def build_graph():
    llm_client = OpenRouterService()
    appointment_service = AppointmentService()
    return build_appointment_graph(llm_client, appointment_service)


graph = build_graph()