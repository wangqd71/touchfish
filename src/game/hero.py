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
            SLOT_MAIN_HAND: None,
            SLOT_OFF_HAND:  None,
            SLOT_HELMET:    None,
            SLOT_CHEST:     None,
            SLOT_BOOTS:     None,
            SLOT_ACCESSORY: None,
        }

        # 背包（所有获得的装备）
        self.inventory = []

        # 技能系统（必须在current_hp之前初始化）
        self.skill_points = 0
        self.learned_skills = {}  # {skill_id: rank}

        # 天赋系统（使用金币点亮）
        self.learned_talents = {}  # {talent_id: rank}

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

    def _get_talent_bonus(self, stat_key):
        """汇总天赋对某属性的加成"""
        bonus = 0.0
        for branch in TALENT_TREES.values():
            for talent in branch["talents"]:
                rank = self.learned_talents.get(talent["id"], 0)
                if rank > 0 and talent["effect_key"] == stat_key:
                    bonus += talent["effect_per_rank"] * rank
        return bonus

    @property
    def max_hp(self):
        base = self.base_hp + (self.level - 1) * HERO_HP_GROWTH
        equip_bonus = sum(e.hp for e in self.equipment.values() if e)
        mult = 1.0 + self._get_skill_bonus("hp_mult") + self._get_talent_bonus("hp_mult")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "hp_mult": mult += hex_val
        return int((base * self.class_config["hp_mult"] + equip_bonus) * mult)

    @property
    def atk(self):
        base = self.base_atk + (self.level - 1) * HERO_ATK_GROWTH
        equip_bonus = sum(e.atk for e in self.equipment.values() if e)
        mult = 1.0 + self._get_skill_bonus("atk_mult") + self._get_talent_bonus("atk_mult")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "atk_mult": mult += hex_val
        return int((base * self.class_config["atk_mult"] + equip_bonus) * mult)

    @property
    def defense(self):
        base = self.base_def + (self.level - 1) * HERO_DEF_GROWTH
        equip_bonus = sum(e.defense for e in self.equipment.values() if e)
        mult = 1.0 + self._get_skill_bonus("def_mult") + self._get_talent_bonus("def_mult")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "def_mult": mult += hex_val
        return int((base * self.class_config["def_mult"] + equip_bonus) * mult)

    @property
    def speed(self):
        base = self.base_speed
        equip_bonus = sum(e.speed for e in self.equipment.values() if e)
        mult = 1.0 + self._get_skill_bonus("speed_mult") + self._get_talent_bonus("speed_mult")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "speed_mult": mult += hex_val
        return (base * self.class_config["speed_mult"] + equip_bonus) * mult

    @property
    def crit_rate(self):
        base = CRIT_CHANCE + self._get_skill_bonus("crit_rate") + self._get_talent_bonus("crit_rate")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "crit_rate": base += hex_val
        return base

    @property
    def crit_damage_mult(self):
        base = CRIT_DAMAGE_MULT + self._get_skill_bonus("crit_dmg") + self._get_talent_bonus("crit_dmg")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "crit_dmg": base += hex_val
        return base

    @property
    def dodge_rate(self):
        base = DODGE_CHANCE + self._get_skill_bonus("dodge_rate") + self._get_talent_bonus("dodge_rate")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "dodge_rate": base += hex_val
        return base

    @property
    def dmg_mult(self):
        base = 1.0 + self._get_skill_bonus("dmg_mult") + self._get_talent_bonus("dmg_mult")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "dmg_mult": base += hex_val
        return base

    @property
    def exp_mult(self):
        base = 1.0 + self._get_skill_bonus("exp_mult") + self._get_talent_bonus("exp_mult")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "exp_mult": base += hex_val
        return base

    @property
    def gold_mult(self):
        base = 1.0 + self._get_skill_bonus("gold_mult") + self._get_talent_bonus("gold_mult")
        hex_type, hex_val = self.get_hexagram_bonus()
        if hex_type == "gold_mult": base += hex_val
        return base

    @property
    def drop_rate_bonus(self):
        return self._get_talent_bonus("drop_rate")

    @property
    def sell_mult(self):
        return 1.0 + self._get_talent_bonus("sell_mult")

    # ---- 六十四卦系统 ----

    def get_hexagram(self):
        """计算当前装备形成的卦象，返回 (卦名, 符号, 加成类型, 加成数值, 爻列表) 或 None"""
        lines = []
        for slot in SLOT_LINE_ORDER:
            item = self.equipment.get(slot)
            if item and item.yin_yang >= 0:
                lines.append(item.yin_yang)
            else:
                return None  # 任一槽位无阴阳属性则不形成卦象

        # 从下到上组合成6位二进制
        binary = "".join(str(l) for l in lines)
        hexagram = HEXAGRAMS.get(binary)
        if not hexagram:
            return None

        name, symbol, bonus_type, bonus_value = hexagram
        return (name, symbol, bonus_type, bonus_value, lines)

    def get_hexagram_bonus(self):
        """获取卦象加成的属性值，返回 (bonus_type, bonus_value) 或 (None, 0)"""
        result = self.get_hexagram()
        if result:
            _, _, bonus_type, bonus_value, _ = result
            return (bonus_type, bonus_value)
        return (None, 0)

    def get_hexagram_display(self):
        """获取卦象显示信息，返回字典或None"""
        result = self.get_hexagram()
        if not result:
            # 检查有多少件史诗+装备有阴阳属性
            yy_count = sum(1 for slot in SLOT_LINE_ORDER
                          if self.equipment.get(slot) and self.equipment[slot].yin_yang >= 0)
            return {"active": False, "count": yy_count, "total": 6}

        name, symbol, bonus_type, bonus_value, lines = result
        bonus_name = HEXAGRAM_BONUS_NAMES.get(bonus_type, bonus_type)
        bonus_text = "+{:.0f}%".format(bonus_value * 100) if bonus_value > 0 else ""

        # 构建爻线显示（从上到下: 主手→副手→头盔→胸甲→鞋子→饰品）
        line_display = []
        for slot in SLOT_LINE_ORDER:
            item = self.equipment.get(slot)
            yy = item.yin_yang if item else -1
            slot_name = SLOT_NAMES_CN.get(slot, slot)
            if yy == YY_YANG:
                line_display.append((slot_name, YANG_DISPLAY, YANG_DISPLAY))
            elif yy == YY_YIN:
                line_display.append((slot_name, YIN_DISPLAY, YIN_DISPLAY))
            else:
                line_display.append((slot_name, "?", "?"))

        return {
            "active": True,
            "name": name,
            "symbol": symbol,
            "bonus_type": bonus_type,
            "bonus_name": bonus_name,
            "bonus_value": bonus_value,
            "bonus_text": bonus_text,
            "lines": line_display,
        }

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

    def add_to_inventory(self, item):
        """添加装备到背包"""
        self.inventory.append(item)

    def equip_from_inventory(self, index):
        """从背包中装备指定索引的装备，返回被替换的装备"""
        if index < 0 or index >= len(self.inventory):
            return None
        item = self.inventory[index]
        old = self.equip(item)
        self.inventory.pop(index)
        return old

    def sell_from_inventory(self, index):
        """出售背包中指定索引的装备，返回获得的金币"""
        if index < 0 or index >= len(self.inventory):
            return 0
        item = self.inventory[index]
        sell_price = max(1, int(item.sell_price * self.sell_mult))
        self.gold += sell_price
        self.total_gold_earned += sell_price
        self.inventory.pop(index)
        return sell_price

    def sell_batch(self, indices):
        """批量出售背包中指定索引的装备，返回总金币"""
        total = 0
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.inventory):
                item = self.inventory[index]
                price = max(1, int(item.sell_price * self.sell_mult))
                self.gold += price
                self.total_gold_earned += price
                total += price
                self.inventory.pop(index)
        return total

    def merge_equipment(self, indices):
        """合成装备：9件同品级 → 1件更高品级，返回是否成功"""
        if len(indices) != 9:
            return False
        items = []
        for i in indices:
            if i < 0 or i >= len(self.inventory):
                return False
            items.append(self.inventory[i])
        # 检查品级相同
        rarities = set(item.rarity for item in items)
        if len(rarities) != 1:
            return False
        rarity = rarities.pop()
        rarity_order = [RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE,
                        RARITY_EPIC, RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_COSMIC]
        idx = rarity_order.index(rarity)
        if idx >= len(rarity_order) - 1:
            return False  # 已是最高品级
        next_rarity = rarity_order[idx + 1]
        # 计算平均等级，随机部位
        import random
        avg_level = max(1, sum(it.level for it in items) // 9)
        slot = random.choice(SLOT_GROUP_ALL)
        from src.game.equipment import Equipment
        new_item = Equipment.generate(avg_level, slot)
        # 强制设置品级
        new_item = Equipment(new_item.name, slot, next_rarity, avg_level,
                             new_item.hp, new_item.atk, new_item.defense, new_item.speed)
        # 删除材料（从后往前删）
        for i in sorted(indices, reverse=True):
            self.inventory.pop(i)
        self.inventory.append(new_item)
        return True

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

    def get_reset_cost(self):
        """获取技能重置费用"""
        total_rank = sum(self.learned_skills.values())
        return total_rank * self.level * 10

    def reset_skills(self):
        """重置所有技能，返还技能点，消耗金币。返回是否成功"""
        cost = self.get_reset_cost()
        if cost <= 0:
            return False
        if self.gold < cost:
            return False
        self.gold -= cost
        total_rank = sum(self.learned_skills.values())
        self.skill_points += total_rank
        self.learned_skills = {}
        self.current_hp = self.max_hp
        return True

    # ---- 天赋系统 ----

    def get_talent_cost(self, talent_id):
        """获取天赋下一级的费用，返回0表示已满级"""
        current_rank = self.learned_talents.get(talent_id, 0)
        if current_rank >= 5:
            return 0
        return TALENT_COSTS[current_rank]

    def learn_talent(self, talent_id):
        """学习/升级天赋，返回是否成功"""
        target = None
        for branch in TALENT_TREES.values():
            for t in branch["talents"]:
                if t["id"] == talent_id:
                    target = t
                    break
        if not target:
            return False
        current_rank = self.learned_talents.get(talent_id, 0)
        if current_rank >= target["max_rank"]:
            return False
        cost = TALENT_COSTS[current_rank]
        if self.gold < cost:
            return False
        self.gold -= cost
        self.learned_talents[talent_id] = current_rank + 1
        self.current_hp = min(self.current_hp, self.max_hp)
        return True

    def get_talent_info(self):
        """获取天赋树信息（含当前等级和可学习状态）"""
        info = {}
        for bid, branch in TALENT_TREES.items():
            talents_info = []
            for t in branch["talents"]:
                rank = self.learned_talents.get(t["id"], 0)
                cost = TALENT_COSTS[rank] if rank < t["max_rank"] else 0
                can_learn = rank < t["max_rank"] and self.gold >= cost
                talents_info.append({
                    **t,
                    "current_rank": rank,
                    "cost": cost,
                    "can_learn": can_learn,
                })
            info[bid] = {
                "name": branch["name"],
                "icon": branch["icon"],
                "desc": branch["desc"],
                "color": branch["color"],
                "talents": talents_info,
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
            "inventory": [item.get_save_data() for item in self.inventory],
            "skill_points": self.skill_points,
            "learned_skills": self.learned_skills,
            "learned_talents": self.learned_talents,
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
        hero.learned_talents = data.get("learned_talents", {})
        hero.total_kills = data.get("total_kills", 0)
        hero.total_gold_earned = data.get("total_gold_earned", 0)
        hero.highest_stage = data.get("highest_stage", 1)
        for slot, item_data in data.get("equipment", {}).items():
            if item_data:
                hero.equipment[slot] = Equipment.from_save_data(item_data)
        hero.inventory = [Equipment.from_save_data(d) for d in data.get("inventory", [])]
        hero.current_hp = min(data["current_hp"], hero.max_hp)
        return hero
