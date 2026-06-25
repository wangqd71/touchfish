"""全量前端交互测试 - 模拟所有点击路径"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from src.ui.main_window import MainWindow, SkillTreeDialog, InventoryDialog, NewGameDialog
from src.game.engine import GameEngine
from src.game.hero import Hero
from src.game.equipment import Equipment
from src.utils.constants import *
import random

app = QApplication(sys.argv)

PASS = 0
FAIL = 0
results = []

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        results.append(("OK", name))
    except Exception as e:
        FAIL += 1
        results.append(("FAIL", name + " -> " + str(e)))

# ===== 1. Main Window =====
def test_main_window_create():
    w = MainWindow()
    assert w.windowTitle() != ""
    assert w.width() > 0
    w.close()

def test_main_window_update_ui():
    w = MainWindow()
    e = GameEngine()
    e.new_game("TestHero", CLASS_WARRIOR)
    w.engine = e
    w._update_ui()
    assert w.lbl_name.text() != ""
    assert w.lbl_hp.text() != ""
    assert w.lbl_exp.text() != ""
    w.close()

def test_main_window_update_ui_with_equipment():
    w = MainWindow()
    e = GameEngine()
    e.new_game("TestHero", CLASS_WARRIOR)
    for i in range(5):
        item = Equipment.generate(10, random.choice([SLOT_WEAPON, SLOT_ARMOR, SLOT_ACCESSORY]))
        e.hero.add_to_inventory(item)
    w.engine = e
    w._update_ui()
    assert len(e.hero.inventory) == 5
    w.close()

test("MainWindow create", test_main_window_create)
test("MainWindow update_ui", test_main_window_update_ui)
test("MainWindow update_ui with equipment", test_main_window_update_ui_with_equipment)

# ===== 2. New Game Dialog =====
def test_new_game_dialog():
    dlg = NewGameDialog()
    dlg.show()
    data = dlg.get_data()
    assert data["name"] != ""
    assert data["hero_class"] in HERO_CLASSES
    dlg.close()

test("NewGameDialog", test_new_game_dialog)

# ===== 3. Skill Tree Dialog =====
def test_skill_tree_create():
    h = Hero("Test", CLASS_WARRIOR)
    h.skill_points = 10
    dlg = SkillTreeDialog(h)
    dlg.show()
    assert dlg.layout().count() >= 3
    dlg.close()

def test_skill_tree_learn():
    h = Hero("Test", CLASS_WARRIOR)
    h.skill_points = 10
    tree = h.get_skill_tree_info()
    for bname in tree["branches"]:
        for s in tree["branches"][bname]["skills"]:
            if s["can_learn"] and h.skill_points > 0:
                h.learn_skill(s["id"])
    assert len(h.learned_skills) > 0
    assert h.skill_points < 10

def test_skill_tree_learn_then_save():
    h = Hero("Test", CLASS_WARRIOR)
    h.skill_points = 5
    tree = h.get_skill_tree_info()
    for bname in tree["branches"]:
        for s in tree["branches"][bname]["skills"]:
            if s["can_learn"] and h.skill_points > 0:
                h.learn_skill(s["id"])
    learned_before = dict(h.learned_skills)
    sp_before = h.skill_points
    data = h.get_save_data()
    h2 = Hero.from_save_data(data)
    assert h2.learned_skills == learned_before
    assert h2.skill_points == sp_before

test("SkillTree create", test_skill_tree_create)
test("SkillTree learn", test_skill_tree_learn)
test("SkillTree learn then save/load", test_skill_tree_learn_then_save)

# ===== 4. Inventory Dialog =====
def test_inventory_create():
    h = Hero("Test", CLASS_WARRIOR)
    for i in range(5):
        item = Equipment.generate(10, random.choice([SLOT_WEAPON, SLOT_ARMOR, SLOT_ACCESSORY]))
        h.add_to_inventory(item)
    dlg = InventoryDialog(h)
    dlg.show()
    assert dlg.layout().count() >= 4
    dlg.close()

def test_inventory_sell():
    h = Hero("Test", CLASS_WARRIOR)
    item = Equipment.generate(10, SLOT_WEAPON)
    h.add_to_inventory(item)
    gold_before = h.gold
    price = h.sell_from_inventory(0)
    assert price > 0
    assert h.gold == gold_before + price
    assert len(h.inventory) == 0

def test_inventory_equip():
    h = Hero("Test", CLASS_WARRIOR)
    item = Equipment.generate(10, SLOT_WEAPON)
    h.add_to_inventory(item)
    assert h.equipment["weapon"] is None
    h.equip_from_inventory(0)
    assert h.equipment["weapon"] is not None
    assert len(h.inventory) == 0

def test_inventory_sell_empty():
    h = Hero("Test", CLASS_WARRIOR)
    price = h.sell_from_inventory(0)
    assert price == 0
    assert h.gold == 0

def test_inventory_sell_out_of_range():
    h = Hero("Test", CLASS_WARRIOR)
    price = h.sell_from_inventory(999)
    assert price == 0

def test_inventory_equip_out_of_range():
    h = Hero("Test", CLASS_WARRIOR)
    result = h.equip_from_inventory(999)
    assert result is None

test("Inventory create", test_inventory_create)
test("Inventory sell", test_inventory_sell)
test("Inventory equip", test_inventory_equip)
test("Inventory sell empty", test_inventory_sell_empty)
test("Inventory sell out of range", test_inventory_sell_out_of_range)
test("Inventory equip out of range", test_inventory_equip_out_of_range)

# ===== 5. Engine Game Flow =====
def test_engine_new_game():
    e = GameEngine()
    e.new_game("Hero", CLASS_MAGE)
    assert e.hero is not None
    assert e.stage == 1
    assert e.difficulty == DIFF_NORMAL

def test_engine_combat():
    e = GameEngine()
    e.new_game("Hero", CLASS_WARRIOR)
    e.update()
    assert e.hero.total_kills >= 0
    assert e.hero.gold >= 0

def test_engine_300_ticks():
    e = GameEngine()
    e.new_game("Hero", CLASS_WARRIOR)
    for _ in range(300):
        e.update()
    assert e.hero.level >= 1
    assert e.stage >= 1

def test_engine_resurrect():
    e = GameEngine()
    e.new_game("Hero", CLASS_WARRIOR)
    e.hero.current_hp = 0
    e.state = "dead"
    gold_before = e.hero.gold
    e.resurrect()
    assert e.hero.current_hp == e.hero.max_hp
    assert e.state != "dead"

def test_engine_save_load():
    e = GameEngine()
    e.new_game("Hero", CLASS_WARRIOR)
    for _ in range(10):
        e.update()
    data = e.get_save_data()
    e2 = GameEngine()
    e2.load_save_data(data)
    assert e2.hero.name == e.hero.name
    assert e2.hero.level == e.hero.level
    assert e2.hero.gold == e.hero.gold
    assert e2.stage == e.stage

test("Engine new_game", test_engine_new_game)
test("Engine combat", test_engine_combat)
test("Engine 300 ticks", test_engine_300_ticks)
test("Engine resurrect", test_engine_resurrect)
test("Engine save/load", test_engine_save_load)

# ===== 6. All 6 Classes =====
for cls_id in [CLASS_WARRIOR, CLASS_MAGE, CLASS_RANGER, CLASS_KNIGHT, CLASS_PRIEST, CLASS_ASSASSIN]:
    def make_test(cid=cls_id):
        def t():
            e = GameEngine()
            e.new_game("Test", cid)
            for _ in range(100):
                e.update()
            assert e.hero.level >= 1
        return t
    test("Class " + HERO_CLASSES[cls_id]["name"], make_test(cls_id))

# ===== 7. Edge Cases =====
def test_hero_level_cap():
    h = Hero("Test", CLASS_WARRIOR)
    h.level = MAX_LEVEL
    h.exp = 0
    h.gain_exp(9999999)
    assert h.level == MAX_LEVEL
    assert h.exp == 0

def test_hero_hp_floor():
    h = Hero("Test", CLASS_WARRIOR)
    h.take_damage(999999)
    assert h.current_hp == 0

def test_hero_hp_max_cap():
    h = Hero("Test", CLASS_WARRIOR)
    h.current_hp = h.max_hp
    h.heal(999999)
    assert h.current_hp == h.max_hp

def test_min_damage():
    from src.game.combat import CombatEngine
    dmg = CombatEngine.calculate_damage(1, 1000)
    assert dmg >= 1

test("Hero level cap", test_hero_level_cap)
test("Hero HP floor", test_hero_hp_floor)
test("Hero HP max cap", test_hero_hp_max_cap)
test("Min damage", test_min_damage)

# ===== Results =====
print()
print("=" * 50)
print("  FRONTEND TEST RESULTS")
print("=" * 50)
for status, name in results:
    print("  [{}] {}".format(status, name))
print()
print("  Total: {} | Pass: {} | Fail: {}".format(PASS + FAIL, PASS, FAIL))
if FAIL == 0:
    print("  ALL TESTS PASSED")
else:
    print("  {} TESTS FAILED".format(FAIL))
print("=" * 50)
