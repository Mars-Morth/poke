from random import randint

from src.pokemon import Pokemon
from src.move import Move
from src.types import Type
from src.type_chart import TYPE_CHART
from src.move_effects import DamageEffect, StatEffect


class Battle:
    def __init__(self, team1: list[Pokemon], team2: list[Pokemon]):
        self.turn_count = 0
        self.battle_over = False
        self.player1_team = team1
        self.player2_team = team2
        self.pokemon1 = self.player1_team[0]
        self.pokemon1_stat_modifiers = {"atk": 1, "defe": 1, "satk": 1, "sdef": 1, "spe": 1}
        self.pokemon2 = self.player2_team[0]
        self.pokemon2_stat_modifiers = {"atk": 1, "defe": 1, "satk": 1, "sdef": 1, "spe": 1}


    def process_turn(self, player1_move: Move, player2_move: Move):
        self.turn_count += 1
        if self.pokemon1.spe * self.pokemon1_stat_modifiers["spe"] >= self.pokemon2.spe * self.pokemon2_stat_modifiers["spe"]:
            self.process_move(1, player1_move)
            if not self.battle_over:
                self.process_move(2, player2_move)
        else:
            self.process_move(2, player2_move)
            if not self.battle_over:
                self.process_move(1, player1_move)


    def process_move(self, current_player: int, move: Move):

        if current_player == 1:
            attacker = self.pokemon1
            defender = self.pokemon2
        else:
            attacker = self.pokemon2
            defender = self.pokemon1

        for effect in move.effects:
            if isinstance(effect, DamageEffect):
                damage = self.calculate_damage(attacker, defender, move.type, effect)
                defender.deal_damage(damage)
                if defender.current_hp <= 0:
                    self.battle_over = True
            if not self.battle_over:
                if isinstance(effect, StatEffect):
                    if current_player == 1:
                        if effect.stat in self.pokemon2_stat_modifiers:
                            self.pokemon2_stat_modifiers[effect.stat] += effect.stage
                    else:
                        if effect.stat in self.pokemon1_stat_modifiers:
                            self.pokemon1_stat_modifiers[effect.stat] += effect.stage


    def calculate_damage(self, attacker: Pokemon, defender: Pokemon, move_type: Type, damage_effect: DamageEffect) -> float:

        if attacker == self.pokemon1:
            atk_modifier = self.pokemon1_stat_modifiers["atk"]
            satk_modifier = self.pokemon1_stat_modifiers["satk"]
            def_modifier = self.pokemon2_stat_modifiers["defe"]
            sdef_modifier = self.pokemon2_stat_modifiers["sdef"]
        else:
            atk_modifier = self.pokemon2_stat_modifiers["atk"]
            satk_modifier = self.pokemon2_stat_modifiers["satk"]
            def_modifier = self.pokemon1_stat_modifiers["defe"]
            sdef_modifier = self.pokemon1_stat_modifiers["sdef"]
        
        type_multiplier = 1.0
        if move_type in TYPE_CHART:
            for defender_type in defender.types:
                if defender_type in TYPE_CHART[move_type]:
                    type_multiplier *= TYPE_CHART[move_type][defender_type]

        if damage_effect.damage_type == "physical":
            move_atk = attacker.atk * atk_modifier
            target_def = defender.defe * def_modifier
        else:
            move_atk = attacker.satk * satk_modifier
            target_def = defender.sdef * sdef_modifier

        stab_multiplier = 1.0
        if move_type in attacker.types:
            stab_multiplier = 1.5

        crit_multiplier = 1.0
        if randint(1, 24) == 1:
            crit_multiplier = 2.0

        level = 50
        damage = ((((((2*level)/5)+2)*damage_effect.power*(move_atk/target_def))/50)+2)*crit_multiplier*stab_multiplier*type_multiplier
        return damage
