"""战斗系统 - 使用英雄技能加成属性"""
import random
from src.utils.constants import *


class CombatResult:
    def __init__(self):
        self.victory = False
        self.damage_dealt = 0
        self.damage_taken = 0
        self.exp_gained = 0
        self.gold_gained = 0
        self.loot = None
        self.level_ups = 0
        self.crit_hits = 0
        self.dodges = 0


class CombatEngine:

    @staticmethod
    def calculate_damage(attacker_atk, defender_def, is_crit=False, crit_mult=CRIT_DAMAGE_MULT, dmg_mult=1.0):
        base_damage = max(1, attacker_atk - defender_def * 0.5)
        variance = random.uniform(0.9, 1.1)
        damage = base_damage * variance * dmg_mult
        if is_crit:
            damage *= crit_mult
        return max(1, int(damage))

    @staticmethod
    def battle(hero, monster):
        result = CombatResult()

        hero_first = hero.speed >= monster.atk * 0.1

        while hero.is_alive and monster.is_alive:
            if hero_first:
                # 英雄攻击
                if random.random() < hero.dodge_rate:
                    result.dodges += 1
                else:
                    is_crit = random.random() < hero.crit_rate
                    if is_crit:
                        result.crit_hits += 1
                    damage = CombatEngine.calculate_damage(
                        hero.atk, monster.defense, is_crit,
                        hero.crit_damage_mult, hero.dmg_mult
                    )
                    actual = monster.take_damage(damage)
                    result.damage_dealt += actual

                # 怪物攻击
                if monster.is_alive:
                    if random.random() < hero.dodge_rate:
                        result.dodges += 1
                    else:
                        damage = CombatEngine.calculate_damage(monster.atk, hero.defense)
                        actual = hero.take_damage(damage)
                        result.damage_taken += actual
            else:
                # 怪物先手
                if random.random() < hero.dodge_rate:
                    result.dodges += 1
                else:
                    damage = CombatEngine.calculate_damage(monster.atk, hero.defense)
                    actual = hero.take_damage(damage)
                    result.damage_taken += actual

                if hero.is_alive:
                    if random.random() < hero.dodge_rate:
                        result.dodges += 1
                    else:
                        is_crit = random.random() < hero.crit_rate
                        if is_crit:
                            result.crit_hits += 1
                        damage = CombatEngine.calculate_damage(
                            hero.atk, monster.defense, is_crit,
                            hero.crit_damage_mult, hero.dmg_mult
                        )
                        actual = monster.take_damage(damage)
                        result.damage_dealt += actual

        if hero.is_alive:
            result.victory = True
            result.exp_gained = 20 + monster.level * 5
            result.gold_gained = GOLD_BASE + monster.level * GOLD_GROWTH
            result.gold_gained = int(result.gold_gained * random.uniform(0.8, 1.2))

            hero.gain_gold(result.gold_gained)
            result.level_ups = hero.gain_exp(result.exp_gained)
            hero.total_kills += 1
        else:
            result.victory = False

        return result
