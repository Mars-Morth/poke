import csv

from src.move import Move
from src.types import Type
from src.target_types import TargetType
from src.move_effects import parse_move_effect


def load_move(name: str) -> Move:
    requested_name = name.strip().casefold()
    with open("data/moves.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["name"].strip().casefold() == requested_name:
                return Move(
                    name=row["name"],
                    type=Type[row["type"].upper()],
                    max_pp=int(row["max_pp"]),
                    current_pp=int(row["max_pp"]),
                    effects=[
                        parse_move_effect(effect)
                        for effect in row["effects"].split("/")
                        if effect
                    ],
                    accuracy=float(row["accuracy"]),
                    target_type=TargetType[row["target_type"].upper()],
                    priority=int(row["priority"]),
                    description=row["description"],
                )
    raise ValueError(f"Unknown move: {name}")