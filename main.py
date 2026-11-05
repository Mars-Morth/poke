from src.battle import Battle
from src.pokemon import Pokemon
from src.types import Type
from src.load_pokemon import load_pokemon
from src.load_move import load_move
from src.battle import Battle


bulbasaur = load_pokemon("Bulbasaur")
charmander = load_pokemon("Charmander")
bulbasaur.moves.append(load_move("Tackle"))
charmander.moves.append(load_move("Scratch"))
battle = Battle([bulbasaur], [charmander])

damage = battle.calculate_damage(battle.pokemon1, battle.pokemon2, battle.pokemon1.moves[0].type, battle.pokemon1.moves[0].effects[0])
print(damage)
print(charmander.hp)