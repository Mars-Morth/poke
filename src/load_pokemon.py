import csv

from src.pokemon import Pokemon


def load_pokemon(species):
    with open('data/pokedex.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['species'] == species:
                types = row['types'].split('/')
                hp = int(row['hp'])
                atk = int(row['atk'])
                defe = int(row['defe'])
                satk = int(row['satk'])
                sdef = int(row['sdef'])
                spe = int(row['spe'])
                return Pokemon(species, types, hp, atk, defe, satk, sdef, spe)
