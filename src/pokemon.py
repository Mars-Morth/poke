class Pokemon:

    def __init__(self, species, types, hp, atk, defe, satk, sdef, spe, moves=None):
        self.species = species
        self.types = types

        self.hp = hp
        self.atk = atk
        self.defe = defe
        self.satk = satk
        self.sdef = sdef
        self.spe = spe

        self.moves = [] if moves is None else moves

    def __str__(self):
        type_names = "/".join(pokemon_type.value for pokemon_type in self.types)
        move_names = ", ".join(str(move) for move in self.moves)
        return f"{self.species} ({type_names}) HP:{self.hp} ATK:{self.atk} DEF:{self.defe} SATK:{self.satk} SDEF:{self.sdef} SPE:{self.spe} MOVES:{move_names}"

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int):
        self.hp = max(self.hp - damage, 0)
