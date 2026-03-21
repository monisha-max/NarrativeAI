import orjson
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog

from app.agents.orchestrator import OrchestratorAgent
from app.agents.base import AgentContext

router = APIRouter()
logger = structlog.get_logger()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for progressive dossier rendering."""
    await websocket.accept()
    logger.info("ws.connected", session_id=session_id)

    try:
        while True:
            data = await websocket.receive_text()
            request = orjson.loads(data)
            action = request.get("action")

            if action == "build_dossier":
                context = AgentContext(
                    dossier_id=request.get("dossier_id"),
                    query=request.get("query"),
                    data={
                        "dossier_slug": request.get("dossier_slug"),
                        "max_articles": request.get("max_articles", 50),
                        "perspective": request.get("perspective", {}),
                    },
                )

                orchestrator = OrchestratorAgent()

                # Stream progressive updates
                async for update in orchestrator.execute_progressive(context):
                    await websocket.send_json(update)

            elif action == "update_dossier":
                # Re-run pipeline for an existing dossier
                context = AgentContext(
                    dossier_id=request.get("dossier_id"),
                    query=request.get("query"),
                    data={
                        "dossier_slug": request.get("dossier_slug"),
                        "max_articles": request.get("max_articles", 20),
                    },
                )

                orchestrator = OrchestratorAgent()
                result = await orchestrator.run(context)

                await websocket.send_json({
                    "type": "update_complete",
                    "success": result.success,
                    "data": result.data,
                    "duration_ms": result.duration_ms,
                })

            elif action == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                })

    except WebSocketDisconnect:
        logger.info("ws.disconnected", session_id=session_id)
    except Exception as e:
        logger.error("ws.error", session_id=session_id, error=str(e))
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
