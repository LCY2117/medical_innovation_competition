from fastapi import APIRouter, WebSocket

from app.services.incidents import IncidentService


def build_ws_router(service: IncidentService) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws")
    async def ws_endpoint(websocket: WebSocket, incidentId: str) -> None:
        await service.handle_websocket(websocket, incidentId)

    return router
