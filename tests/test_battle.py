import pytest

from src.battle import Battle
from src.pokemon import Pokemon
from src.types import Type
from src.load_pokemon import load_pokemon
from src.load_move import load_move
from src.battle import Battle

@pytest.fixture
def battle():
    bulbasaur = load_pokemon("Bulbasaur")
    charmander = load_pokemon("Charmander")
    bulbasaur.moves.append(load_move("Tackle"))
    charmander.moves.append(load_move("Scratch"))
    return Battle([bulbasaur], [charmander])

def test_battle_initialization(battle):
    assert battle.turn_count == 0
    assert not battle.battle_over
    assert battle.pokemon1.species == load_pokemon("Bulbasaur").species
    assert battle.pokemon2.species == load_pokemon("Charmander").species

def test_calculate_damage(battle):
    damage = battle.calculate_damage(battle.pokemon1, battle.pokemon2, battle.pokemon1.moves[0].type, battle.pokemon1.moves[0].effects[0])
    assert damage > 0
