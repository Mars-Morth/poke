from src.move import Move
from src.move_effects import DamageEffect, StatEffect, parse_move_effect
from src.target_types import TargetType
from src.types import Type
from src.load_move import load_move


def test_move_creation():
    move = Move(
        name="Tackle",
        type=Type.NORMAL,
        max_pp=35,
        current_pp=35,
        target_type=TargetType.SINGLE,
        accuracy=100,
        priority=0,
        description="A physical attack in which the user charges and slams into the target with its whole body.",
        effects=[]
    )
    assert move.name == "Tackle"
    assert move.type == Type.NORMAL
    assert move.max_pp == 35
    assert move.current_pp == 35
    assert move.target_type == TargetType.SINGLE
    assert move.accuracy == 100
    assert move.priority == 0
    assert move.description == "A physical attack in which the user charges and slams into the target with its whole body."
    assert move.effects == []

def test_move_effect_damage():
    damage_effect = DamageEffect(power=50, damage_type="physical")
    assert damage_effect.power == 50
    assert damage_effect.damage_type == "physical"
    assert parse_move_effect("damage:50:physical") == damage_effect

def test_move_effect_status():
    stat_effect = StatEffect(stat="attack", stages=-1, chance=100)
    assert stat_effect.stat == "attack"
    assert stat_effect.chance == 100
    assert parse_move_effect("stat:attack:-1:100") == stat_effect

def test_move_creation_with_effects():
    damage_effect = DamageEffect(power=50, damage_type="physical")
    stat_effect = StatEffect(stat="atk", stages=-1, chance=100)
    move = Move(
        name="Tackle",
        type=Type.NORMAL,
        max_pp=35,
        current_pp=35,
        target_type=TargetType.SINGLE,
        accuracy=100,
        priority=0,
        description="A physical attack in which the user charges and slams into the target with its whole body.",
        effects=[damage_effect, stat_effect]
    )
    assert move.effects == [damage_effect, stat_effect]

def test_load_move():
    move = load_move("Tackle")
    assert move.name == "Tackle"
    assert move.type == Type.NORMAL
    assert move.max_pp == 35
    assert move.current_pp == 35
    assert move.target_type == TargetType.SINGLE
    assert move.accuracy == 100
    assert move.priority == 0
    assert move.description == "Inflicts regular damage with no additional effect."
    assert move.effects == [DamageEffect(power=40, damage_type="physical")]

def test_load_move_request_ignores_case_and_outer_whitespace():
    move = load_move("  tAcKlE  ")
    assert move.name == "Tackle"

def test_load_move_stat_effect():
    move = load_move("Growl")
    assert move.effects == [StatEffect(stat="atk", stages=-1, chance=100)]
