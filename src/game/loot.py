"""掉落系统"""
import random
from src.utils.constants import *
from src.game.equipment import Equipment


class LootResult:
    """掉落结果"""
    def __init__(self):
        self.gold = 0
        self.exp = 0
        self.items = []
        self.is_boss = False


class LootTable:
    """掉落表"""

    @staticmethod
    def roll(stage, is_boss=False, chapter=CHAPTER_1):
        """根据关卡和是否Boss计算掉落"""
        result = LootResult()
        result.is_boss = is_boss

        # 基础奖励
        result.gold = GOLD_BASE + stage * GOLD_GROWTH
        result.gold = int(result.gold * random.uniform(0.8, 1.2))

        if is_boss:
            result.gold *= 3
            result.exp = (20 + stage * 5) * 2
        else:
            result.exp = 20 + stage * 5

        # 装备掉落
        drop_chance = DROP_CHANCE
        if is_boss:
            drop_chance = 0.8  # Boss 80%掉装备

        if random.random() < drop_chance:
            # 随机装备部位
            slot = random.choice([SLOT_WEAPON, SLOT_ARMOR, SLOT_ACCESSORY])
            item = Equipment.generate(stage, slot)
            result.items.append(item)

        # Boss额外掉落
        if is_boss and random.random() < 0.3:
            slot = random.choice([SLOT_WEAPON, SLOT_ARMOR, SLOT_ACCESSORY])
            item = Equipment.generate(stage + 5, slot)
            result.items.append(item)

        return result
