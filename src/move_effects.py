from dataclasses import dataclass
from typing import Callable


class MoveEffect:
    pass


@dataclass
class DamageEffect(MoveEffect):
    power: int
    damage_type: str # "physical" or "special"

@dataclass
class StatEffect(MoveEffect):
    stat: str
    stages: int
    chance: int


def _parse_damage(arguments: list[str]) -> DamageEffect:
    if len(arguments) != 2 or arguments[1] not in {"physical", "special"}:
        raise ValueError("expected format damage:<power>:<physical|special>")
    return DamageEffect(power=int(arguments[0]), damage_type=arguments[1])


def _parse_stat(arguments: list[str]) -> StatEffect:
    if len(arguments) != 3 or not arguments[0]:
        raise ValueError("expected format stat:<name>:<stages>:<chance>")
    return StatEffect(stat=arguments[0], stages=int(arguments[1]), chance=int(arguments[2]))


_EFFECT_PARSERS: dict[str, Callable[[list[str]], MoveEffect]] = {
    "damage": _parse_damage,
    "stat": _parse_stat,
}


def parse_move_effect(value: str) -> MoveEffect:
    effect_type, separator, raw_arguments = value.strip().partition(":")
    parser = _EFFECT_PARSERS.get(effect_type)
    if not separator or parser is None:
        raise ValueError(f"Unsupported move effect: {value}")

    try:
        return parser(raw_arguments.split(":"))
    except ValueError as error:
        raise ValueError(f"Invalid move effect {value!r}: {error}") from error
