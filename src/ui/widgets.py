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
        self.setMinimumWidth(100)


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


class MonsterCanvas(QWidget):
    """像素风怪物画布"""

    # 怪物像素图案 (8x8 grid, 0=transparent, 1-9=颜色编号)
    PATTERNS = {
        "暗影史莱姆": [
            [0,0,0,1,1,0,0,0],
            [0,0,1,2,2,1,0,0],
            [0,1,2,3,3,2,1,0],
            [1,2,3,4,4,3,2,1],
            [1,2,3,4,4,3,2,1],
            [0,1,2,3,3,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,0,1,1,0,0,0],
        ],
        "骷髅兵": [
            [0,0,1,1,1,1,0,0],
            [0,1,2,2,2,2,1,0],
            [0,1,3,2,2,3,1,0],
            [0,1,2,2,2,2,1,0],
            [0,0,1,4,4,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,1,1,1,1,0,0],
            [0,1,0,1,1,0,1,0],
        ],
        "蝙蝠": [
            [1,0,0,0,0,0,0,1],
            [1,1,0,0,0,0,1,1],
            [1,2,1,0,0,1,2,1],
            [1,2,2,1,1,2,2,1],
            [0,1,2,3,3,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "狼人": [
            [0,1,0,0,0,0,1,0],
            [1,2,1,0,0,1,2,1],
            [1,2,2,1,1,2,2,1],
            [0,1,3,2,2,3,1,0],
            [0,1,2,4,4,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,1,2,2,1,0,0],
            [0,1,1,0,0,1,1,0],
        ],
        "暗影骑士": [
            [0,0,1,1,1,1,0,0],
            [0,1,2,3,3,2,1,0],
            [0,1,3,4,4,3,1,0],
            [0,0,1,2,2,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,2,1,1,1,1,2,1],
            [1,2,0,1,1,0,2,1],
            [0,1,0,1,1,0,1,0],
        ],
        "岩石傀儡": [
            [0,1,1,1,1,1,1,0],
            [1,2,2,2,2,2,2,1],
            [1,2,3,2,2,3,2,1],
            [1,2,2,2,2,2,2,1],
            [1,2,2,3,3,2,2,1],
            [0,1,2,2,2,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,1,1,1,1,0,0],
        ],
        "毒蝎": [
            [0,0,0,0,0,0,1,0],
            [0,0,0,0,0,1,2,1],
            [0,1,0,0,0,0,1,0],
            [1,2,1,1,1,1,0,0],
            [0,1,2,3,2,1,0,0],
            [0,0,1,2,1,0,0,0],
            [0,1,0,0,0,1,0,0],
            [1,0,0,0,0,0,1,0],
        ],
        "洞穴巨蛛": [
            [1,0,0,0,0,0,0,1],
            [0,1,0,0,0,0,1,0],
            [0,1,1,1,1,1,1,0],
            [1,2,3,2,2,3,2,1],
            [0,1,2,2,2,2,1,0],
            [0,1,1,1,1,1,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,1,1,0,0,1],
        ],
        "矮人矿工": [
            [0,0,1,1,1,1,0,0],
            [0,1,2,2,2,2,1,0],
            [0,1,3,2,2,3,1,0],
            [0,1,2,4,4,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,1,2,2,2,2,1,0],
            [0,1,0,2,2,0,1,0],
            [0,1,0,1,1,0,1,0],
        ],
        "水晶魔像": [
            [0,0,1,2,2,1,0,0],
            [0,1,2,3,3,2,1,0],
            [1,2,3,4,4,3,2,1],
            [1,2,3,4,4,3,2,1],
            [0,1,2,3,3,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,1,0,0,1,0,0],
            [0,1,1,0,0,1,1,0],
        ],
        "恶魔侍卫": [
            [1,0,0,0,0,0,0,1],
            [1,1,0,0,0,0,1,1],
            [0,1,2,2,2,2,1,0],
            [0,1,3,2,2,3,1,0],
            [0,1,2,4,4,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,2,0,1,1,0,2,1],
        ],
        "堕落天使": [
            [1,1,0,0,0,0,1,1],
            [1,2,1,0,0,1,2,1],
            [0,1,2,1,1,2,1,0],
            [0,1,2,3,3,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,1,1,2,2,1,1,0],
            [1,2,0,1,1,0,2,1],
            [1,0,0,0,0,0,0,1],
        ],
        "死灵法师": [
            [0,0,1,1,1,1,0,0],
            [0,1,2,3,3,2,1,0],
            [0,1,3,4,4,3,1,0],
            [0,1,2,2,2,2,1,0],
            [0,0,1,4,4,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,0,0,1,1,0,0,1],
            [1,0,0,1,1,0,0,1],
        ],
        "地狱犬": [
            [1,1,0,0,0,0,1,1],
            [1,2,1,0,0,1,2,1],
            [0,1,2,2,2,2,1,0],
            [0,1,3,4,4,3,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,1,2,2,1,0,0],
            [0,0,1,0,0,1,0,0],
            [0,1,1,0,0,1,1,0],
        ],
        "魔王": [
            [1,0,0,1,1,0,0,1],
            [1,1,0,1,1,0,1,1],
            [0,1,2,3,3,2,1,0],
            [0,1,3,4,4,3,1,0],
            [0,1,2,5,5,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,2,1,0,0,1,2,1],
        ],
    }

    # 颜色映射
    COLORS = {
        1: "#333333",  # 深灰轮廓
        2: "#666666",  # 灰色主体
        3: "#FF4444",  # 红色眼睛
        4: "#FFAA00",  # 金色高光
        5: "#AA0000",  # 暗红
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self.monster_name = ""
        self._get_fallback_pattern()

    def _get_fallback_pattern(self):
        """没有匹配图案时的默认图案"""
        self.pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,2,2,2,2,1,0],
            [0,1,2,3,3,2,1,0],
            [0,1,2,2,2,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ]

    def set_monster(self, name):
        self.monster_name = name
        self.pattern = self.PATTERNS.get(name, self.PATTERNS.get("暗影史莱姆"))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # 背景
        painter.fillRect(self.rect(), QColor("#0d0d1a"))

        # 绘制像素
        pixel_size = 7
        offset_x = (self.width() - 8 * pixel_size) // 2
        offset_y = (self.height() - 8 * pixel_size) // 2

        for y, row in enumerate(self.pattern):
            for x, val in enumerate(row):
                if val > 0:
                    color = self.COLORS.get(val, "#555555")
                    painter.fillRect(
                        offset_x + x * pixel_size,
                        offset_y + y * pixel_size,
                        pixel_size - 1,
                        pixel_size - 1,
                        QColor(color)
                    )
        painter.end()


class MonsterWidget(QWidget):
    """怪物显示控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(10)

        # 像素怪物
        self.canvas = MonsterCanvas()
        layout.addWidget(self.canvas)

        # 右侧信息
        right = QVBoxLayout()
        right.setSpacing(2)
        right.setContentsMargins(0, 2, 4, 2)

        self.name_label = QLabel("等待怪物...")
        self.name_label.setStyleSheet("""
            QLabel {
                color: #FF6666;
                font-size: 14px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        self.name_label.setMinimumHeight(20)
        right.addWidget(self.name_label)

        self.hp_bar = DarkProgressBar("#FF4444")
        self.hp_bar.setFixedHeight(18)
        right.addWidget(self.hp_bar)

        right.addStretch()

        layout.addLayout(right, 1)

    def update_monster(self, monster):
        """更新怪物显示"""
        if monster:
            self.name_label.setText(monster.name + " Lv." + str(monster.level))
            self.hp_bar.setValue(int(monster.hp_percent * 100))
            self.canvas.set_monster(monster.name)
        else:
            self.name_label.setText("等待怪物...")
            self.hp_bar.setValue(0)
            self.canvas.set_monster("")
