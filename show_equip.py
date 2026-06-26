"""查看100级装备数值"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game.equipment import Equipment
from src.utils.constants import *

print("=" * 65)
print("  Stage 100 Equipment Stats by Rarity (20 samples avg)")
print("=" * 65)

for slot in [SLOT_MAIN_HAND, SLOT_CHEST, SLOT_ACCESSORY]:
    slot_name = EQUIPMENT_SLOTS[slot]["name"]
    print(f"\n  [{slot_name}]")
    hdr = f"  {'Rarity':>10} | {'HP':>6} | {'ATK':>6} | {'DEF':>6} | {'SPD':>5} | {'Total':>7}"
    print(hdr)
    print("  " + "-" * 55)

    for rarity in RARITY_CONFIG:
        items = []
        for _ in range(200):
            item = Equipment.generate(100, slot)
            if item.rarity == rarity:
                items.append(item)

        if items:
            avg_hp = sum(i.hp for i in items) // len(items)
            avg_atk = sum(i.atk for i in items) // len(items)
            avg_def = sum(i.defense for i in items) // len(items)
            avg_spd = sum(i.speed for i in items) / len(items)
            avg_total = sum(i.total_stats for i in items) / len(items)
            rname = RARITY_CONFIG[rarity]["name"]
            print(f"  {rname:>10} | {avg_hp:>6} | {avg_atk:>6} | {avg_def:>6} | {avg_spd:>5.1f} | {avg_total:>7.1f}")
        else:
            rname = RARITY_CONFIG[rarity]["name"]
            print(f"  {rname:>10} | (no samples)")

# Single full set for each rarity
print("\n" + "=" * 65)
print("  Full Set Preview (weapon + armor + accessory)")
print("=" * 65)

print(f"\n  {'Rarity':>10} | {'HP':>6} | {'ATK':>6} | {'DEF':>6} | {'SPD':>5} | {'Total':>7}")
print("  " + "-" * 55)

for rarity in RARITY_CONFIG:
    total_hp = 0
    total_atk = 0
    total_def = 0
    total_spd = 0.0
    for slot in [SLOT_MAIN_HAND, SLOT_CHEST, SLOT_ACCESSORY]:
        item = Equipment.generate(100, slot)
        # Force rarity
        item.rarity = rarity
        # Recalculate with forced rarity
        base = 5 + 100 * 2.5
        mult = RARITY_CONFIG[rarity]["stat_mult"]
        if slot == SLOT_MAIN_HAND:
            item.atk = int(base * mult)
        elif slot == SLOT_CHEST:
            item.hp = int(base * 3 * mult)
            item.defense = int(base * 0.6 * mult)
        else:
            item.hp = int(base * mult)
            item.atk = int(base * 0.35 * mult)
            item.defense = int(base * 0.35 * mult)
            item.speed = round(mult * 0.35, 1)
        total_hp += item.hp
        total_atk += item.atk
        total_def += item.defense
        total_spd += item.speed
    rname = RARITY_CONFIG[rarity]["name"]
    total = total_hp + total_atk + total_def + total_spd
    print(f"  {rname:>10} | {total_hp:>6} | {total_atk:>6} | {total_def:>6} | {total_spd:>5.1f} | {total:>7.0f}")

# Hero stat comparison
print("\n" + "=" * 65)
print("  Hero Lv.100 Base Stats vs With Full Cosmic Set")
print("=" * 65)

from src.game.hero import Hero

for cls_id, cls_cfg in HERO_CLASSES.items():
    h = Hero("T", cls_id)
    while h.level < 100:
        h.gain_exp(h.exp_to_level - h.exp)
    base_hp = h.max_hp
    base_atk = h.atk
    base_def = h.defense

    # Add full cosmic set
    base = 5 + 100 * 2.5
    mult = 5.5  # cosmic
    from src.game.equipment import Equipment as Eq
    w = Eq("W", SLOT_MAIN_HAND, RARITY_COSMIC, 100, atk=int(base * mult))
    a = Eq("A", SLOT_CHEST, RARITY_COSMIC, 100, hp=int(base*3*mult), defense=int(base*0.6*mult))
    ac = Eq("C", SLOT_ACCESSORY, RARITY_COSMIC, 100, hp=int(base*mult), atk=int(base*0.35*mult), defense=int(base*0.35*mult), speed=round(mult*0.35,1))
    h.equipment[SLOT_MAIN_HAND] = w
    h.equipment[SLOT_CHEST] = a
    h.equipment[SLOT_ACCESSORY] = ac

    print(f"\n  {cls_cfg['name']}:")
    print(f"    Base:  HP={base_hp}  ATK={base_atk}  DEF={base_def}")
    print(f"    Gear:  HP={h.max_hp}  ATK={h.atk}  DEF={h.defense}  SPD={h.speed:.1f}")
    print(f"    Boost: HP +{h.max_hp-base_hp}({h.max_hp/base_hp:.1f}x)  ATK +{h.atk-base_atk}({h.atk/base_atk:.1f}x)  DEF +{h.defense-base_def}({h.defense/base_def:.1f}x)")
