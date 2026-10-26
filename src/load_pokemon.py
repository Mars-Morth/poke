import csv

from src.pokemon import Pokemon
from src.types import Type


def load_pokemon(species):
    with open('data/pokedex.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['species'] == species:
                types = [Type(t) for t in row['types'].split('/')]
                hp = int(row['hp'])
                atk = int(row['atk'])
                defe = int(row['defe'])
                satk = int(row['satk'])
                sdef = int(row['sdef'])
                spe = int(row['spe'])
                return Pokemon(species, types, hp, atk, defe, satk, sdef, spe)
    raise ValueError(f"Unknown Pokemon: {species}")
