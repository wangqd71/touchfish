"""存档管理器"""
import json
import os
from pathlib import Path


class SaveManager:
    """存档管理"""

    def __init__(self, save_dir="saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.save_file = self.save_dir / "savegame.json"

    def save(self, data):
        """保存数据"""
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False

    def load(self):
        """加载数据"""
        try:
            if self.save_file.exists():
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载失败: {e}")
        return None

    def has_save(self):
        """检查是否有存档"""
        return self.save_file.exists()

    def delete_save(self):
        """删除存档"""
        if self.save_file.exists():
            self.save_file.unlink()
