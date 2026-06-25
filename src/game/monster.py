"""怪物系统 - 难度倍率"""
import random
from src.utils.constants import *


# 怪物模板（按章节）
MONSTER_TEMPLATES = {
    CHAPTER_1: [
        {"name": "暗影史莱姆", "hp_mult": 1.0, "atk_mult": 1.0, "def_mult": 0.8},
        {"name": "骷髅兵",     "hp_mult": 1.2, "atk_mult": 1.1, "def_mult": 1.0},
        {"name": "蝙蝠",       "hp_mult": 0.7, "atk_mult": 0.9, "def_mult": 0.6},
        {"name": "狼人",       "hp_mult": 1.3, "atk_mult": 1.2, "def_mult": 0.9},
        {"name": "暗影骑士",   "hp_mult": 1.5, "atk_mult": 1.3, "def_mult": 1.3},
    ],
    CHAPTER_2: [
        {"name": "岩石傀儡",   "hp_mult": 1.6, "atk_mult": 1.3, "def_mult": 1.6},
        {"name": "毒蝎",       "hp_mult": 1.2, "atk_mult": 1.5, "def_mult": 1.0},
        {"name": "洞穴巨蛛",   "hp_mult": 1.3, "atk_mult": 1.4, "def_mult": 1.2},
        {"name": "矮人矿工",   "hp_mult": 1.4, "atk_mult": 1.4, "def_mult": 1.3},
        {"name": "水晶魔像",   "hp_mult": 2.0, "atk_mult": 1.6, "def_mult": 2.0},
    ],
    CHAPTER_3: [
        {"name": "恶魔侍卫",   "hp_mult": 2.2, "atk_mult": 1.8, "def_mult": 1.6},
        {"name": "堕落天使",   "hp_mult": 2.0, "atk_mult": 2.0, "def_mult": 1.4},
        {"name": "死灵法师",   "hp_mult": 1.6, "atk_mult": 2.2, "def_mult": 1.2},
        {"name": "地狱犬",     "hp_mult": 1.8, "atk_mult": 1.9, "def_mult": 1.5},
        {"name": "魔王",       "hp_mult": 3.0, "atk_mult": 2.5, "def_mult": 2.0},
    ],
}


class Monster:

    def __init__(self, name, level, hp, atk, defense):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.current_hp = hp
        self.atk = atk
        self.defense = defense

    @property
    def hp_percent(self):
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0

    @property
    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, damage):
        actual = max(1, int(damage))
        self.current_hp = max(0, self.current_hp - actual)
        return actual

    @classmethod
    def generate(cls, stage, difficulty=DIFF_NORMAL):
        """根据关卡和难度生成怪物，关卡=怪物等级"""
        chapter = cls._get_chapter_for_stage(stage)
        templates = MONSTER_TEMPLATES.get(chapter, MONSTER_TEMPLATES[CHAPTER_1])
        template = random.choice(templates)

        diff_mult = DIFFICULTIES[difficulty]["mult"]
        monster_level = stage

        base_hp = 40 + stage * 12
        base_atk = 4 + stage * 5
        base_def = 2 + stage * 1.5

        hp = int(base_hp * template["hp_mult"] * diff_mult)
        atk = int(base_atk * template["atk_mult"] * diff_mult)
        defense = int(base_def * template["def_mult"] * diff_mult)

        return cls(template["name"], monster_level, hp, atk, defense)

    @classmethod
    def generate_boss(cls, stage, difficulty=DIFF_NORMAL):
        chapter = cls._get_chapter_for_stage(stage)
        templates = MONSTER_TEMPLATES.get(chapter, MONSTER_TEMPLATES[CHAPTER_1])
        boss_template = templates[-1]

        diff_mult = DIFFICULTIES[difficulty]["mult"]
        monster_level = stage + 2

        base_hp = 80 + stage * 12
        base_atk = 6 + stage * 3.5
        base_def = 4 + stage * 1.5

        hp = int(base_hp * min(boss_template["hp_mult"], 2.0) * diff_mult)
        atk = int(base_atk * min(boss_template["atk_mult"], 1.8) * diff_mult)
        defense = int(base_def * min(boss_template["def_mult"], 1.8) * diff_mult)

        return cls(boss_template["name"] + " [{}]".format(DIFFICULTIES[difficulty]["name"]),
                   monster_level, hp, atk, defense)

    @staticmethod
    def _get_chapter_for_stage(stage):
        idx = ((stage - 1) // 10) % 3
        chapters = [CHAPTER_1, CHAPTER_2, CHAPTER_3]
        return chapters[idx]
