"""自定义UI控件"""
from PyQt5.QtWidgets import QProgressBar, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QLinearGradient, QFont


class DarkProgressBar(QProgressBar):
    """暗黑风格进度条"""

    def __init__(self, color="#FF4444", parent=None):
        super().__init__(parent)
        self.bar_color = QColor(color)
        self.setTextVisible(False)
        self.setFixedHeight(16)
        self._update_style()

    def setBarColor(self, color):
        self.bar_color = QColor(color)
        self._update_style()

    def _update_style(self):
        r, g, b = self.bar_color.red(), self.bar_color.green(), self.bar_color.blue()
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1a1a2e;
                border: 1px solid #333;
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: rgb({r}, {g}, {b});
                border-radius: 2px;
            }}
        """)


class StatLabel(QLabel):
    """属性标签"""

    def __init__(self, icon="", text="", color="#CCCCCC", parent=None):
        super().__init__(parent)
        self.setText(f"{icon} {text}")
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                padding: 2px;
            }}
        """)
        self.setFont(QFont("Microsoft YaHei", 9))


class DarkWidget(QWidget):
    """暗黑风格基础控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d1a;
                color: #CCCCCC;
            }
        """)


class BattleLogWidget(QLabel):
    """战斗日志控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_lines = []
        self.max_lines = 8
        self.setStyleSheet("""
            QLabel {
                background-color: #0d0d1a;
                color: #888;
                font-size: 10px;
                padding: 4px;
                border: 1px solid #222;
                border-radius: 4px;
            }
        """)
        self.setFont(QFont("Microsoft YaHei", 8))
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

    def add_log(self, message):
        """添加日志"""
        self.log_lines.append(message)
        if len(self.log_lines) > self.max_lines:
            self.log_lines.pop(0)
        self.setText("\n".join(self.log_lines))
        # 滚动到底部
        self.repaint()

    def set_logs(self, messages):
        """设置全部日志"""
        self.log_lines = messages[-self.max_lines:]
        self.setText("\n".join(self.log_lines))


class MonsterWidget(QWidget):
    """怪物显示控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 怪物名称和emoji
        self.name_label = QLabel("等待怪物...")
        self.name_label.setStyleSheet("""
            QLabel {
                color: #FF6666;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)

        # 怪物血条
        self.hp_bar = DarkProgressBar("#FF4444")
        layout.addWidget(self.hp_bar)

    def update_monster(self, monster):
        """更新怪物显示"""
        if monster:
            self.name_label.setText(f"{monster.emoji} {monster.name} Lv.{monster.level}")
            self.hp_bar.setValue(int(monster.hp_percent * 100))
        else:
            self.name_label.setText("等待怪物...")
            self.hp_bar.setValue(0)
