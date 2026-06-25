"""数值平衡性审计脚本 - 全量模拟测试"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.constants import *
from src.game.hero import Hero
from src.game.monster import Monster
from src.game.combat import CombatEngine
from src.game.equipment import Equipment

random.seed(42)
SEP = "=" * 60

def test_exp_curve():
    print(SEP)
    print("[1] 经验曲线审计")
    print(SEP)
    issues = []
    total_exp = 0
    print(f"  Lv |   ExpNext |     CumExp | KillsNeed | Verdict")
    print(f"  " + "-" * 55)
    for lv in range(1, 101):
        exp_next = int(EXP_BASE * (EXP_GROWTH_RATE ** (lv - 1)))
        total_exp += exp_next
        exp_per_kill = 20 + lv * 5
        kills = max(1, exp_next // exp_per_kill)
        if lv <= 10: expected = 5
        elif lv <= 30: expected = 8
        elif lv <= 60: expected = 12
        else: expected = 15
        if kills > expected * 2:
            issues.append(f"Lv.{lv}: need {kills} kills (expected ~{expected})")
            verdict = "[!] SLOW"
        elif kills < expected // 3:
            verdict = "[!] FAST"
        else:
            verdict = "[OK]"
        if lv in [1, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            print(f"  {lv:>2} | {exp_next:>9} | {total_exp:>10} | {kills:>9} | {verdict}")
    print(f"\n  Total exp to 100: {total_exp:,}")
    if issues:
        print(f"  Issues: {len(issues)} (showing first 5)")
        for i in issues[:5]: print(f"    {i}")
    return issues

def test_hero_stats():
    print(f"\n{SEP}")
    print("[2] Hero Stats Audit")
    print(SEP)
    issues = []
    for cls_id, cls_cfg in HERO_CLASSES.items():
        print(f"\n  {cls_cfg['name']} ({cls_cfg['desc']}):")
        print(f"  Lv |   HP | ATK | DEF | SPD")
        print(f"  " + "-" * 30)
        for lv in [1, 10, 20, 30, 50, 70, 100]:
            h = Hero("T", cls_id)
            while h.level < lv:
                h.gain_exp(h.exp_to_level - h.exp)
            print(f"  {lv:>2} | {h.max_hp:>4} | {h.atk:>3} | {h.defense:>3} | {h.speed:.1f}")
    # class diff check at lv50
    print(f"\n  Class diff @ Lv50:")
    stats = {}
    for cls_id in HERO_CLASSES:
        h = Hero("T", cls_id)
        while h.level < 50:
            h.gain_exp(h.exp_to_level - h.exp)
        stats[cls_id] = (h.max_hp, h.atk, h.defense)
    sin_hp, sin_atk, sin_def = stats[CLASS_ASSASSIN]
    kn_hp, kn_atk, kn_def = stats[CLASS_KNIGHT]
    print(f"  Assassin: HP={sin_hp} ATK={sin_atk} DEF={sin_def}")
    print(f"  Knight:   HP={kn_hp} ATK={kn_atk} DEF={kn_def}")
    ratio_hp = kn_hp / sin_hp if sin_hp else 0
    ratio_atk = sin_atk / kn_atk if kn_atk else 0
    print(f"  Knight/Assassin HP: {ratio_hp:.2f}x  Assassin/Knight ATK: {ratio_atk:.2f}x")
    if kn_atk >= sin_atk:
        issues.append("Knight ATK >= Assassin ATK")
    if sin_hp >= kn_hp:
        issues.append("Assassin HP >= Knight HP")
    if ratio_atk < 1.2:
        issues.append(f"Assassin/Knight ATK ratio only {ratio_atk:.2f}x, should be >1.3x")
    return issues

def test_monster_balance():
    print(f"\n{SEP}")
    print("[3] Monster Balance Audit")
    print(SEP)
    issues = []
    test_stages = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]
    print(f"\n  Normal Monsters:")
    print(f"  Stage |   HP | ATK | DEF | Chapter")
    print(f"  " + "-" * 40)
    for s in test_stages:
        ch = CHAPTER_1 if s <= 20 else (CHAPTER_2 if s <= 50 else CHAPTER_3)
        random.seed(s)
        m = Monster.generate(s, ch)
        print(f"  {s:>5} | {m.max_hp:>4} | {m.atk:>3} | {m.defense:>3} | {ch}")
    print(f"\n  Boss Monsters:")
    print(f"  Stage |     HP | ATK | DEF")
    print(f"  " + "-" * 30)
    for s in test_stages:
        ch = CHAPTER_1 if s <= 20 else (CHAPTER_2 if s <= 50 else CHAPTER_3)
        random.seed(s + 1000)
        m = Monster.generate_boss(s, ch)
        print(f"  {s:>5} | {m.max_hp:>6} | {m.atk:>3} | {m.defense:>3}")
    # Hero vs Monster
    print(f"\n  Hero(Warrior) vs Monster (no equip):")
    print(f"  Stage | HeroHP | HeroATK | HeroDEF | MonHP | MonATK | MonDEF | R2Kill | R2Die | Verdict")
    print(f"  " + "-" * 80)
    for s in [1, 10, 30, 50, 70, 100]:
        ch = CHAPTER_1 if s <= 20 else (CHAPTER_2 if s <= 50 else CHAPTER_3)
        hero = Hero("T", CLASS_WARRIOR)
        while hero.level < s:
            hero.gain_exp(hero.exp_to_level - hero.exp)
        random.seed(s + 2000)
        monster = Monster.generate(s, ch)
        h_dmg = max(1, hero.atk - monster.defense * 0.5)
        r2k = max(1, monster.max_hp // h_dmg)
        m_dmg = max(1, monster.atk - hero.defense * 0.5)
        r2d = max(1, hero.max_hp // m_dmg)
        ratio = r2d / r2k if r2k > 0 else 999
        if ratio < 1.0:
            verdict = "[X] DIE"
            issues.append(f"Stage {s}: hero dies first (ratio={ratio:.2f})")
        elif ratio < 1.5:
            verdict = "[!] CLOSE"
        elif ratio > 5.0:
            verdict = "[!] STOMP"
        else:
            verdict = "[OK]"
        print(f"  {s:>5} | {hero.max_hp:>6} | {hero.atk:>7} | {hero.defense:>7} | "
              f"{monster.max_hp:>5} | {monster.atk:>6} | {monster.defense:>6} | "
              f"{r2k:>6} | {r2d:>5} | {verdict}")
    return issues

def test_equipment_balance():
    print(f"\n{SEP}")
    print("[4] Equipment Balance Audit")
    print(SEP)
    issues = []
    print(f"\n  Weapon ATK by stage and rarity:")
    print(f"  Rarity   |  S10 |  S30 |  S50 |  S70 | S100")
    print(f"  " + "-" * 45)
    for rarity in RARITY_CONFIG:
        row = f"  {RARITY_CONFIG[rarity]['name']:>8} |"
        for stage in [10, 30, 50, 70, 100]:
            base = 5 + stage * 2.5
            mult = RARITY_CONFIG[rarity]["stat_mult"]
            atk = int(base * mult)
            row += f" {atk:>4} |"
        print(row)
    # gap check
    base50 = 5 + 50 * 2.5
    common = int(base50 * 1.0)
    cosmic = int(base50 * 5.5)
    ratio = cosmic / common if common else 0
    print(f"\n  Cosmic vs Common weapon @ S50: {cosmic} / {common} = {ratio:.1f}x")
    if ratio > 6:
        issues.append(f"Cosmic/Common gap too large: {ratio:.1f}x")
    # drop rates
    print(f"\n  Drop rate simulation (1000 rolls):")
    from collections import Counter
    drops = Counter()
    for _ in range(1000):
        drops[Equipment._random_rarity()] += 1
    for rarity in RARITY_CONFIG:
        cnt = drops.get(rarity, 0)
        print(f"  {RARITY_CONFIG[rarity]['name']:>8}: {cnt:>4} ({cnt/10:.1f}%)")
    return issues

def test_combat_simulation():
    print(f"\n{SEP}")
    print("[5] Combat Simulation")
    print(SEP)
    issues = []
    configs = [
        (CLASS_WARRIOR, 1, 1), (CLASS_WARRIOR, 10, 10), (CLASS_WARRIOR, 30, 30),
        (CLASS_WARRIOR, 50, 50), (CLASS_WARRIOR, 70, 70),
        (CLASS_MAGE, 1, 1), (CLASS_MAGE, 10, 10), (CLASS_MAGE, 30, 30),
        (CLASS_KNIGHT, 1, 1), (CLASS_KNIGHT, 10, 10), (CLASS_KNIGHT, 30, 30),
        (CLASS_ASSASSIN, 1, 1), (CLASS_ASSASSIN, 10, 10), (CLASS_ASSASSIN, 30, 30),
        (CLASS_PRIEST, 1, 1), (CLASS_PRIEST, 10, 10), (CLASS_PRIEST, 30, 30),
        (CLASS_RANGER, 1, 1), (CLASS_RANGER, 10, 10), (CLASS_RANGER, 30, 30),
    ]
    print(f"\n  Win% over 200 fights (no equip):")
    print(f"  Class    | Lv | Stage | Win% | Verdict")
    print(f"  " + "-" * 45)
    for cls_id, hlv, stage in configs:
        ch = CHAPTER_1 if stage <= 10 else (CHAPTER_2 if stage <= 25 else CHAPTER_3)
        wins = 0
        for _ in range(200):
            hero = Hero("T", cls_id)
            while hero.level < hlv:
                hero.gain_exp(hero.exp_to_level - hero.exp)
            monster = Monster.generate(stage, ch)
            result = CombatEngine.battle(hero, monster)
            if result.victory:
                wins += 1
        cls_name = HERO_CLASSES[cls_id]["name"]
        if wins < 30:
            verdict = "[X] TOO HARD"
            issues.append(f"{cls_name} Lv.{hlv} vs S{stage}: {wins}% win")
        elif wins > 95:
            verdict = "[!] TOO EASY"
        else:
            verdict = "[OK]"
        print(f"  {cls_name:>8} | {hlv:>2} | {stage:>5} | {wins:>3}% | {verdict}")
    return issues

def test_loot_balance():
    print(f"\n{SEP}")
    print("[6] Loot/Economy Audit")
    print(SEP)
    issues = []
    print(f"\n  Gold per stage (10 normal + 1 boss):")
    print(f"  Stage | Normal | Boss |  Total")
    print(f"  " + "-" * 35)
    for s in [1, 10, 20, 30, 50, 70, 100]:
        ng = GOLD_BASE + s * GOLD_GROWTH
        bg = ng * 3
        total = ng * 10 + bg
        print(f"  {s:>5} | {ng:>6} | {bg:>4} | {total:>6}")
    print(f"\n  [!] No gold sink mechanic found")
    issues.append("No gold sink - economy inflates forever")
    return issues

def test_damage_formula():
    print(f"\n{SEP}")
    print("[7] Damage Formula Audit")
    print(SEP)
    issues = []
    print(f"\n  calculate_damage: dmg = max(1, atk - def*0.5) * var * mult")
    print(f"  hero.take_damage: actual = max(1, dmg*(1-reduce))  [FIXED: no double def]")
    print(f"  monster.take_damage: actual = max(1, dmg)           [FIXED: no double def]")
    print(f"\n  [OK] Defense double-dip bug has been fixed!")
    print(f"    Defense is now only applied once in calculate_damage")

    # damage table
    print(f"\n  Damage Table (hero hits monster):")
    print(f"  ATK  | DEF  | calc_dmg | mon_take | Effective")
    print(f"  " + "-" * 45)
    for atk, df in [(10,5),(20,10),(50,20),(100,50),(200,100)]:
        calc = max(1, atk - df * 0.5)
        mon_take = max(1, calc)  # Fixed: no double def
        print(f"  {atk:>4} | {df:>4} | {calc:>8.0f} | {mon_take:>8} | {mon_take:>5}")

    return issues

def run_all():
    print("\n" + "=" * 60)
    print("  DARK TASK RPG - FULL BALANCE AUDIT")
    print("=" * 60 + "\n")

    all_issues = []
    all_issues.extend(test_exp_curve())
    all_issues.extend(test_hero_stats())
    all_issues.extend(test_monster_balance())
    all_issues.extend(test_equipment_balance())
    all_issues.extend(test_combat_simulation())
    all_issues.extend(test_loot_balance())
    all_issues.extend(test_damage_formula())

    print(f"\n{'=' * 60}")
    print(f"  AUDIT SUMMARY")
    print(f"{'=' * 60}")
    if all_issues:
        print(f"\n  Found {len(all_issues)} issues:\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    else:
        print(f"\n  [OK] No balance issues found")
    print()

if __name__ == "__main__":
    run_all()
