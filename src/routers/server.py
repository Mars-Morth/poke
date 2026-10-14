from fastapi import APIRouter, Request

TRAINERS = [
    "Ash",
    "Brock",
    "Misty",
]  # TODO: replace with class (https://github.com/Mars-Morth/poke/issues/15)

router = APIRouter()


@router.get("/")
def root(request: Request):
    return {
        "status": "ok",
        "role": request.app.state.context.current_state.name,
        "server_ip": str(request.app.state.context._active_server_ip),
    }


@router.get("/trainers")
def get_trainers():
    return TRAINERS
