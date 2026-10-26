from fastapi import APIRouter, Request

from logic.states import Promoting

router = APIRouter()


@router.get("/")
def root():
    return None


@router.post("/serve")
async def promote_to_server(request: Request):
    context = request.app.state.context
    await context.transition_to(Promoting)
    return {
        "status": "ok",
        "role": request.app.state.context.current_state.name,
    }
