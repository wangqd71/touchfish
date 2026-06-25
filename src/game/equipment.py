"""装备系统 - 7种稀有度"""
import random
from src.utils.constants import *

# ============================================================
# 武器名称
# ============================================================
WEAPON_NAMES = {
    RARITY_COMMON:    ["铁剑", "木弓", "法杖", "短刀", "长枪"],
    RARITY_UNCOMMON:  ["钢刃", "长弓", "橡木杖", "双刃匕首", "战戟"],
    RARITY_RARE:      ["秘银剑", "精灵弓", "符文杖", "淬毒短剑", "龙骨枪"],
    RARITY_EPIC:      ["暗影之刃", "风暴之弓", "奥术之杖", "血牙匕首", "雷霆戟"],
    RARITY_LEGENDARY: ["灭世魔剑", "末日之弓", "混沌法杖", "暗杀者之牙", "神罚之枪"],
    RARITY_MYTHIC:    ["天罚圣剑", "星陨之弓", "虚空法杖", "影之哀伤", "破晓神枪"],
    RARITY_COSMIC:    ["创世之刃", "永恒之弓", "灭世法杖", "虚空之牙", "诸神黄昏"],
}

ARMOR_NAMES = {
    RARITY_COMMON:    ["布甲", "皮甲", "锁甲"],
    RARITY_UNCOMMON:  ["强化皮甲", "链甲", "板甲"],
    RARITY_RARE:      ["秘银甲", "精灵锁甲", "符文板甲"],
    RARITY_EPIC:      ["暗影战甲", "风暴皮甲", "奥术长袍"],
    RARITY_LEGENDARY: ["灭世铠甲", "末日之衣", "混沌法袍"],
    RARITY_MYTHIC:    ["天罚圣铠", "星陨战衣", "虚空法袍"],
    RARITY_COSMIC:    ["创世之铠", "永恒之衣", "灭世法袍"],
}

ACCESSORY_NAMES = {
    RARITY_COMMON:    ["铜戒指", "玻璃项链", "石质护符"],
    RARITY_UNCOMMON:  ["银戒指", "珍珠项链", "铁质护符"],
    RARITY_RARE:      ["金戒指", "宝石项链", "秘银护符"],
    RARITY_EPIC:      ["暗影指环", "风暴吊坠", "奥术徽章"],
    RARITY_LEGENDARY: ["灭世之戒", "末日之心", "混沌之眼"],
    RARITY_MYTHIC:    ["天罚之戒", "星陨之心", "虚空之眼"],
    RARITY_COSMIC:    ["创世之戒", "永恒之心", "灭世之眼"],
}

EQUIP_NAME_MAP = {
    SLOT_WEAPON: WEAPON_NAMES,
    SLOT_ARMOR: ARMOR_NAMES,
    SLOT_ACCESSORY: ACCESSORY_NAMES,
}


class Equipment:
    """装备类"""

    def __init__(self, name, slot, rarity, level, hp=0, atk=0, defense=0, speed=0):
        self.name = name
        self.slot = slot
        self.rarity = rarity
        self.level = level
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.speed = speed

    @property
    def rarity_config(self):
        return RARITY_CONFIG[self.rarity]

    @property
    def rarity_name(self):
        return self.rarity_config["name"]

    @property
    def rarity_color(self):
        return self.rarity_config["color"]

    @property
    def slot_name(self):
        return EQUIPMENT_SLOTS[self.slot]["name"]

    @property
    def slot_icon(self):
        return EQUIPMENT_SLOTS[self.slot]["icon"]

    @property
    def total_stats(self):
        return self.hp + self.atk + self.defense + self.speed

    @property
    def score(self):
        """装备评分 = 属性总和 × 品级倍率"""
        return int(self.total_stats * self.rarity_config["stat_mult"])

    @property
    def sell_price(self):
        """售卖价格"""
        return max(1, int(self.total_stats * self.rarity_config["stat_mult"] * 0.5))

    def get_stat_text(self):
        parts = []
        if self.hp > 0:
            parts.append(f"HP+{self.hp}")
        if self.atk > 0:
            parts.append(f"攻击+{self.atk}")
        if self.defense > 0:
            parts.append(f"防御+{self.defense}")
        if self.speed > 0:
            parts.append(f"速度+{self.speed:.1f}")
        return " ".join(parts)

    def get_save_data(self):
        return {
            "name": self.name,
            "slot": self.slot,
            "rarity": self.rarity,
            "level": self.level,
            "hp": self.hp,
            "atk": self.atk,
            "defense": self.defense,
            "speed": self.speed,
        }

    @classmethod
    def from_save_data(cls, data):
        return cls(
            data["name"], data["slot"], data["rarity"], data["level"],
            data.get("hp", 0), data.get("atk", 0),
            data.get("defense", 0), data.get("speed", 0)
        )

    @classmethod
    def generate(cls, stage, slot=None):
        """根据关卡生成随机装备"""
        rarity = cls._random_rarity()
        rarity_mult = RARITY_CONFIG[rarity]["stat_mult"]

        if slot is None:
            slot = random.choice([SLOT_WEAPON, SLOT_ARMOR, SLOT_ACCESSORY])

        names = EQUIP_NAME_MAP.get(slot, WEAPON_NAMES)
        name = random.choice(names.get(rarity, ["未知装备"]))

        level = stage
        base_stat = 5 + stage * 2.5

        hp = 0
        atk = 0
        defense = 0
        speed = 0

        if slot == SLOT_WEAPON:
            atk = int(base_stat * rarity_mult * random.uniform(0.85, 1.15))
        elif slot == SLOT_ARMOR:
            hp = int(base_stat * 3 * rarity_mult * random.uniform(0.85, 1.15))
            defense = int(base_stat * 0.6 * rarity_mult * random.uniform(0.85, 1.15))
        else:
            hp = int(base_stat * rarity_mult * random.uniform(0.85, 1.15))
            atk = int(base_stat * 0.35 * rarity_mult * random.uniform(0.85, 1.15))
            defense = int(base_stat * 0.35 * rarity_mult * random.uniform(0.85, 1.15))
            speed = round(rarity_mult * random.uniform(0.1, 0.6), 1)

        return cls(name, slot, rarity, level, hp, atk, defense, speed)

    @staticmethod
    def _random_rarity():
        rarities = list(RARITY_CONFIG.keys())
        weights = [RARITY_CONFIG[r]["drop_weight"] for r in rarities]
        return random.choices(rarities, weights=weights, k=1)[0]
