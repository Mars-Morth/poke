from fastapi import APIRouter, Request

from logic.states import ClientAndServer, Promoting

router = APIRouter()


@router.get("/")
def root():
    return None


@router.post("/serve")
def promote_to_server(request: Request):
    request.app.state.context.transition_to(Promoting)
    request.app.state.context.transition_to(ClientAndServer)
    request.app.state.context._active_server_ip = request.app.state.context._LOCAL_IP
    return {
        "status": "ok",
        "role": request.app.state.context.current_state.name,
    }
