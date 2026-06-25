"""暗黑任务栏RPG - 主入口"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from src.ui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 将窗口移动到屏幕右下角（任务栏附近）
    screen = app.primaryScreen().geometry()
    x = screen.width() - window.width() - 10
    y = screen.height() - window.height() - 50
    window.move(x, y)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
