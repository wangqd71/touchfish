"""游戏引擎 - 难度+章节+关卡系统"""
import time
from src.utils.constants import *
from src.game.hero import Hero
from src.game.monster import Monster
from src.game.combat import CombatEngine
from src.game.loot import LootTable


class GameState:
    IDLE = "idle"
    COMBAT = "combat"
    BOSS = "boss"
    DEAD = "dead"


class GameEngine:

    def __init__(self):
        self.hero = None
        self.current_monster = None
        self.state = GameState.IDLE
        self.stage = 1               # 绝对关卡 1-100
        self.stage_progress = 0      # 当前关卡击杀数 0-MONSTERS_PER_STAGE
        self.difficulty = DIFF_NORMAL
        self.chapter = CHAPTER_1

        self.combat_log = []
        self.max_log = 20

        self.total_play_time = 0
        self.session_start = time.time()

        self.on_combat = None
        self.on_loot = None
        self.on_level_up = None
        self.on_stage_clear = None

    # ---- 难度/章节计算 ----

    @staticmethod
    def get_difficulty(stage):
        """Stage 1-33: Normal, 34-66: Nightmare, 67-100: Hell"""
        if stage <= 33:
            return DIFF_NORMAL
        elif stage <= 66:
            return DIFF_NIGHTMARE
        else:
            return DIFF_HELL

    @staticmethod
    def get_chapter(stage):
        """每10关一个章节，3章循环"""
        local = (stage - 1) % 10    # 当前难度内的进度 0-9
        idx = ((stage - 1) // 10) % 3
        chapters = [CHAPTER_1, CHAPTER_2, CHAPTER_3]
        return chapters[idx]

    def get_chapter_name(self):
        return CHAPTERS.get(self.chapter, {}).get("name", "未知")

    def get_difficulty_name(self):
        return DIFFICULTIES.get(self.difficulty, {}).get("name", "普通")

    # ---- 游戏流程 ----

    def new_game(self, name="无名英雄", hero_class=CLASS_WARRIOR):
        self.hero = Hero(name, hero_class)
        self.stage = 1
        self.stage_progress = 0
        self.difficulty = DIFF_NORMAL
        self.chapter = CHAPTER_1
        self.state = GameState.IDLE
        self.log("{} 开始冒险！".format(name))

    def update(self):
        if not self.hero or not self.hero.is_alive:
            self.state = GameState.DEAD
            return
        if self.state == GameState.DEAD:
            return
        if self.state in (GameState.IDLE, GameState.COMBAT, GameState.BOSS):
            self._auto_combat()

    def _auto_combat(self):
        if not self.hero.is_alive:
            self.state = GameState.DEAD
            return

        # 生成怪物
        if not self.current_monster or not self.current_monster.is_alive:
            self._spawn_next_monster()
            return

        # 执行战斗
        result = CombatEngine.battle(self.hero, self.current_monster)

        if result.victory:
            monster_name = self.current_monster.name
            self.log("击败 {}！经验+{} 金币+{}".format(monster_name, result.exp_gained, result.gold_gained))

            if result.crit_hits > 0:
                self.log("暴击 {} 次！".format(result.crit_hits))

            # 掉落
            is_boss = self.state == GameState.BOSS
            loot = LootTable.roll(self.stage, is_boss, self.chapter)
            for item in loot.items:
                self.log("获得 [{}] {}!".format(item.rarity_name, item.name))
                self._auto_equip(item)

            # 升级
            if result.level_ups > 0:
                self.log("升级！当前等级: {}".format(self.hero.level))

            # 更新进度
            if self.state == GameState.BOSS:
                self._advance_stage()
            else:
                self.stage_progress += 1
                if self.stage_progress >= MONSTERS_PER_STAGE:
                    self.state = GameState.BOSS
                    self.log("Boss 出现了！[{}关]".format(self.stage))

            if self.on_combat:
                self.on_combat(result)
        else:
            self.log("被 {} 击败...".format(self.current_monster.name))
            self.state = GameState.DEAD

        self.current_monster = None

    def _spawn_next_monster(self):
        if self.state == GameState.BOSS:
            self.current_monster = Monster.generate_boss(self.stage, self.difficulty)
        else:
            self.current_monster = Monster.generate(self.stage, self.difficulty)
        self.state = GameState.COMBAT if self.state != GameState.BOSS else GameState.BOSS

    def _advance_stage(self):
        self.stage += 1
        self.stage_progress = 0
        self.state = GameState.IDLE

        self.difficulty = self.get_difficulty(self.stage)
        new_chapter = self.get_chapter(self.stage)

        if new_chapter != self.chapter:
            self.chapter = new_chapter

        # 记录最高关卡
        if self.stage > self.hero.highest_stage:
            self.hero.highest_stage = self.stage

        diff_name = self.get_difficulty_name()
        ch_name = self.get_chapter_name()
        self.log("[{}] 进入第 {} 关 - {} | {}".format(diff_name, self.stage, ch_name, self.stage_progress))

    def _auto_equip(self, item):
        current = self.hero.equipment.get(item.slot)
        if current is None or item.total_stats > current.total_stats:
            old = self.hero.equip(item)
            if old:
                self.log("替换 [{}] {}".format(old.rarity_name, old.name))
            self.log("装备 [{}] {}".format(item.rarity_name, item.name))

    def resurrect(self):
        if self.hero and not self.hero.is_alive:
            self.hero.current_hp = self.hero.max_hp
            self.state = GameState.IDLE
            self.current_monster = None
            self.stage_progress = 0
            gold_loss = self.hero.gold // 10
            self.hero.gold -= gold_loss
            self.log("复活！损失 {} 金币".format(gold_loss))

    def log(self, message):
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log:
            self.combat_log.pop(0)

    def get_save_data(self):
        return {
            "hero": self.hero.get_save_data() if self.hero else None,
            "stage": self.stage,
            "difficulty": self.difficulty,
            "chapter": self.chapter,
            "stage_progress": self.stage_progress,
            "total_play_time": self.total_play_time + (time.time() - self.session_start),
        }

    def load_save_data(self, data):
        if data.get("hero"):
            self.hero = Hero.from_save_data(data["hero"])
            self.stage = data.get("stage", 1)
            self.difficulty = data.get("difficulty", DIFF_NORMAL)
            self.chapter = data.get("chapter", CHAPTER_1)
            self.stage_progress = data.get("stage_progress", 0)
            self.total_play_time = data.get("total_play_time", 0)
            self.session_start = time.time()
            self.state = GameState.IDLE
            self.log("存档加载成功！{} Lv.{}".format(self.hero.name, self.hero.level))
            return True
        return False
