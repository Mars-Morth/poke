class Pokemon:

    def __init__(self, species, types, hp, atk, defe, satk, sdef, spe, moves=[]):
        self.species = species
        self.types = types

        self.hp = hp
        self.atk = atk
        self.defe = defe
        self.satk = satk
        self.sdef = sdef
        self.spe = spe

        self.moves = moves

    def __str__(self):
        return f"{self.species} ({'/'.join(self.types)}) HP:{self.hp} ATK:{self.atk} DEF:{self.defe} SATK:{self.satk} SDEF:{self.sdef} SPE:{self.spe} MOVES:{', '.join(self.moves)}"
