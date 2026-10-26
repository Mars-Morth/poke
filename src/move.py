from dataclasses import dataclass, field
from src.target_types import TargetType
from src.types import Type
from src.move_effects import MoveEffect


@dataclass
class Move:
    name: str
    type: Type
    max_pp: int
    current_pp: int
    target_type: TargetType
    accuracy: int
    priority: int
    description: str
    effects: list["MoveEffect"] = field(default_factory=list)
