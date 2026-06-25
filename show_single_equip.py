"""展示单件装备详情"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game.equipment import Equipment
from src.utils.constants import *

random.seed(2026)

print("=" * 60)
print("  Single Equipment Showcase - Stage 100")
print("=" * 60)

for rarity in [RARITY_COMMON, RARITY_RARE, RARITY_LEGENDARY, RARITY_COSMIC]:
    rname = RARITY_CONFIG[rarity]["name"]
    mult = RARITY_CONFIG[rarity]["stat_mult"]

    print(f"\n  {'=' * 50}")
    print(f"  [{rname}] (x{mult})")
    print(f"  {'=' * 50}")

    for slot in [SLOT_WEAPON, SLOT_ARMOR, SLOT_ACCESSORY]:
        item = Equipment.generate(100, slot)
        sname = EQUIPMENT_SLOTS[slot]["name"]
        print(f"\n  {item.name}")
        print(f"  {sname} | Lv.{item.level}")
        if item.hp > 0:
            print(f"    HP  +{item.hp}")
        if item.atk > 0:
            print(f"    ATK +{item.atk}")
        if item.defense > 0:
            print(f"    DEF +{item.defense}")
        if item.speed > 0:
            print(f"    SPD +{item.speed:.1f}")
        print(f"    Total: {item.total_stats:.0f}")
