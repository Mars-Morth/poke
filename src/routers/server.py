from fastapi import APIRouter

TRAINERS = [
    "Ash",
    "Brock",
    "Misty",
]  # TODO: replace with class (https://github.com/Mars-Morth/poke/issues/15)

router = APIRouter()


@router.get("/")
def root():
    return None


@router.get("/trainers")
def get_trainers():
    return TRAINERS
