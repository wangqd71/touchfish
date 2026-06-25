"""英雄系统 - 扩展版（含技能树和技能点）"""
from src.utils.constants import *


class Hero:
    """英雄角色类"""

    def __init__(self, name="无名英雄", hero_class=CLASS_WARRIOR):
        self.name = name
        self.hero_class = hero_class
        self.level = 1
        self.exp = 0
        self.gold = 0

        # 基础属性
        self.base_hp = HERO_BASE_HP
        self.base_atk = HERO_BASE_ATK
        self.base_def = HERO_BASE_DEF
        self.base_speed = HERO_BASE_SPEED

        # 装备（必须在current_hp之前初始化）
        self.equipment = {
            SLOT_WEAPON: None,
            SLOT_ARMOR: None,
            SLOT_ACCESSORY: None,
        }

        # 技能系统（必须在current_hp之前初始化）
        self.skill_points = 0
        self.learned_skills = {}  # {skill_id: rank}

        # 当前状态
        self.current_hp = self.max_hp

        # 统计
        self.total_kills = 0
        self.total_gold_earned = 0
        self.highest_stage = 1

    @property
    def class_config(self):
        return HERO_CLASSES[self.hero_class]

    # ---- 带技能加成的属性计算 ----

    def _get_skill_bonus(self, stat_key):
        """汇总已学技能对某属性的加成"""
        bonus = 0.0
        tree = SKILL_TREES.get(self.hero_class)
        if not tree:
            return bonus
        for branch in tree["branches"].values():
            for skill in branch["skills"]:
                rank = self.learned_skills.get(skill["id"], 0)
                if rank > 0:
                    bonus += skill["effect"].get(stat_key, 0) * rank
        return bonus

    @property
    def max_hp(self):
        base = self.base_hp + (self.level - 1) * HERO_HP_GROWTH
        equip_bonus = sum(e.hp for e in self.equipment.values() if e)
        skill_mult = 1.0 + self._get_skill_bonus("hp_mult")
        return int((base * self.class_config["hp_mult"] + equip_bonus) * skill_mult)

    @property
    def atk(self):
        base = self.base_atk + (self.level - 1) * HERO_ATK_GROWTH
        equip_bonus = sum(e.atk for e in self.equipment.values() if e)
        skill_mult = 1.0 + self._get_skill_bonus("atk_mult")
        return int((base * self.class_config["atk_mult"] + equip_bonus) * skill_mult)

    @property
    def defense(self):
        base = self.base_def + (self.level - 1) * HERO_DEF_GROWTH
        equip_bonus = sum(e.defense for e in self.equipment.values() if e)
        skill_mult = 1.0 + self._get_skill_bonus("def_mult")
        return int((base * self.class_config["def_mult"] + equip_bonus) * skill_mult)

    @property
    def speed(self):
        base = self.base_speed
        equip_bonus = sum(e.speed for e in self.equipment.values() if e)
        skill_mult = 1.0 + self._get_skill_bonus("speed_mult")
        return (base * self.class_config["speed_mult"] + equip_bonus) * skill_mult

    @property
    def crit_rate(self):
        return CRIT_CHANCE + self._get_skill_bonus("crit_rate")

    @property
    def crit_damage_mult(self):
        return CRIT_DAMAGE_MULT + self._get_skill_bonus("crit_dmg")

    @property
    def dodge_rate(self):
        return DODGE_CHANCE + self._get_skill_bonus("dodge_rate")

    @property
    def dmg_mult(self):
        return 1.0 + self._get_skill_bonus("dmg_mult")

    @property
    def dmg_reduce(self):
        return self._get_skill_bonus("dmg_reduce")

    @property
    def exp_mult(self):
        return 1.0 + self._get_skill_bonus("exp_mult")

    @property
    def gold_mult(self):
        return 1.0 + self._get_skill_bonus("gold_mult")

    # ---- 等级与经验 ----

    @property
    def exp_to_level(self):
        # 混合公式：指数(早期快) + 多项式(后期慢，Lv10后开始)
        exp = EXP_BASE * (EXP_GROWTH_RATE ** (self.level - 1))
        if self.level > 10:
            exp += EXP_POLY_FACTOR * ((self.level - 10) ** 2)
        return int(exp)

    @property
    def exp_progress(self):
        return self.exp / self.exp_to_level if self.exp_to_level > 0 else 0

    @property
    def hp_percent(self):
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0

    @property
    def is_alive(self):
        return self.current_hp > 0

    @property
    def available_skill_points(self):
        return self.skill_points

    def gain_exp(self, amount):
        """获得经验（含加成），返回升级次数"""
        actual = int(amount * self.exp_mult)
        level_ups = 0
        self.exp += actual
        while self.exp >= self.exp_to_level and self.level < MAX_LEVEL:
            self.exp -= self.exp_to_level
            self.level += 1
            self.skill_points += SKILL_POINT_PER_LEVEL
            self.current_hp = self.max_hp  # 升级回满血
            level_ups += 1
        # 溢出经验清零
        if self.level >= MAX_LEVEL:
            self.exp = 0
        return level_ups

    def gain_gold(self, amount):
        actual = int(amount * self.gold_mult)
        self.gold += actual
        self.total_gold_earned += actual

    def take_damage(self, damage):
        """受到伤害（含减伤） - 防御已在calculate_damage中扣除"""
        reduced = damage * (1.0 - self.dmg_reduce)
        actual = max(1, int(reduced))
        self.current_hp = max(0, self.current_hp - actual)
        return actual

    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def equip(self, item):
        slot = item.slot
        old = self.equipment[slot]
        self.equipment[slot] = item
        self.current_hp = min(self.current_hp, self.max_hp)
        return old

    # ---- 技能系统 ----

    def learn_skill(self, skill_id):
        """学习/升级技能，返回是否成功"""
        tree = SKILL_TREES.get(self.hero_class)
        if not tree:
            return False

        # 查找技能
        target_skill = None
        for branch in tree["branches"].values():
            for skill in branch["skills"]:
                if skill["id"] == skill_id:
                    target_skill = skill
                    break

        if not target_skill:
            return False

        current_rank = self.learned_skills.get(skill_id, 0)

        # 检查条件
        if current_rank >= target_skill["max_rank"]:
            return False  # 已满级
        if self.skill_points <= 0:
            return False  # 没有技能点
        if self.level < target_skill["req_level"]:
            return False  # 等级不够

        # 学习
        self.learned_skills[skill_id] = current_rank + 1
        self.skill_points -= 1

        # 学习后回满血（可能提升了血量上限）
        self.current_hp = self.max_hp
        return True

    def get_skill_rank(self, skill_id):
        return self.learned_skills.get(skill_id, 0)

    def get_skill_tree_info(self):
        """获取当前职业的技能树信息"""
        tree = SKILL_TREES.get(self.hero_class)
        if not tree:
            return None

        info = {"name": tree["name"], "branches": {}}
        for bname, branch in tree["branches"].items():
            skills_info = []
            for skill in branch["skills"]:
                rank = self.learned_skills.get(skill["id"], 0)
                can_learn = (
                    rank < skill["max_rank"]
                    and self.skill_points > 0
                    and self.level >= skill["req_level"]
                )
                skills_info.append({
                    **skill,
                    "current_rank": rank,
                    "can_learn": can_learn,
                })
            info["branches"][bname] = {
                "desc": branch["desc"],
                "skills": skills_info,
            }
        return info

    # ---- 存档 ----

    def get_save_data(self):
        return {
            "name": self.name,
            "hero_class": self.hero_class,
            "level": self.level,
            "exp": self.exp,
            "gold": self.gold,
            "current_hp": self.current_hp,
            "equipment": {slot: item.get_save_data() if item else None
                          for slot, item in self.equipment.items()},
            "skill_points": self.skill_points,
            "learned_skills": self.learned_skills,
            "total_kills": self.total_kills,
            "total_gold_earned": self.total_gold_earned,
            "highest_stage": self.highest_stage,
        }

    @classmethod
    def from_save_data(cls, data):
        from src.game.equipment import Equipment
        hero = cls(data["name"], data["hero_class"])
        hero.level = data["level"]
        hero.exp = data["exp"]
        hero.gold = data["gold"]
        hero.skill_points = data.get("skill_points", 0)
        hero.learned_skills = data.get("learned_skills", {})
        hero.total_kills = data.get("total_kills", 0)
        hero.total_gold_earned = data.get("total_gold_earned", 0)
        hero.highest_stage = data.get("highest_stage", 1)
        for slot, item_data in data.get("equipment", {}).items():
            if item_data:
                hero.equipment[slot] = Equipment.from_save_data(item_data)
        hero.current_hp = min(data["current_hp"], hero.max_hp)
        return hero
