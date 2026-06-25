"""主窗口UI - 扩展版"""
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QApplication, QScrollArea, QDialog,
    QLineEdit, QComboBox, QGroupBox, QGridLayout, QTabWidget,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

from src.utils.constants import *
from src.game.engine import GameEngine, GameState
from src.utils.save_manager import SaveManager
from src.ui.widgets import DarkProgressBar, StatLabel, BattleLogWidget, MonsterWidget


DARK_STYLE = """
QMainWindow {
    background-color: #0d0d1a;
}
QWidget {
    background-color: #0d0d1a;
    color: #CCCCCC;
    font-family: "Microsoft YaHei";
}
QPushButton {
    background-color: #1a1a2e;
    color: #CCCCCC;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #2a2a4e;
    border-color: #555;
}
QPushButton:pressed {
    background-color: #3a3a5e;
}
QPushButton:disabled {
    background-color: #111;
    color: #555;
}
QLabel {
    color: #CCCCCC;
}
QGroupBox {
    border: 1px solid #333;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
    font-size: 11px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QScrollArea {
    border: none;
}
QScrollBar:vertical {
    background: #0d0d1a;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #333;
    border-radius: 4px;
}
QComboBox {
    background-color: #1a1a2e;
    color: #CCCCCC;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 4px;
}
QLineEdit {
    background-color: #1a1a2e;
    color: #CCCCCC;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 4px;
}
QTabWidget::pane {
    border: 1px solid #333;
    background-color: #0d0d1a;
}
QTabBar::tab {
    background-color: #1a1a2e;
    color: #888;
    padding: 6px 12px;
    border: 1px solid #333;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 11px;
}
QTabBar::tab:selected {
    background-color: #0d0d1a;
    color: #FFAA00;
    border-bottom: 1px solid #0d0d1a;
}
"""


class NewGameDialog(QDialog):
    """新建游戏对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建角色")
        self.setFixedSize(320, 280)
        self.setStyleSheet(DARK_STYLE)

        layout = QVBoxLayout(self)

        name_group = QGroupBox("角色名称")
        name_layout = QVBoxLayout(name_group)
        self.name_input = QLineEdit("无名英雄")
        name_layout.addWidget(self.name_input)
        layout.addWidget(name_group)

        class_group = QGroupBox("选择职业")
        class_layout = QVBoxLayout(class_group)
        self.class_combo = QComboBox()
        for cls_id, cls_info in HERO_CLASSES.items():
            self.class_combo.addItem(
                f"{cls_info['icon']} {cls_info['name']} - {cls_info['desc']}", cls_id
            )
        class_layout.addWidget(self.class_combo)
        layout.addWidget(class_group)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("开始冒险")
        self.btn_start.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def get_data(self):
        return {
            "name": self.name_input.text() or "无名英雄",
            "hero_class": self.class_combo.currentData()
        }


class SkillTreeDialog(QDialog):
    """技能树对话框"""
    def __init__(self, hero, parent=None):
        super().__init__(parent)
        self.hero = hero
        self.setWindowTitle("Skill Tree - " + hero.name)
        self.setFixedSize(560, 600)
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 技能点显示
        sp_label = QLabel("Available Points: " + str(self.hero.skill_points))
        sp_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFAA00;")
        sp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(sp_label)

        tree_info = self.hero.get_skill_tree_info()
        if not tree_info:
            layout.addWidget(QLabel("No skill tree"))
            return

        # 用Tab展示3条分支
        tabs = QTabWidget()
        for bname, binfo in tree_info["branches"].items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            # 分支描述
            desc_label = QLabel(binfo["desc"])
            desc_label.setStyleSheet("color: #888; font-size: 11px;")
            tab_layout.addWidget(desc_label)

            # 技能列表
            for skill in binfo["skills"]:
                frame = QFrame()
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #1a1a2e;
                        border: 1px solid #333;
                        border-radius: 4px;
                        padding: 6px;
                    }
                """)
                s_layout = QHBoxLayout(frame)
                s_layout.setSpacing(8)

                # 技能信息
                info_layout = QVBoxLayout()
                name_text = skill["name"] + "  [" + str(skill["current_rank"]) + "/" + str(skill["max_rank"]) + "]"
                name_label = QLabel(name_text)
                name_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFAA00;")
                name_label.setWordWrap(True)
                info_layout.addWidget(name_label)

                desc_text = skill["desc"] + "  (Lv." + str(skill["req_level"]) + ")"
                desc_label = QLabel(desc_text)
                desc_label.setStyleSheet("font-size: 11px; color: #888;")
                desc_label.setWordWrap(True)
                info_layout.addWidget(desc_label)

                s_layout.addLayout(info_layout, 1)

                # 学习按钮
                btn = QPushButton("Learn")
                btn.setFixedSize(60, 32)
                if skill["can_learn"]:
                    btn.setStyleSheet("""
                        QPushButton { background-color: #2a4a2a; color: #55CC55; border-color: #336633; font-size: 12px; }
                        QPushButton:hover { background-color: #3a6a3a; }
                    """)
                    btn.clicked.connect(lambda checked, sid=skill["id"]: self._learn(sid))
                else:
                    btn.setEnabled(False)
                s_layout.addWidget(btn, 0)

                tab_layout.addWidget(frame)

            tab_layout.addStretch()
            tabs.addTab(tab, bname)

        layout.addWidget(tabs)

        # 关闭按钮
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def _learn(self, skill_id):
        if self.hero.learn_skill(skill_id):
            # 删除所有顶级widget（tabs和close按钮会自动清理子内容）
            layout = self.layout()
            while layout.count():
                child = layout.takeAt(0)
                w = child.widget()
                if w:
                    w.setParent(None)
                    w.deleteLater()
            self._build_ui()

    def _clear_layout(self, layout):
        """清空layout中的widget"""
        while layout.count():
            child = layout.takeAt(0)
            w = child.widget()
            if w:
                w.setParent(None)
                w.deleteLater()


class InventoryDialog(QDialog):
    """背包栏对话框 - 展示所有装备+出售功能"""
    def __init__(self, hero, parent=None):
        super().__init__(parent)
        self.hero = hero
        self.setWindowTitle("Inventory")
        self.setFixedSize(520, 600)
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # 已装备区
        equip_label = QLabel("Equipped")
        equip_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFAA00; padding: 2px;")
        layout.addWidget(equip_label)

        for slot_key in ["weapon", "armor", "accessory"]:
            item = self.hero.equipment.get(slot_key)
            slot_name = EQUIPMENT_SLOTS[slot_key]["name"]
            if item:
                stat_parts = []
                if item.hp > 0: stat_parts.append("生命+" + str(item.hp))
                if item.atk > 0: stat_parts.append("攻击+" + str(item.atk))
                if item.defense > 0: stat_parts.append("防御+" + str(item.defense))
                if item.speed > 0: stat_parts.append("速度+" + str(item.speed))
                text = "[" + slot_name + "] " + item.name + " (" + item.rarity_name + ") " + " ".join(stat_parts)
                color = item.rarity_color
            else:
                text = "[" + slot_name + "] -"
                color = "#555555"
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 11px; color: " + color + "; padding: 2px;")
            layout.addWidget(lbl)

        # 分隔线
        sep = QLabel("─" * 50)
        sep.setStyleSheet("color: #333; font-size: 8px;")
        layout.addWidget(sep)

        # 背包区
        inv_label = QLabel("Backpack ({} items)".format(len(self.hero.inventory)))
        inv_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFAA00; padding: 2px;")
        layout.addWidget(inv_label)

        # 背包列表（可滚动）
        inv_widget = QWidget()
        self.inv_layout = QVBoxLayout(inv_widget)
        self.inv_layout.setSpacing(2)
        self.inv_layout.setContentsMargins(0, 0, 0, 0)

        for idx, item in enumerate(self.hero.inventory):
            row = QHBoxLayout()
            row.setSpacing(4)

            stat_parts = []
            if item.hp > 0: stat_parts.append("生命+" + str(item.hp))
            if item.atk > 0: stat_parts.append("攻击+" + str(item.atk))
            if item.defense > 0: stat_parts.append("防御+" + str(item.defense))
            if item.speed > 0: stat_parts.append("速度+" + str(item.speed))

            slot_name = EQUIPMENT_SLOTS[item.slot]["name"]
            text = "[" + slot_name + "] " + item.name + " (" + item.rarity_name + ") " + " ".join(stat_parts)
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 10px; color: " + item.rarity_color + ";")
            row.addWidget(lbl, 1)

            # 装备按钮
            btn_equip = QPushButton("E")
            btn_equip.setFixedSize(28, 22)
            btn_equip.setStyleSheet("QPushButton { font-size: 10px; background-color: #1a1a2e; color: #55CC55; border: 1px solid #336633; } QPushButton:hover { background-color: #2a4a2a; }")
            btn_equip.clicked.connect(lambda checked, i=idx: self._equip_item(i))
            row.addWidget(btn_equip, 0)

            # 出售按钮
            sell_price = max(1, int(item.total_stats * RARITY_CONFIG[item.rarity]["stat_mult"] * 0.5))
            btn_sell = QPushButton(str(sell_price) + "g")
            btn_sell.setFixedSize(42, 22)
            btn_sell.setStyleSheet("QPushButton { font-size: 10px; background-color: #1a1a2e; color: #FF6666; border: 1px solid #663333; } QPushButton:hover { background-color: #3a1a1a; }")
            btn_sell.clicked.connect(lambda checked, i=idx: self._sell_item(i))
            row.addWidget(btn_sell, 0)

            row_widget = QWidget()
            row_widget.setLayout(row)
            self.inv_layout.addWidget(row_widget)

        self.inv_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(inv_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #333; background-color: #0a0a15; }")
        layout.addWidget(scroll, 1)

        # 关闭按钮
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def _equip_item(self, index):
        self.hero.equip_from_inventory(index)
        self._refresh()

    def _sell_item(self, index):
        price = self.hero.sell_from_inventory(index)
        self._refresh()

    def _refresh(self):
        """刷新整个界面 - 关闭并重新打开"""
        parent = self.parent()
        self.close()
        if parent and self.hero:
            dlg = InventoryDialog(self.hero, parent)
            dlg.exec_()


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.save_manager = SaveManager()
        self._last_inv_count = -1  # 跟踪背包变化

        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(DARK_STYLE)

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )

        self._init_ui()
        self._init_timers()
        self._drag_pos = None
        self._try_load()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # === 标题栏 ===
        title_bar = QHBoxLayout()
        title_label = QLabel("⚔️ 暗黑任务栏RPG")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF6666;")
        title_bar.addWidget(title_label)
        title_bar.addStretch()

        btn_min = QPushButton("—")
        btn_min.setFixedSize(24, 24)
        btn_min.clicked.connect(self.showMinimized)
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet(
            "QPushButton { color: #FF4444; } QPushButton:hover { background-color: #FF4444; color: white; }"
        )
        btn_close.clicked.connect(self.close)
        title_bar.addWidget(btn_min)
        title_bar.addWidget(btn_close)
        main_layout.addLayout(title_bar)

        # === 英雄信息区 ===
        hero_group = QGroupBox("英雄")
        hero_layout = QVBoxLayout(hero_group)

        self.lbl_name = QLabel("未创建角色")
        self.lbl_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFAA00;")
        hero_layout.addWidget(self.lbl_name)

        # 血条
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("❤️"))
        self.hp_bar = DarkProgressBar("#FF4444")
        hp_layout.addWidget(self.hp_bar)
        self.lbl_hp = QLabel("0/0")
        self.lbl_hp.setFixedWidth(80)
        hp_layout.addWidget(self.lbl_hp)
        hero_layout.addLayout(hp_layout)

        # 经验条
        exp_layout = QHBoxLayout()
        exp_layout.addWidget(QLabel("✨"))
        self.exp_bar = DarkProgressBar("#44AAFF")
        exp_layout.addWidget(self.exp_bar)
        self.lbl_exp = QLabel("0%")
        self.lbl_exp.setFixedWidth(80)
        exp_layout.addWidget(self.lbl_exp)
        hero_layout.addLayout(exp_layout)

        # 属性行
        stats_layout = QHBoxLayout()
        self.lbl_atk = StatLabel("⚔️", "攻击: 0", "#FF6666")
        self.lbl_def = StatLabel("🛡️", "防御: 0", "#6666FF")
        self.lbl_spd = StatLabel("💨", "速度: 0", "#66FF66")
        stats_layout.addWidget(self.lbl_atk)
        stats_layout.addWidget(self.lbl_def)
        stats_layout.addWidget(self.lbl_spd)
        hero_layout.addLayout(stats_layout)

        stats2_layout = QHBoxLayout()
        self.lbl_gold = StatLabel("💰", "金币: 0", GOLD_COLOR)
        self.lbl_sp = StatLabel("🔮", "技能点: 0", "#AA55CC")
        self.lbl_crit = StatLabel("💥", "暴击: 8%", "#FF5555")
        stats2_layout.addWidget(self.lbl_gold)
        stats2_layout.addWidget(self.lbl_sp)
        stats2_layout.addWidget(self.lbl_crit)
        hero_layout.addLayout(stats2_layout)

        main_layout.addWidget(hero_group)

        # === 装备栏 ===
        equip_group = QGroupBox("Equipment")
        equip_layout = QVBoxLayout(equip_group)
        equip_layout.setSpacing(2)

        # 已装备
        self.lbl_weapon = QLabel("[ - ]")
        self.lbl_weapon.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        self.lbl_armor = QLabel("[ - ]")
        self.lbl_armor.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        self.lbl_accessory = QLabel("[ - ]")
        self.lbl_accessory.setStyleSheet("font-size: 11px; color: #AAAAAA;")

        equip_layout.addWidget(self.lbl_weapon)
        equip_layout.addWidget(self.lbl_armor)
        equip_layout.addWidget(self.lbl_accessory)

        # 背包（可滚动）
        self.inventory_container = QVBoxLayout()
        self.inventory_container.setSpacing(2)
        inventory_widget = QWidget()
        inventory_widget.setLayout(self.inventory_container)
        self.inventory_scroll = QScrollArea()
        self.inventory_scroll.setWidget(inventory_widget)
        self.inventory_scroll.setWidgetResizable(True)
        self.inventory_scroll.setFixedHeight(120)
        self.inventory_scroll.setStyleSheet("QScrollArea { border: 1px solid #333; background-color: #0a0a15; }")
        equip_layout.addWidget(self.inventory_scroll)

        main_layout.addWidget(equip_group)

        # === 怪物/战斗区 ===
        monster_group = QGroupBox("战斗")
        monster_layout = QVBoxLayout(monster_group)

        self.monster_widget = MonsterWidget()
        monster_layout.addWidget(self.monster_widget)

        stage_layout = QHBoxLayout()
        self.lbl_difficulty = QLabel("[普通]")
        self.lbl_difficulty.setStyleSheet("font-size: 11px; color: #CCCCCC; font-weight: bold;")
        stage_layout.addWidget(self.lbl_difficulty)
        self.lbl_stage = QLabel("第 1 关 - 黑暗森林")
        self.lbl_stage.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        stage_layout.addWidget(self.lbl_stage)
        stage_layout.addStretch()
        self.lbl_progress = QLabel("进度: 0/30")
        self.lbl_progress.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        stage_layout.addWidget(self.lbl_progress)
        monster_layout.addLayout(stage_layout)

        main_layout.addWidget(monster_group)

        # === 战斗日志 ===
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout(log_group)
        self.battle_log = BattleLogWidget()
        self.battle_log.setFixedHeight(90)
        log_layout.addWidget(self.battle_log)
        main_layout.addWidget(log_group)

        # === 按钮区 ===
        btn_layout = QHBoxLayout()

        self.btn_resurrect = QPushButton("💀 复活")
        self.btn_resurrect.setStyleSheet("""
            QPushButton { background-color: #4a1a1a; color: #FF6666; border-color: #663333; }
            QPushButton:hover { background-color: #6a2a2a; }
        """)
        self.btn_resurrect.clicked.connect(self._on_resurrect)
        self.btn_resurrect.setVisible(False)
        btn_layout.addWidget(self.btn_resurrect)

        self.btn_skill = QPushButton("Skill")
        self.btn_skill.clicked.connect(self._on_skill_tree)
        btn_layout.addWidget(self.btn_skill)

        self.btn_inventory = QPushButton("Bag")
        self.btn_inventory.clicked.connect(self._on_inventory)
        btn_layout.addWidget(self.btn_inventory)

        self.btn_new = QPushButton("New")
        self.btn_new.clicked.connect(self._on_new_game)
        btn_layout.addWidget(self.btn_new)

        self.btn_save = QPushButton("💾 存档")
        self.btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(self.btn_save)

        self.btn_quit = QPushButton("🚪 退出")
        self.btn_quit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_quit)

        main_layout.addLayout(btn_layout)

    def _init_timers(self):
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self._game_tick)
        self.game_timer.start(TICK_RATE)

        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_ui)
        self.ui_timer.start(200)

        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._on_save)
        self.auto_save_timer.start(AUTO_SAVE_INTERVAL)

    def _game_tick(self):
        if self.engine.hero and self.engine.state != GameState.DEAD:
            self.engine.update()

    def _update_ui(self):
        hero = self.engine.hero
        if not hero:
            self.lbl_name.setText("未创建角色")
            return

        cls_cfg = HERO_CLASSES[hero.hero_class]
        self.lbl_name.setText(f"{cls_cfg['icon']} {hero.name} - {cls_cfg['name']} Lv.{hero.level}")

        self.hp_bar.setValue(int(hero.hp_percent * 100))
        self.lbl_hp.setText(f"{hero.current_hp}/{hero.max_hp}")

        self.exp_bar.setValue(int(hero.exp_progress * 100))
        if hero.level >= MAX_LEVEL:
            self.lbl_exp.setText("MAX")
        else:
            self.lbl_exp.setText(f"{hero.exp}/{hero.exp_to_level}")

        self.lbl_atk.setText(f"⚔️ 攻击: {hero.atk}")
        self.lbl_def.setText(f"🛡️ 防御: {hero.defense}")
        self.lbl_spd.setText(f"💨 速度: {hero.speed:.1f}")
        self.lbl_gold.setText("金币: {}".format(hero.gold))
        self.lbl_sp.setText("技能点: {}".format(hero.skill_points))
        self.lbl_crit.setText("暴击: {}%".format(int(hero.crit_rate*100)))

        # Update equipment display
        for slot_key, lbl in [("weapon", self.lbl_weapon),
                               ("armor", self.lbl_armor),
                               ("accessory", self.lbl_accessory)]:
            item = hero.equipment.get(slot_key)
            if item:
                stat_parts = []
                if item.hp > 0: stat_parts.append("生命+" + str(item.hp))
                if item.atk > 0: stat_parts.append("攻击+" + str(item.atk))
                if item.defense > 0: stat_parts.append("防御+" + str(item.defense))
                if item.speed > 0: stat_parts.append("速度+" + str(item.speed))
                stat_str = " ".join(stat_parts)
                slot_name = EQUIPMENT_SLOTS[slot_key]["name"]
                rname = item.rarity_name
                rcolor = item.rarity_color
                text = "[" + slot_name + "] " + item.name + " (" + rname + ") " + stat_str
                lbl.setText(text)
                lbl.setStyleSheet("font-size: 11px; color: " + rcolor + ";")
            else:
                slot_name = EQUIPMENT_SLOTS[slot_key]["name"]
                lbl.setText("[" + slot_name + "] -")
                lbl.setStyleSheet("font-size: 11px; color: #555555;")

        # Update inventory display
        self._update_inventory()

        self.monster_widget.update_monster(self.engine.current_monster)

        diff_name = self.engine.get_difficulty_name()
        diff_color = DIFFICULTIES[self.engine.difficulty]["color"]
        self.lbl_difficulty.setText("[{}]".format(diff_name))
        self.lbl_difficulty.setStyleSheet("font-size: 11px; color: {}; font-weight: bold;".format(diff_color))
        chapter_name = self.engine.get_chapter_name()
        self.lbl_stage.setText("第 {} 关 - {}".format(self.engine.stage, chapter_name))
        self.lbl_progress.setText("进度: {}/{}".format(self.engine.stage_progress, MONSTERS_PER_STAGE))

        self.battle_log.set_logs(self.engine.combat_log)

        is_dead = self.engine.state == GameState.DEAD
        self.btn_resurrect.setVisible(is_dead)
        self.btn_new.setVisible(not is_dead)

    def _update_inventory(self):
        """更新背包显示 - 仅在背包变化时重建"""
        hero = self.engine.hero
        if not hero:
            return

        # 仅在背包数量变化时重建
        inv_count = len(hero.inventory)
        if inv_count == self._last_inv_count:
            return
        self._last_inv_count = inv_count

        # 清空旧widget
        self._clear_inv_container()

        # 显示背包物品
        for idx, item in enumerate(hero.inventory):
            row = QHBoxLayout()
            row.setSpacing(4)

            stat_parts = []
            if item.hp > 0: stat_parts.append("生命+" + str(item.hp))
            if item.atk > 0: stat_parts.append("攻击+" + str(item.atk))
            if item.defense > 0: stat_parts.append("防御+" + str(item.defense))
            if item.speed > 0: stat_parts.append("速度+" + str(item.speed))

            slot_name = EQUIPMENT_SLOTS[item.slot]["name"]
            text = "[" + slot_name + "] " + item.name + " (" + item.rarity_name + ") " + " ".join(stat_parts)
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 10px; color: " + item.rarity_color + ";")
            row.addWidget(lbl, 1)

            btn = QPushButton("装")
            btn.setFixedSize(24, 20)
            btn.setStyleSheet("QPushButton { font-size: 10px; background-color: #1a1a2e; color: #55CC55; border: 1px solid #336633; } QPushButton:hover { background-color: #2a4a2a; }")
            btn.clicked.connect(lambda checked, i=idx: self._equip_from_inventory(i))
            row.addWidget(btn, 0)

            row_widget = QWidget()
            row_widget.setLayout(row)
            self.inventory_container.addWidget(row_widget)

        # Add stretch at bottom
        self.inventory_container.addStretch()

    def _clear_inv_container(self):
        """清空背包容器"""
        while self.inventory_container.count():
            child = self.inventory_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_inv_container_sub(child.layout())

    def _clear_inv_container_sub(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_inv_container_sub(child.layout())

    def _equip_from_inventory(self, index):
        """从背包装备物品"""
        hero = self.engine.hero
        if hero:
            hero.equip_from_inventory(index)
            self._last_inv_count = -1  # 强制刷新

    def _on_new_game(self):
        self._last_inv_count = -1  # 重置背包缓存
        dialog = NewGameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.engine.new_game(data["name"], data["hero_class"])

    def _on_resurrect(self):
        self.engine.resurrect()

    def _on_skill_tree(self):
        if self.engine.hero:
            dlg = SkillTreeDialog(self.engine.hero, self)
            dlg.exec_()

    def _on_inventory(self):
        if self.engine.hero:
            dlg = InventoryDialog(self.engine.hero, self)
            dlg.exec_()
            self._last_inv_count = -1  # 强制刷新主界面背包

    def _on_save(self):
        if self.engine.hero:
            data = self.engine.get_save_data()
            self.save_manager.save(data)

    def _try_load(self):
        if self.save_manager.has_save():
            data = self.save_manager.load()
            if data:
                self.engine.load_save_data(data)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def closeEvent(self, event):
        self._on_save()
        event.accept()
