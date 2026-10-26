from src.pokemon import Pokemon
from src.load_pokemon import load_pokemon

from src.types import Type


def test_pokemon_creation():
    p = Pokemon("Charmander", [Type.FIRE], 39, 52, 43, 60, 50, 65)
    assert p.species == "Charmander"
    assert p.types == [Type.FIRE]
    assert p.hp == 39
    assert p.atk == 52
    assert p.defe == 43
    assert p.satk == 60
    assert p.sdef == 50
    assert p.spe == 65

def test_pokemon_types():
    p = Pokemon("Bulbasaur", [Type.GRASS, Type.POISON], 45, 49, 49, 65, 65, 45)
    assert p.species == "Bulbasaur"
    assert p.types == [Type.GRASS, Type.POISON]

def test_load_pokemon():
    p = load_pokemon("Charmander")
    assert p.species == "Charmander"
    assert p.types == [Type.FIRE]
    assert p.hp == 39
    assert p.atk == 52
    assert p.defe == 43
    assert p.satk == 60
    assert p.sdef == 50
    assert p.spe == 65

def test_pokemon_is_alive():
    p = Pokemon("Charmander", [Type.FIRE], 39, 52, 43, 60, 50, 65)
    assert p.is_alive() is True
    p.hp = 0
    assert p.is_alive() is False

def test_pokemon_take_damage():
    p = Pokemon("Charmander", [Type.FIRE], 39, 52, 43, 60, 50, 65)
    p.take_damage(10)
    assert p.hp == 29
    p.take_damage(50)
    assert p.hp == 0
    assert p.is_alive() is False
