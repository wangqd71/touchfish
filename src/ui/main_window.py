"""主窗口UI - 扩展版"""
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QApplication, QScrollArea, QDialog,
    QLineEdit, QComboBox, QGroupBox, QGridLayout, QTabWidget,
    QSizePolicy, QCheckBox
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
            tab_layout.setContentsMargins(4, 4, 4, 4)

            # 分支描述
            desc_label = QLabel(binfo["desc"])
            desc_label.setStyleSheet("color: #888; font-size: 11px;")
            tab_layout.addWidget(desc_label)

            # 技能列表容器
            skills_widget = QWidget()
            skills_layout = QVBoxLayout(skills_widget)
            skills_layout.setSpacing(4)
            skills_layout.setContentsMargins(0, 0, 0, 0)

            for skill in binfo["skills"]:
                frame = QFrame()
                frame.setMinimumHeight(50)
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

                skills_layout.addWidget(frame)

            skills_layout.addStretch()

            # 用ScrollArea包裹技能列表
            scroll = QScrollArea()
            scroll.setWidget(skills_widget)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
            tab_layout.addWidget(scroll)

            tabs.addTab(tab, bname)

        layout.addWidget(tabs, 1)

        # 重置技能按钮
        reset_cost = self.hero.get_reset_cost()
        btn_reset = QPushButton("重置技能 ({} 金币)".format(reset_cost))
        if reset_cost > 0 and self.hero.gold >= reset_cost:
            btn_reset.setStyleSheet("""
                QPushButton { background-color: #4a3a1a; color: #FFAA00; border-color: #665533; font-size: 12px; }
                QPushButton:hover { background-color: #6a4a2a; }
            """)
            btn_reset.clicked.connect(self._reset_skills)
        else:
            btn_reset.setEnabled(False)
        layout.addWidget(btn_reset)

        # 关闭按钮
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def _learn(self, skill_id):
        if self.hero.learn_skill(skill_id):
            # 记住当前tab索引
            old_tabs = self.findChild(QTabWidget)
            tab_index = old_tabs.currentIndex() if old_tabs else 0
            self._clear_layout(self.layout())
            self._rebuild_ui(tab_index)

    def _reset_skills(self):
        if self.hero.reset_skills():
            self._clear_layout(self.layout())
            self._rebuild_ui()

    def _rebuild_ui(self, tab_index=0):
        """在现有布局上重建UI内容"""
        layout = self.layout()

        sp_label = QLabel("Available Points: " + str(self.hero.skill_points))
        sp_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFAA00;")
        sp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(sp_label)

        tree_info = self.hero.get_skill_tree_info()
        if not tree_info:
            layout.addWidget(QLabel("No skill tree"))
            return

        tabs = QTabWidget()
        for bname, binfo in tree_info["branches"].items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            desc_label = QLabel(binfo["desc"])
            desc_label.setStyleSheet("color: #888; font-size: 11px;")
            tab_layout.addWidget(desc_label)

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

        if tab_index < tabs.count():
            tabs.setCurrentIndex(tab_index)

        layout.addWidget(tabs)

        # 重置技能按钮
        reset_cost = self.hero.get_reset_cost()
        btn_reset = QPushButton("重置技能 ({} 金币)".format(reset_cost))
        if reset_cost > 0 and self.hero.gold >= reset_cost:
            btn_reset.setStyleSheet("""
                QPushButton { background-color: #4a3a1a; color: #FFAA00; border-color: #665533; font-size: 12px; }
                QPushButton:hover { background-color: #6a4a2a; }
            """)
            btn_reset.clicked.connect(self._reset_skills)
        else:
            btn_reset.setEnabled(False)
        layout.addWidget(btn_reset)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def _clear_layout(self, layout):
        """清空layout中的所有widget和子布局"""
        while layout.count():
            child = layout.takeAt(0)
            w = child.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
            sub = child.layout()
            if sub:
                self._clear_layout(sub)


class TalentTreeDialog(QDialog):
    """天赋树对话框 - 使用金币点亮"""
    def __init__(self, hero, parent=None):
        super().__init__(parent)
        self.hero = hero
        self.setWindowTitle("天赋树 - " + hero.name)
        self.setFixedSize(560, 600)
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        gold_label = QLabel("金币: {}".format(self.hero.gold))
        gold_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFD700;")
        gold_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(gold_label)

        talent_info = self.hero.get_talent_info()

        tabs = QTabWidget()
        for bid, binfo in talent_info.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(4, 4, 4, 4)

            desc_label = QLabel(binfo["icon"] + " " + binfo["desc"])
            desc_label.setStyleSheet("color: {}; font-size: 12px; font-weight: bold;".format(binfo["color"]))
            tab_layout.addWidget(desc_label)

            # 天赋列表容器
            talents_widget = QWidget()
            talents_layout = QVBoxLayout(talents_widget)
            talents_layout.setSpacing(4)
            talents_layout.setContentsMargins(0, 0, 0, 0)

            for talent in binfo["talents"]:
                frame = QFrame()
                frame.setMinimumHeight(50)
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #1a1a2e;
                        border: 1px solid #333;
                        border-radius: 4px;
                        padding: 6px;
                    }
                """)
                t_layout = QHBoxLayout(frame)
                t_layout.setSpacing(8)

                info_layout = QVBoxLayout()
                name_text = talent["icon"] + " " + talent["name"] + "  [" + str(talent["current_rank"]) + "/" + str(talent["max_rank"]) + "]"
                name_label = QLabel(name_text)
                name_label.setStyleSheet("font-size: 13px; font-weight: bold; color: {};".format(binfo["color"]))
                name_label.setWordWrap(True)
                info_layout.addWidget(name_label)

                value_now = talent["effect_per_rank"] * talent["current_rank"] * 100
                value_next = talent["effect_per_rank"] * (talent["current_rank"] + 1) * 100 if talent["current_rank"] < talent["max_rank"] else value_now
                desc_text = talent["desc"].format(value=int(value_now)) + " -> " + str(int(value_next)) + "%"
                desc_label = QLabel(desc_text)
                desc_label.setStyleSheet("font-size: 11px; color: #888;")
                desc_label.setWordWrap(True)
                info_layout.addWidget(desc_label)

                t_layout.addLayout(info_layout, 1)

                btn_text = str(talent["cost"]) + "g" if talent["cost"] > 0 else "MAX"
                btn = QPushButton(btn_text)
                btn.setFixedSize(70, 32)
                if talent["can_learn"]:
                    btn.setStyleSheet("""
                        QPushButton { background-color: #3a3a1a; color: #FFD700; border-color: #665533; font-size: 11px; }
                        QPushButton:hover { background-color: #5a4a2a; }
                    """)
                    btn.clicked.connect(lambda checked, tid=talent["id"]: self._learn(tid))
                else:
                    btn.setEnabled(False)
                t_layout.addWidget(btn, 0)

                talents_layout.addWidget(frame)

            talents_layout.addStretch()

            # 用ScrollArea包裹
            scroll = QScrollArea()
            scroll.setWidget(talents_widget)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
            tab_layout.addWidget(scroll)

            tabs.addTab(tab, binfo["icon"] + " " + binfo["name"])

        layout.addWidget(tabs, 1)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def _learn(self, talent_id):
        if self.hero.learn_talent(talent_id):
            old_tabs = self.findChild(QTabWidget)
            tab_index = old_tabs.currentIndex() if old_tabs else 0
            self._clear_layout(self.layout())
            self._rebuild_ui(tab_index)

    def _rebuild_ui(self, tab_index=0):
        layout = self.layout()

        gold_label = QLabel("💰 金币: {}".format(self.hero.gold))
        gold_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFD700;")
        gold_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(gold_label)

        talent_info = self.hero.get_talent_info()

        tabs = QTabWidget()
        for bid, binfo in talent_info.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            desc_label = QLabel(binfo["icon"] + " " + binfo["desc"])
            desc_label.setStyleSheet("color: {}; font-size: 12px; font-weight: bold;".format(binfo["color"]))
            tab_layout.addWidget(desc_label)

            for talent in binfo["talents"]:
                frame = QFrame()
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #1a1a2e;
                        border: 1px solid #333;
                        border-radius: 4px;
                        padding: 6px;
                    }
                """)
                t_layout = QHBoxLayout(frame)
                t_layout.setSpacing(8)

                info_layout = QVBoxLayout()
                name_text = talent["icon"] + " " + talent["name"] + "  [" + str(talent["current_rank"]) + "/" + str(talent["max_rank"]) + "]"
                name_label = QLabel(name_text)
                name_label.setStyleSheet("font-size: 13px; font-weight: bold; color: {};".format(binfo["color"]))
                name_label.setWordWrap(True)
                info_layout.addWidget(name_label)

                value_now = talent["effect_per_rank"] * talent["current_rank"] * 100
                value_next = talent["effect_per_rank"] * (talent["current_rank"] + 1) * 100 if talent["current_rank"] < talent["max_rank"] else value_now
                desc_text = talent["desc"].format(value=int(value_now)) + " → " + str(int(value_next)) + "%"
                desc_label = QLabel(desc_text)
                desc_label.setStyleSheet("font-size: 11px; color: #888;")
                desc_label.setWordWrap(True)
                info_layout.addWidget(desc_label)

                t_layout.addLayout(info_layout, 1)

                btn_text = str(talent["cost"]) + "金" if talent["cost"] > 0 else "MAX"
                btn = QPushButton(btn_text)
                btn.setFixedSize(70, 32)
                if talent["can_learn"]:
                    btn.setStyleSheet("""
                        QPushButton { background-color: #3a3a1a; color: #FFD700; border-color: #665533; font-size: 11px; }
                        QPushButton:hover { background-color: #5a4a2a; }
                    """)
                    btn.clicked.connect(lambda checked, tid=talent["id"]: self._learn(tid))
                else:
                    btn.setEnabled(False)
                t_layout.addWidget(btn, 0)

                tab_layout.addWidget(frame)

            tab_layout.addStretch()
            tabs.addTab(tab, binfo["icon"] + " " + binfo["name"])

        if tab_index < tabs.count():
            tabs.setCurrentIndex(tab_index)

        layout.addWidget(tabs)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            w = child.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
            sub = child.layout()
            if sub:
                self._clear_layout(sub)


class InventoryDialog(QDialog):
    """背包对话框 - 装备评分 + 批量售卖 + 合成"""
    def __init__(self, hero, parent=None):
        super().__init__(parent)
        self.hero = hero
        self.setWindowTitle("背包")
        self.setFixedSize(560, 640)
        self.setStyleSheet(DARK_STYLE)
        self.selected = set()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # 已装备
        equip_label = QLabel("已装备")
        equip_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFAA00; padding: 2px;")
        layout.addWidget(equip_label)

        for slot_key in SLOT_GROUP_ALL:
            item = self.hero.equipment.get(slot_key)
            slot_name = EQUIPMENT_SLOTS[slot_key]["name"]
            if item:
                yy_str = ""
                if item.yin_yang == YY_YANG:
                    yy_str = " [—— ]"
                elif item.yin_yang == YY_YIN:
                    yy_str = " [— —]"
                text = "[{}] {} ({}) {} 评分:{}{}".format(
                    slot_name, item.name, item.rarity_name, item.get_stat_text(), item.score, yy_str)
                color = item.rarity_color
            else:
                text = "[{}] -".format(slot_name)
                color = "#555555"
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 11px; color: {}; padding: 2px;".format(color))
            layout.addWidget(lbl)

        # 卦象显示
        hex_info = self.hero.get_hexagram_display()
        if hex_info["active"]:
            sep = QLabel("─" * 60)
            sep.setStyleSheet("color: #333; font-size: 8px;")
            layout.addWidget(sep)

            hex_label = QLabel("{} {} | {} {}".format(
                hex_info["symbol"], hex_info["name"],
                hex_info["bonus_name"], hex_info["bonus_text"]))
            hex_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFD700; padding: 2px;")
            layout.addWidget(hex_label)

            # 爻线显示
            lines_text = ""
            for slot_name, line_str, yy_name in hex_info["lines"]:
                lines_text += "{}: {}  ".format(slot_name, line_str)
            lines_label = QLabel(lines_text)
            lines_label.setStyleSheet("font-size: 10px; color: #AAAAAA; padding: 2px;")
            layout.addWidget(lines_label)
        elif hex_info["count"] > 0:
            sep = QLabel("─" * 60)
            sep.setStyleSheet("color: #333; font-size: 8px;")
            layout.addWidget(sep)
            hex_label = QLabel("卦象: {}/6 件装备有阴阳属性".format(hex_info["count"]))
            hex_label.setStyleSheet("font-size: 10px; color: #888; padding: 2px;")
            layout.addWidget(hex_label)

        sep = QLabel("─" * 60)
        sep.setStyleSheet("color: #333; font-size: 8px;")
        layout.addWidget(sep)

        inv_label = QLabel("背包 ({} 件)".format(len(self.hero.inventory)))
        inv_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFAA00; padding: 2px;")
        layout.addWidget(inv_label)

        # 背包列表
        inv_widget = QWidget()
        self.inv_layout = QVBoxLayout(inv_widget)
        self.inv_layout.setSpacing(2)
        self.inv_layout.setContentsMargins(0, 0, 0, 0)

        for idx, item in enumerate(self.hero.inventory):
            row = QHBoxLayout()
            row.setSpacing(4)

            cb = QCheckBox()
            cb.setChecked(idx in self.selected)
            cb.stateChanged.connect(lambda state, i=idx: self._toggle_select(i, state))
            row.addWidget(cb, 0)

            slot_name = EQUIPMENT_SLOTS[item.slot]["name"]
            yy_str = ""
            if item.yin_yang == YY_YANG:
                yy_str = " [阳]"
            elif item.yin_yang == YY_YIN:
                yy_str = " [阴]"
            text = "[{}] {} ({}) {} 评分:{}{}".format(
                slot_name, item.name, item.rarity_name, item.get_stat_text(), item.score, yy_str)
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 10px; color: {};".format(item.rarity_color))
            row.addWidget(lbl, 1)

            btn_equip = QPushButton("装备")
            btn_equip.setFixedSize(36, 22)
            btn_equip.setStyleSheet("QPushButton { font-size: 10px; background-color: #1a1a2e; color: #55CC55; border: 1px solid #336633; } QPushButton:hover { background-color: #2a4a2a; }")
            btn_equip.clicked.connect(lambda checked, i=idx: self._equip_item(i))
            row.addWidget(btn_equip, 0)

            btn_sell = QPushButton("{}g".format(max(1, int(item.sell_price * self.hero.sell_mult))))
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

        # 按钮栏
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(6)

        btn_sel_all = QPushButton("全选")
        btn_sel_all.setFixedSize(50, 28)
        btn_sel_all.clicked.connect(self._select_all)
        btn_bar.addWidget(btn_sel_all)

        btn_sel_none = QPushButton("取消")
        btn_sel_none.setFixedSize(50, 28)
        btn_sel_none.clicked.connect(self._select_none)
        btn_bar.addWidget(btn_sel_none)

        btn_sel_rarity = QComboBox()
        btn_sel_rarity.setFixedWidth(80)
        for rk, rc in RARITY_CONFIG.items():
            btn_sel_rarity.addItem(rc["name"], rk)
        btn_sel_rarity.currentIndexChanged.connect(lambda: self._select_by_rarity(btn_sel_rarity.currentData()))
        btn_bar.addWidget(btn_sel_rarity)

        btn_batch_sell = QPushButton("批量售卖")
        btn_batch_sell.setFixedHeight(28)
        btn_batch_sell.setStyleSheet("QPushButton { background-color: #3a1a1a; color: #FF6666; border-color: #663333; } QPushButton:hover { background-color: #5a2a2a; }")
        btn_batch_sell.clicked.connect(self._batch_sell)
        btn_bar.addWidget(btn_batch_sell)

        btn_merge = QPushButton("合成 (9件同品级)")
        btn_merge.setFixedHeight(28)
        btn_merge.setStyleSheet("QPushButton { background-color: #1a1a3a; color: #6666FF; border-color: #333366; } QPushButton:hover { background-color: #2a2a5a; }")
        btn_merge.clicked.connect(self._merge)
        btn_bar.addWidget(btn_merge)

        layout.addLayout(btn_bar)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def _toggle_select(self, idx, state):
        if state:
            self.selected.add(idx)
        else:
            self.selected.discard(idx)

    def _select_all(self):
        self.selected = set(range(len(self.hero.inventory)))
        self._rebuild_inv()

    def _select_none(self):
        self.selected.clear()
        self._rebuild_inv()

    def _select_by_rarity(self, rarity):
        self.selected.clear()
        for idx, item in enumerate(self.hero.inventory):
            if item.rarity == rarity:
                self.selected.add(idx)
        self._rebuild_inv()

    def _equip_item(self, index):
        self.hero.equip_from_inventory(index)
        self.selected.discard(index)
        self._rebuild_inv()

    def _sell_item(self, index):
        self.hero.sell_from_inventory(index)
        self.selected.discard(index)
        self._rebuild_inv()

    def _batch_sell(self):
        if not self.selected:
            return
        self.hero.sell_batch(sorted(self.selected))
        self.selected.clear()
        self._rebuild_inv()

    def _merge(self):
        if len(self.selected) != 9:
            return
        if self.hero.merge_equipment(sorted(self.selected)):
            self.selected.clear()
            self._rebuild_inv()

    def _rebuild_inv(self):
        """只重建背包列表，不重建整个对话框"""
        # 清空旧的inv_layout
        while self.inv_layout.count():
            child = self.inv_layout.takeAt(0)
            w = child.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        # 重建
        for idx, item in enumerate(self.hero.inventory):
            row = QHBoxLayout()
            row.setSpacing(4)

            cb = QCheckBox()
            cb.setChecked(idx in self.selected)
            cb.stateChanged.connect(lambda state, i=idx: self._toggle_select(i, state))
            row.addWidget(cb, 0)

            slot_name = EQUIPMENT_SLOTS[item.slot]["name"]
            yy_str = ""
            if item.yin_yang == YY_YANG:
                yy_str = " [阳]"
            elif item.yin_yang == YY_YIN:
                yy_str = " [阴]"
            text = "[{}] {} ({}) {} 评分:{}{}".format(
                slot_name, item.name, item.rarity_name, item.get_stat_text(), item.score, yy_str)
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 10px; color: {};".format(item.rarity_color))
            row.addWidget(lbl, 1)

            btn_equip = QPushButton("装备")
            btn_equip.setFixedSize(36, 22)
            btn_equip.setStyleSheet("QPushButton { font-size: 10px; background-color: #1a1a2e; color: #55CC55; border: 1px solid #336633; } QPushButton:hover { background-color: #2a4a2a; }")
            btn_equip.clicked.connect(lambda checked, i=idx: self._equip_item(i))
            row.addWidget(btn_equip, 0)

            btn_sell = QPushButton("{}g".format(max(1, int(item.sell_price * self.hero.sell_mult))))
            btn_sell.setFixedSize(42, 22)
            btn_sell.setStyleSheet("QPushButton { font-size: 10px; background-color: #1a1a2e; color: #FF6666; border: 1px solid #663333; } QPushButton:hover { background-color: #3a1a1a; }")
            btn_sell.clicked.connect(lambda checked, i=idx: self._sell_item(i))
            row.addWidget(btn_sell, 0)

            row_widget = QWidget()
            row_widget.setLayout(row)
            self.inv_layout.addWidget(row_widget)

        self.inv_layout.addStretch()


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.save_manager = SaveManager()

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
        hero_group.setMinimumHeight(160)
        hero_layout = QVBoxLayout(hero_group)

        self.lbl_name = QLabel("未创建角色")
        self.lbl_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFAA00;")
        hero_layout.addWidget(self.lbl_name)

        # 血条
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("HP"))
        self.hp_bar = DarkProgressBar("#FF4444")
        hp_layout.addWidget(self.hp_bar)
        self.lbl_hp = QLabel("0/0")
        self.lbl_hp.setFixedWidth(80)
        hp_layout.addWidget(self.lbl_hp)
        hero_layout.addLayout(hp_layout)

        # 经验条
        exp_layout = QHBoxLayout()
        exp_layout.addWidget(QLabel("EXP"))
        self.exp_bar = DarkProgressBar("#44AAFF")
        exp_layout.addWidget(self.exp_bar)
        self.lbl_exp = QLabel("0%")
        self.lbl_exp.setFixedWidth(80)
        exp_layout.addWidget(self.lbl_exp)
        hero_layout.addLayout(exp_layout)

        # 属性行
        stats_layout = QHBoxLayout()
        self.lbl_atk = StatLabel("", "攻击: 0", "#FF6666")
        self.lbl_def = StatLabel("", "防御: 0", "#6666FF")
        self.lbl_spd = StatLabel("", "速度: 0", "#66FF66")
        stats_layout.addWidget(self.lbl_atk)
        stats_layout.addWidget(self.lbl_def)
        stats_layout.addWidget(self.lbl_spd)
        hero_layout.addLayout(stats_layout)

        stats2_layout = QHBoxLayout()
        self.lbl_gold = StatLabel("", "金币: 0", GOLD_COLOR)
        self.lbl_sp = StatLabel("", "技能点: 0", "#AA55CC")
        self.lbl_crit = StatLabel("", "暴击: 8%", "#FF5555")
        stats2_layout.addWidget(self.lbl_gold)
        stats2_layout.addWidget(self.lbl_sp)
        stats2_layout.addWidget(self.lbl_crit)
        hero_layout.addLayout(stats2_layout)

        main_layout.addWidget(hero_group)

        # === 装备栏 ===
        equip_group = QGroupBox("Equipment")
        equip_layout = QVBoxLayout(equip_group)
        equip_layout.setSpacing(1)

        # 已装备 (6槽)
        self.equip_labels = {}
        for slot_key in SLOT_GROUP_ALL:
            lbl = QLabel("[ - ]")
            lbl.setStyleSheet("font-size: 10px; color: #AAAAAA;")
            equip_layout.addWidget(lbl)
            self.equip_labels[slot_key] = lbl

        # 卦象显示
        self.lbl_hexagram = QLabel("")
        self.lbl_hexagram.setStyleSheet("font-size: 11px; color: #FFD700; padding: 2px;")
        self.lbl_hexagram.setWordWrap(True)
        equip_layout.addWidget(self.lbl_hexagram)

        main_layout.addWidget(equip_group)

        # === 怪物/战斗区 ===
        monster_group = QGroupBox("战斗")
        monster_layout = QVBoxLayout(monster_group)
        monster_layout.setSpacing(10)

        self.monster_widget = MonsterWidget()
        monster_layout.addWidget(self.monster_widget)

        stage_layout = QHBoxLayout()
        stage_layout.setSpacing(8)
        self.lbl_difficulty = QLabel("[普通]")
        self.lbl_difficulty.setStyleSheet("font-size: 11px; color: #CCCCCC; font-weight: bold;")
        self.lbl_difficulty.setFixedWidth(40)
        stage_layout.addWidget(self.lbl_difficulty)
        self.lbl_stage = QLabel("第 1 关 - 黑暗森林")
        self.lbl_stage.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        stage_layout.addWidget(self.lbl_stage, 1)
        self.lbl_progress = QLabel("进度: 0/30")
        self.lbl_progress.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        self.lbl_progress.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
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

        self.btn_skill = QPushButton("技能")
        self.btn_skill.clicked.connect(self._on_skill_tree)
        btn_layout.addWidget(self.btn_skill)

        self.btn_talent = QPushButton("天赋")
        self.btn_talent.clicked.connect(self._on_talent_tree)
        btn_layout.addWidget(self.btn_talent)

        self.btn_inventory = QPushButton("背包")
        self.btn_inventory.clicked.connect(self._on_inventory)
        btn_layout.addWidget(self.btn_inventory)

        self.btn_new = QPushButton("新建")
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
        self.lbl_name.setText("{} - {} Lv.{}".format(hero.name, cls_cfg["name"], hero.level))

        self.hp_bar.setValue(int(hero.hp_percent * 100))
        self.lbl_hp.setText(f"{hero.current_hp}/{hero.max_hp}")

        self.exp_bar.setValue(int(hero.exp_progress * 100))
        if hero.level >= MAX_LEVEL:
            self.lbl_exp.setText("MAX")
        else:
            self.lbl_exp.setText(f"{hero.exp}/{hero.exp_to_level}")

        self.lbl_atk.setText("攻击: {}".format(hero.atk))
        self.lbl_def.setText("防御: {}".format(hero.defense))
        self.lbl_spd.setText("速度: {:.1f}".format(hero.speed))
        self.lbl_gold.setText("金币: {}".format(hero.gold))
        self.lbl_sp.setText("技能点: {}".format(hero.skill_points))
        self.lbl_crit.setText("暴击: {}%".format(int(hero.crit_rate*100)))

        # Update equipment display (6 slots)
        for slot_key in SLOT_GROUP_ALL:
            lbl = self.equip_labels.get(slot_key)
            if not lbl:
                continue
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
                yy_str = ""
                if item.yin_yang == YY_YANG:
                    yy_str = " [—— ]"
                elif item.yin_yang == YY_YIN:
                    yy_str = " [— —]"
                text = "[" + slot_name + "] " + item.name + " (" + rname + ") " + stat_str + yy_str
                lbl.setText(text)
                lbl.setStyleSheet("font-size: 10px; color: " + rcolor + ";")
            else:
                slot_name = EQUIPMENT_SLOTS[slot_key]["name"]
                lbl.setText("[" + slot_name + "] -")
                lbl.setStyleSheet("font-size: 10px; color: #555555;")

        # Update hexagram display
        hex_info = hero.get_hexagram_display()
        if hex_info["active"]:
            hex_text = "{} {} | {} +{:.0f}%".format(
                hex_info["symbol"], hex_info["name"],
                hex_info["bonus_name"], hex_info["bonus_value"] * 100)
            self.lbl_hexagram.setText(hex_text)
            self.lbl_hexagram.setStyleSheet("font-size: 11px; color: #FFD700; font-weight: bold; padding: 2px;")
        elif hex_info["count"] > 0:
            self.lbl_hexagram.setText("卦象: {}/6".format(hex_info["count"]))
            self.lbl_hexagram.setStyleSheet("font-size: 10px; color: #888; padding: 2px;")
        else:
            self.lbl_hexagram.setText("")

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

    def _on_new_game(self):
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

    def _on_talent_tree(self):
        if self.engine.hero:
            dlg = TalentTreeDialog(self.engine.hero, self)
            dlg.exec_()

    def _on_inventory(self):
        if self.engine.hero:
            dlg = InventoryDialog(self.engine.hero, self)
            dlg.exec_()

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
