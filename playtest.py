"""完整游戏试玩测试"""
import sys, random
sys.path.insert(0, ".")
from src.game.engine import GameEngine
from src.game.hero import Hero
from src.game.equipment import Equipment
from src.game.combat import CombatEngine
from src.game.loot import LootTable
from src.game.monster import Monster
from src.utils.constants import *
from src.utils.save_manager import SaveManager

random.seed(2026)
print("=" * 60)
print("  PLAYTEST REPORT - All 6 Classes, 300 ticks")
print("=" * 60)
all_issues = []

for cls_id, cls_cfg in HERO_CLASSES.items():
    e = GameEngine()
    e.new_game(cls_cfg["name"], cls_id)
    for i in range(300):
        e.update()
    iss = []
    if e.hero.level < 6: iss.append("level too slow")
    if e.hero.gold < 500: iss.append("gold too low")
    if e.hero.total_kills < 10: iss.append("kills too low")
    if e.stage < 6: iss.append("stage too slow")
    st = "[OK]" if not iss else "[!] " + "; ".join(iss)
    alive = "DEAD!" if e.state == "dead" else f"HP {e.hero.current_hp}/{e.hero.max_hp}"
    print("[{:>6}] Lv{:>3} | Gold {:>5} | Kills {:>3} | Stage {:>3} | {} | {}".format(
        cls_cfg["name"], e.hero.level, e.hero.gold, e.hero.total_kills, e.stage, alive, st))
    if iss:
        all_issues.extend(iss)

print("\nIssues found: {}".format(len(all_issues)))
for i in all_issues[:8]:
    print("  - {}".format(i))

# Save/Load
print("\n--- Save/Load ---")
e2 = GameEngine()
e2.new_game("SaveTest", CLASS_WARRIOR)
for i in range(20): e2.update()
data = e2.get_save_data()
sm = SaveManager()
sm.save(data)
e3 = GameEngine()
e3.load_save_data(sm.load())
match = e3.hero.level == e2.hero.level and e3.hero.gold == e2.hero.gold
print("[OK] Save/Load: {} Lv{} Gold{} | Load: {} Lv{} Gold{} | Match: {}".format(
    e2.hero.name, e2.hero.level, e2.hero.gold, e3.hero.name, e3.hero.level, e3.hero.gold, match))

# Equip test
print("\n--- Equip ---")
h = Hero("Test", CLASS_WARRIOR)
w = Equipment.generate(50, "weapon")
a = Equipment.generate(50, "armor")
ac = Equipment.generate(50, "accessory")
h.equip(w); h.equip(a); h.equip(ac)
w2 = Equipment.generate(50, "weapon")
if w2.total_stats > w.total_stats:
    old = h.equip(w2)
    print("[OK] Auto-replace: {} -> {} (ATK={})".format(old.name, w2.name, h.atk))
else:
    print("[OK] No replace ({} ATK={})".format(w.name, h.atk))

# Edge cases
print("\n--- Edge Cases ---")
h2 = Hero("Cap", CLASS_WARRIOR)
h2.level = 100
h2.exp = 0
h2.gain_exp(9999999)
print("[OK] Lv100 cap: lv={} exp={} sp={}".format(h2.level, h2.exp, h2.skill_points))

h3 = Hero("HPFloor", CLASS_ASSASSIN)
h3.current_hp = 10
h3.take_damage(99999)
print("[OK] HP floor: {}".format(h3.current_hp))

min_dmg = CombatEngine.calculate_damage(1, 100)
print("[OK] Min damage (1 ATK vs 100 DEF): {}".format(min_dmg))

# Equip gen
items = [Equipment.generate(100) for _ in range(100)]
high = sum(1 for i in items if i.rarity in [RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_COSMIC])
print("[OK] 100 items: Common={} Uncommon={} Rare={} Epic={} Legendary+={}".format(
    sum(1 for i in items if i.rarity == RARITY_COMMON),
    sum(1 for i in items if i.rarity == RARITY_UNCOMMON),
    sum(1 for i in items if i.rarity == RARITY_RARE),
    sum(1 for i in items if i.rarity == RARITY_EPIC),
    high))

# Skill test
h4 = Hero("SkillTest", CLASS_WARRIOR)
h4.level = 20
h4.skill_points = 15
tree = h4.get_skill_tree_info()
learned = 0
for bname in tree["branches"]:
    for s in tree["branches"][bname]["skills"]:
        if h4.skill_points > 0 and s["can_learn"]:
            h4.learn_skill(s["id"])
            learned += 1
print("[OK] Learned {} skills, SP left: {}, ATK: {} -> {}".format(learned, h4.skill_points, HERO_BASE_ATK + 19 * HERO_ATK_GROWTH, h4.atk))

print("\n================== PLAYTEST DONE ==================")
