"""游戏常量定义 - 扩展版"""

# ============================================================
# 窗口设置
# ============================================================
WINDOW_TITLE = "暗黑任务栏RPG"
WINDOW_WIDTH = 360
WINDOW_HEIGHT = 640
TASKBAR_HEIGHT = 40

# 游戏循环
TICK_RATE = 2000        # 毫秒（2秒一战斗，idle节奏）
AUTO_SAVE_INTERVAL = 60000

# ============================================================
# 等级系统
# ============================================================
MAX_LEVEL = 100
EXP_BASE = 200
EXP_GROWTH_RATE = 1.08
EXP_POLY_FACTOR = 200       # 等级^2的多项式系数，Lv10后开始生效
SKILL_POINT_PER_LEVEL = 1       # 每级获得1技能点
MILESTONE_LEVELS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # 节点等级

# 英雄基础属性
HERO_BASE_HP = 160
HERO_BASE_ATK = 15
HERO_BASE_DEF = 8
HERO_BASE_SPEED = 1.0
HERO_HP_GROWTH = 18
HERO_ATK_GROWTH = 4
HERO_DEF_GROWTH = 2.5

# ============================================================
# 职业定义
# ============================================================
CLASS_WARRIOR  = "warrior"    # 战士
CLASS_MAGE     = "mage"       # 法师
CLASS_RANGER   = "ranger"     # 游侠
CLASS_KNIGHT   = "knight"     # 骑士
CLASS_PRIEST   = "priest"     # 牧师
CLASS_ASSASSIN = "assassin"   # 刺客

HERO_CLASSES = {
    CLASS_WARRIOR: {
        "name": "战士",
        "icon": "⚔️",
        "hp_mult": 1.2,  "atk_mult": 1.1,  "def_mult": 1.1,  "speed_mult": 1.0,
        "desc": "攻守均衡的近战先锋",
        "primary_stat": "atk",
    },
    CLASS_MAGE: {
        "name": "法师",
        "icon": "🔮",
        "hp_mult": 0.9,  "atk_mult": 1.5,  "def_mult": 0.7,  "speed_mult": 1.0,
        "desc": "高爆发远程魔法输出",
        "primary_stat": "atk",
    },
    CLASS_RANGER: {
        "name": "游侠",
        "icon": "🏹",
        "hp_mult": 0.95, "atk_mult": 1.2,  "def_mult": 0.85, "speed_mult": 1.4,
        "desc": "灵活高速的远程射手",
        "primary_stat": "speed",
    },
    CLASS_KNIGHT: {
        "name": "骑士",
        "icon": "🛡️",
        "hp_mult": 1.5,  "atk_mult": 0.85, "def_mult": 1.5,  "speed_mult": 0.8,
        "desc": "坚不可摧的钢铁堡垒",
        "primary_stat": "def",
    },
    CLASS_PRIEST: {
        "name": "牧师",
        "icon": "✝️",
        "hp_mult": 1.1,  "atk_mult": 0.8,  "def_mult": 1.0,  "speed_mult": 1.0,
        "desc": "神圣治愈与持续作战",
        "primary_stat": "hp",
    },
    CLASS_ASSASSIN: {
        "name": "刺客",
        "icon": "🗡️",
        "hp_mult": 0.85, "atk_mult": 1.4,  "def_mult": 0.7,  "speed_mult": 1.6,
        "desc": "一击必杀的暗影杀手",
        "primary_stat": "atk",
    },
}

# ============================================================
# 技能树系统
# ============================================================
# 每个职业有 3 条分支，每条分支 5 个技能（共15个技能/职业）
# 技能需要前置技能和等级才能解锁

SKILL_TREES = {
    CLASS_WARRIOR: {
        "name": "战士技能树",
        "branches": {
            "狂暴": {
                "desc": "追求极致攻击力",
                "skills": [
                    {"id": "w_berserk_1",    "name": "狂暴打击",   "desc": "攻击+15%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"atk_mult": 0.03}},
                    {"id": "w_berserk_2",    "name": "血怒",       "desc": "暴击率+5%",      "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"crit_rate": 0.01}},
                    {"id": "w_berserk_3",    "name": "旋风斩",     "desc": "攻击+25%",       "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"atk_mult": 0.05}},
                    {"id": "w_berserk_4",    "name": "嗜血狂怒",   "desc": "暴击伤害+15%",   "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"crit_dmg": 0.03}},
                    {"id": "w_berserk_5",    "name": "灭世之力",   "desc": "全伤害+20%",     "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"dmg_mult": 0.067}},
                ],
            },
            "坚韧": {
                "desc": "提升生存能力",
                "skills": [
                    {"id": "w_guard_1",      "name": "铁壁",       "desc": "防御+10%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"def_mult": 0.02}},
                    {"id": "w_guard_2",      "name": "生命强化",   "desc": "生命+10%",       "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"hp_mult": 0.02}},
                    {"id": "w_guard_3",      "name": "战吼",       "desc": "减伤+5%",        "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"dmg_reduce": 0.01}},
                    {"id": "w_guard_4",      "name": "不屈意志",   "desc": "生命+20%",       "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"hp_mult": 0.04}},
                    {"id": "w_guard_5",      "name": "钢铁之躯",   "desc": "减伤+15%",       "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"dmg_reduce": 0.05}},
                ],
            },
            "战意": {
                "desc": "综合战斗技巧",
                "skills": [
                    {"id": "w_will_1",       "name": "战斗本能",   "desc": "攻击+5% 防御+5%","type": "passive", "max_rank": 5, "req_level": 5,  "effect": {"atk_mult": 0.01, "def_mult": 0.01}},
                    {"id": "w_will_2",       "name": "战意昂扬",   "desc": "经验+8%",        "type": "passive", "max_rank": 5, "req_level": 15, "effect": {"exp_mult": 0.016}},
                    {"id": "w_will_3",       "name": "武器精通",   "desc": "攻击+15%",       "type": "passive", "max_rank": 5, "req_level": 30, "effect": {"atk_mult": 0.03}},
                    {"id": "w_will_4",       "name": "战神附体",   "desc": "暴击率+8%",      "type": "passive", "max_rank": 5, "req_level": 50, "effect": {"crit_rate": 0.016}},
                    {"id": "w_will_5",       "name": "不败战神",   "desc": "全属性+10%",     "type": "passive", "max_rank": 3, "req_level": 80, "effect": {"atk_mult": 0.033, "def_mult": 0.033, "hp_mult": 0.033}},
                ],
            },
        },
    },

    CLASS_MAGE: {
        "name": "法师技能树",
        "branches": {
            "元素": {
                "desc": "掌控元素之力",
                "skills": [
                    {"id": "m_elem_1",      "name": "火焰掌握",   "desc": "攻击+15%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"atk_mult": 0.03}},
                    {"id": "m_elem_2",      "name": "冰霜之触",   "desc": "减伤+5%",        "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"dmg_reduce": 0.01}},
                    {"id": "m_elem_3",      "name": "雷电风暴",   "desc": "暴击率+5%",      "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"crit_rate": 0.01}},
                    {"id": "m_elem_4",      "name": "元素融合",   "desc": "攻击+25%",       "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"atk_mult": 0.05}},
                    {"id": "m_elem_5",      "name": "毁灭洪流",   "desc": "全伤害+20%",     "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"dmg_mult": 0.067}},
                ],
            },
            "奥术": {
                "desc": "奥术能量强化",
                "skills": [
                    {"id": "m_arcane_1",     "name": "魔力涌动",   "desc": "攻击+10%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"atk_mult": 0.02}},
                    {"id": "m_arcane_2",     "name": "法力护盾",   "desc": "防御+10%",       "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"def_mult": 0.02}},
                    {"id": "m_arcane_3",     "name": "奥术智慧",   "desc": "经验+10%",       "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"exp_mult": 0.02}},
                    {"id": "m_arcane_4",     "name": "能量爆发",   "desc": "暴击伤害+15%",   "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"crit_dmg": 0.03}},
                    {"id": "m_arcane_5",     "name": "大魔导师",   "desc": "攻击+30%",       "type": "passive", "max_rank": 3, "req_level": 80, "effect": {"atk_mult": 0.1}},
                ],
            },
            "神秘": {
                "desc": "神秘力量加持",
                "skills": [
                    {"id": "m_myst_1",       "name": "神秘之光",   "desc": "生命+10%",       "type": "passive", "max_rank": 5, "req_level": 5,  "effect": {"hp_mult": 0.02}},
                    {"id": "m_myst_2",       "name": "冥想",       "desc": "攻击+8% 防御+8%","type": "passive", "max_rank": 5, "req_level": 15, "effect": {"atk_mult": 0.016, "def_mult": 0.016}},
                    {"id": "m_myst_3",       "name": "元素亲和",   "desc": "暴击率+8%",      "type": "passive", "max_rank": 5, "req_level": 30, "effect": {"crit_rate": 0.016}},
                    {"id": "m_myst_4",       "name": "时间扭曲",   "desc": "速度+20%",       "type": "passive", "max_rank": 5, "req_level": 50, "effect": {"speed_mult": 0.04}},
                    {"id": "m_myst_5",       "name": "禁咒·末日",  "desc": "全属性+10%",     "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"atk_mult": 0.033, "def_mult": 0.033, "hp_mult": 0.033}},
                ],
            },
        },
    },

    CLASS_RANGER: {
        "name": "游侠技能树",
        "branches": {
            "精准": {
                "desc": "精准射击与暴击",
                "skills": [
                    {"id": "r_prec_1",      "name": "精准瞄准",   "desc": "暴击率+5%",      "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"crit_rate": 0.01}},
                    {"id": "r_prec_2",      "name": "穿透射击",   "desc": "攻击+10%",       "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"atk_mult": 0.02}},
                    {"id": "r_prec_3",      "name": "致命一击",   "desc": "暴击伤害+15%",   "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"crit_dmg": 0.03}},
                    {"id": "r_prec_4",      "name": "连珠箭",     "desc": "攻击+20%",       "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"atk_mult": 0.04}},
                    {"id": "r_prec_5",      "name": "神射手",     "desc": "暴击率+15%",     "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"crit_rate": 0.05}},
                ],
            },
            "疾风": {
                "desc": "速度与闪避",
                "skills": [
                    {"id": "r_wind_1",       "name": "疾风步",     "desc": "速度+10%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"speed_mult": 0.02}},
                    {"id": "r_wind_2",       "name": "闪避本能",   "desc": "闪避率+3%",      "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"dodge_rate": 0.006}},
                    {"id": "r_wind_3",       "name": "疾风连射",   "desc": "速度+15%",       "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"speed_mult": 0.03}},
                    {"id": "r_wind_4",       "name": "幻影步",     "desc": "闪避率+8%",      "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"dodge_rate": 0.016}},
                    {"id": "r_wind_5",       "name": "风暴之眼",   "desc": "速度+30%",       "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"speed_mult": 0.1}},
                ],
            },
            "自然": {
                "desc": "自然之力加持",
                "skills": [
                    {"id": "r_nat_1",        "name": "自然亲和",   "desc": "生命+8%",        "type": "passive", "max_rank": 5, "req_level": 5,  "effect": {"hp_mult": 0.016}},
                    {"id": "r_nat_2",        "name": "野性本能",   "desc": "攻击+8% 速度+5%","type": "passive", "max_rank": 5, "req_level": 15, "effect": {"atk_mult": 0.016, "speed_mult": 0.01}},
                    {"id": "r_nat_3",        "name": "自然庇护",   "desc": "防御+15%",       "type": "passive", "max_rank": 5, "req_level": 30, "effect": {"def_mult": 0.03}},
                    {"id": "r_nat_4",        "name": "大地之力",   "desc": "生命+20%",       "type": "passive", "max_rank": 5, "req_level": 50, "effect": {"hp_mult": 0.04}},
                    {"id": "r_nat_5",        "name": "万物归一",   "desc": "全属性+10%",     "type": "passive", "max_rank": 3, "req_level": 80, "effect": {"atk_mult": 0.033, "def_mult": 0.033, "hp_mult": 0.033}},
                ],
            },
        },
    },

    CLASS_KNIGHT: {
        "name": "骑士技能树",
        "branches": {
            "守护": {
                "desc": "守护与防御",
                "skills": [
                    {"id": "k_guard_1",      "name": "坚守阵地",   "desc": "防御+15%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"def_mult": 0.03}},
                    {"id": "k_guard_2",      "name": "圣盾术",     "desc": "减伤+5%",        "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"dmg_reduce": 0.01}},
                    {"id": "k_guard_3",      "name": "钢铁堡垒",   "desc": "生命+15%",       "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"hp_mult": 0.03}},
                    {"id": "k_guard_4",      "name": "神圣守护",   "desc": "减伤+10%",       "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"dmg_reduce": 0.02}},
                    {"id": "k_guard_5",      "name": "不灭之盾",   "desc": "防御+30%",       "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"def_mult": 0.1}},
                ],
            },
            "圣光": {
                "desc": "圣光治愈之力",
                "skills": [
                    {"id": "k_holy_1",       "name": "圣光祝福",   "desc": "生命+10%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"hp_mult": 0.02}},
                    {"id": "k_holy_2",       "name": "神圣之光",   "desc": "攻击+8%",        "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"atk_mult": 0.016}},
                    {"id": "k_holy_3",       "name": "净化之光",   "desc": "减伤+8%",        "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"dmg_reduce": 0.016}},
                    {"id": "k_holy_4",       "name": "神圣审判",   "desc": "攻击+20%",       "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"atk_mult": 0.04}},
                    {"id": "k_holy_5",       "name": "天神下凡",   "desc": "全属性+15%",     "type": "passive", "max_rank": 3, "req_level": 80, "effect": {"atk_mult": 0.05, "def_mult": 0.05, "hp_mult": 0.05}},
                ],
            },
            "冲锋": {
                "desc": "骑士冲锋技巧",
                "skills": [
                    {"id": "k_charge_1",     "name": "冲锋",       "desc": "速度+10%",       "type": "passive", "max_rank": 5, "req_level": 5,  "effect": {"speed_mult": 0.02}},
                    {"id": "k_charge_2",     "name": "破甲冲击",   "desc": "攻击+10%",       "type": "passive", "max_rank": 5, "req_level": 15, "effect": {"atk_mult": 0.02}},
                    {"id": "k_charge_3",     "name": "战马冲锋",   "desc": "暴击率+5%",      "type": "passive", "max_rank": 5, "req_level": 30, "effect": {"crit_rate": 0.01}},
                    {"id": "k_charge_4",     "name": "圣骑士之怒", "desc": "攻击+20% 防御+10%","type": "passive", "max_rank": 5, "req_level": 50, "effect": {"atk_mult": 0.04, "def_mult": 0.02}},
                    {"id": "k_charge_5",     "name": "天堂之拳",   "desc": "全伤害+20%",     "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"dmg_mult": 0.067}},
                ],
            },
        },
    },

    CLASS_PRIEST: {
        "name": "牧师技能树",
        "branches": {
            "神圣": {
                "desc": "神圣治愈与祝福",
                "skills": [
                    {"id": "p_holy_1",       "name": "治愈之光",   "desc": "生命+15%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"hp_mult": 0.03}},
                    {"id": "p_holy_2",       "name": "神圣祝福",   "desc": "防御+10%",       "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"def_mult": 0.02}},
                    {"id": "p_holy_3",       "name": "生命涌泉",   "desc": "生命+20%",       "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"hp_mult": 0.04}},
                    {"id": "p_holy_4",       "name": "神圣庇护",   "desc": "减伤+10%",       "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"dmg_reduce": 0.02}},
                    {"id": "p_holy_5",       "name": "天使降临",   "desc": "全属性+15%",     "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"atk_mult": 0.05, "def_mult": 0.05, "hp_mult": 0.05}},
                ],
            },
            "惩戒": {
                "desc": "神圣惩戒之力",
                "skills": [
                    {"id": "p_punish_1",     "name": "神圣惩击",   "desc": "攻击+10%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"atk_mult": 0.02}},
                    {"id": "p_punish_2",     "name": "驱邪术",     "desc": "暴击率+5%",      "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"crit_rate": 0.01}},
                    {"id": "p_punish_3",     "name": "神圣之火",   "desc": "攻击+15%",       "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"atk_mult": 0.03}},
                    {"id": "p_punish_4",     "name": "天罚之锤",   "desc": "暴击伤害+15%",   "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"crit_dmg": 0.03}},
                    {"id": "p_punish_5",     "name": "末日审判",   "desc": "全伤害+20%",     "type": "passive", "max_rank": 3, "req_level": 80, "effect": {"dmg_mult": 0.067}},
                ],
            },
            "信仰": {
                "desc": "信仰之力",
                "skills": [
                    {"id": "p_faith_1",      "name": "虔诚",       "desc": "经验+10%",       "type": "passive", "max_rank": 5, "req_level": 5,  "effect": {"exp_mult": 0.02}},
                    {"id": "p_faith_2",      "name": "坚定信仰",   "desc": "防御+8% 生命+8%","type": "passive", "max_rank": 5, "req_level": 15, "effect": {"def_mult": 0.016, "hp_mult": 0.016}},
                    {"id": "p_faith_3",      "name": "神圣意志",   "desc": "减伤+8%",        "type": "passive", "max_rank": 5, "req_level": 30, "effect": {"dmg_reduce": 0.016}},
                    {"id": "p_faith_4",      "name": "神恩",       "desc": "金币+15%",       "type": "passive", "max_rank": 5, "req_level": 50, "effect": {"gold_mult": 0.03}},
                    {"id": "p_faith_5",      "name": "神之代言人", "desc": "全属性+10%",     "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"atk_mult": 0.033, "def_mult": 0.033, "hp_mult": 0.033}},
                ],
            },
        },
    },

    CLASS_ASSASSIN: {
        "name": "刺客技能树",
        "branches": {
            "暗影": {
                "desc": "暗影之力",
                "skills": [
                    {"id": "a_shadow_1",     "name": "暗影步",     "desc": "速度+15%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"speed_mult": 0.03}},
                    {"id": "a_shadow_2",     "name": "暗影打击",   "desc": "暴击率+5%",      "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"crit_rate": 0.01}},
                    {"id": "a_shadow_3",     "name": "影遁",       "desc": "闪避率+5%",      "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"dodge_rate": 0.01}},
                    {"id": "a_shadow_4",     "name": "暗杀",       "desc": "暴击伤害+20%",   "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"crit_dmg": 0.04}},
                    {"id": "a_shadow_5",     "name": "影之主宰",   "desc": "速度+30% 暴击+10%","type": "passive", "max_rank": 3, "req_level": 70, "effect": {"speed_mult": 0.1, "crit_rate": 0.033}},
                ],
            },
            "毒刃": {
                "desc": "淬毒与致命打击",
                "skills": [
                    {"id": "a_poison_1",     "name": "淬毒",       "desc": "攻击+10%",       "type": "passive", "max_rank": 5, "req_level": 1,  "effect": {"atk_mult": 0.02}},
                    {"id": "a_poison_2",     "name": "剧毒涂抹",   "desc": "攻击+12%",       "type": "passive", "max_rank": 5, "req_level": 10, "effect": {"atk_mult": 0.024}},
                    {"id": "a_poison_3",     "name": "致命毒素",   "desc": "暴击率+8%",      "type": "passive", "max_rank": 5, "req_level": 25, "effect": {"crit_rate": 0.016}},
                    {"id": "a_poison_4",     "name": "毒爆",       "desc": "全伤害+15%",     "type": "passive", "max_rank": 5, "req_level": 45, "effect": {"dmg_mult": 0.03}},
                    {"id": "a_poison_5",     "name": "死神之触",   "desc": "攻击+30%",       "type": "passive", "max_rank": 3, "req_level": 70, "effect": {"atk_mult": 0.1}},
                ],
            },
            "敏捷": {
                "desc": "敏捷与生存",
                "skills": [
                    {"id": "a_agi_1",        "name": "灵活",       "desc": "闪避率+3%",      "type": "passive", "max_rank": 5, "req_level": 5,  "effect": {"dodge_rate": 0.006}},
                    {"id": "a_agi_2",        "name": "疾风之刃",   "desc": "速度+8% 攻击+5%","type": "passive", "max_rank": 5, "req_level": 15, "effect": {"speed_mult": 0.016, "atk_mult": 0.01}},
                    {"id": "a_agi_3",        "name": "危险感知",   "desc": "闪避率+5%",      "type": "passive", "max_rank": 5, "req_level": 30, "effect": {"dodge_rate": 0.01}},
                    {"id": "a_agi_4",        "name": "无影无踪",   "desc": "速度+20%",       "type": "passive", "max_rank": 5, "req_level": 50, "effect": {"speed_mult": 0.04}},
                    {"id": "a_agi_5",        "name": "暗影之王",   "desc": "全属性+10%",     "type": "passive", "max_rank": 3, "req_level": 80, "effect": {"atk_mult": 0.033, "def_mult": 0.033, "hp_mult": 0.033}},
                ],
            },
        },
    },
}


# ============================================================
# 装备稀有度 (7种)
# ============================================================
RARITY_COMMON     = "common"       # 普通
RARITY_UNCOMMON   = "uncommon"     # 优秀
RARITY_RARE       = "rare"         # 稀有
RARITY_EPIC       = "epic"         # 史诗
RARITY_LEGENDARY  = "legendary"    # 传说
RARITY_MYTHIC     = "mythic"       # 神话
RARITY_COSMIC     = "cosmic"       # 宇宙

RARITY_CONFIG = {
    RARITY_COMMON:    {"name": "普通", "color": "#AAAAAA", "stat_mult": 1.0,  "drop_weight": 50},
    RARITY_UNCOMMON:  {"name": "优秀", "color": "#55CC55", "stat_mult": 1.3,  "drop_weight": 25},
    RARITY_RARE:      {"name": "稀有", "color": "#5555FF", "stat_mult": 1.7,  "drop_weight": 13},
    RARITY_EPIC:      {"name": "史诗", "color": "#AA55CC", "stat_mult": 2.2,  "drop_weight": 7},
    RARITY_LEGENDARY: {"name": "传说", "color": "#FFAA00", "stat_mult": 3.0,  "drop_weight": 3},
    RARITY_MYTHIC:    {"name": "神话", "color": "#FF5555", "stat_mult": 4.0,  "drop_weight": 1.5},
    RARITY_COSMIC:    {"name": "宇宙", "color": "#00FFFF", "stat_mult": 5.5,  "drop_weight": 0.5},
}

# 装备部位 (6种)
SLOT_MAIN_HAND  = "main_hand"    # 主手
SLOT_OFF_HAND   = "off_hand"     # 副手
SLOT_HELMET     = "helmet"       # 头盔
SLOT_CHEST      = "chest"        # 胸甲
SLOT_BOOTS      = "boots"        # 鞋子
SLOT_ACCESSORY  = "accessory"    # 饰品

EQUIPMENT_SLOTS = {
    SLOT_MAIN_HAND:  {"name": "主手", "icon": "⚔️"},
    SLOT_OFF_HAND:   {"name": "副手", "icon": "🗡️"},
    SLOT_HELMET:     {"name": "头盔", "icon": "⛑️"},
    SLOT_CHEST:      {"name": "胸甲", "icon": "🛡️"},
    SLOT_BOOTS:      {"name": "鞋子", "icon": "👢"},
    SLOT_ACCESSORY:  {"name": "饰品", "icon": "💍"},
}

# 装备槽分组
SLOT_GROUP_WEAPON = [SLOT_MAIN_HAND, SLOT_OFF_HAND]
SLOT_GROUP_ARMOR  = [SLOT_HELMET, SLOT_CHEST, SLOT_BOOTS]
SLOT_GROUP_ALL    = [SLOT_MAIN_HAND, SLOT_OFF_HAND, SLOT_HELMET, SLOT_CHEST, SLOT_BOOTS, SLOT_ACCESSORY]

# ============================================================
# 难度系统
# ============================================================
DIFF_NORMAL    = "normal"       # 普通
DIFF_NIGHTMARE = "nightmare"    # 噩梦
DIFF_HELL      = "hell"         # 地狱

DIFFICULTIES = {
    DIFF_NORMAL:    {"name": "普通", "color": "#CCCCCC", "mult": 1.0},
    DIFF_NIGHTMARE: {"name": "噩梦", "color": "#FF6600", "mult": 1.3},
    DIFF_HELL:      {"name": "地狱", "color": "#FF0000", "mult": 1.7},
}

# ============================================================
# 章节（3个章节，每10关循环）
# ============================================================
CHAPTER_1 = "chapter_1"
CHAPTER_2 = "chapter_2"
CHAPTER_3 = "chapter_3"

CHAPTERS = {
    CHAPTER_1: {"name": "黑暗森林", },
    CHAPTER_2: {"name": "废弃矿洞", },
    CHAPTER_3: {"name": "恶魔城堡", },
}

# ============================================================
# 关卡结构
# ============================================================
STAGES_PER_DIFFICULTY = 33      # 每难度33关（3章×11关）
MONSTERS_PER_STAGE = 30         # 每关30只普通怪 + 1个Boss
BOSS_MONSTER_INTERVAL = 30      # 每30只普通怪出一只Boss

# ============================================================
# 战斗设置
# ============================================================
COMBAT_TICK = 1000
CRIT_CHANCE = 0.08
CRIT_DAMAGE_MULT = 2.0
DODGE_CHANCE = 0.05

# 掉落设置
DROP_CHANCE = 0.35
GOLD_BASE = 12
GOLD_GROWTH = 6

# 颜色
GOLD_COLOR = "#FFD700"
HP_COLOR   = "#FF4444"
EXP_COLOR  = "#44AAFF"

# ============================================================
# 天赋树系统（使用金币点亮，全局生效）
# ============================================================
# 天赋费用：每级花费，5级满
TALENT_COSTS = [80, 200, 400, 800, 1500]

TALENT_TREES = {
    "fortune": {
        "name": "财富",
        "icon": "💰",
        "desc": "提升金币与经验获取",
        "color": "#FFD700",
        "talents": [
            {
                "id": "t_gold_find",
                "name": "聚财术",
                "desc": "金币获取+{value}%",
                "icon": "💰",
                "max_rank": 5,
                "effect_key": "gold_mult",
                "effect_per_rank": 0.04,
            },
            {
                "id": "t_exp_boost",
                "name": "博学",
                "desc": "经验获取+{value}%",
                "icon": "📖",
                "max_rank": 5,
                "effect_key": "exp_mult",
                "effect_per_rank": 0.05,
            },
            {
                "id": "t_treasure_hunter",
                "name": "寻宝直觉",
                "desc": "装备掉落率+{value}%",
                "icon": "🗝️",
                "max_rank": 5,
                "effect_key": "drop_rate",
                "effect_per_rank": 0.04,
            },
            {
                "id": "t_bargain",
                "name": "讨价还价",
                "desc": "装备售价+{value}%",
                "icon": "🏷️",
                "max_rank": 5,
                "effect_key": "sell_mult",
                "effect_per_rank": 0.06,
            },
            {
                "id": "t_gold_rush",
                "name": "黄金狂热",
                "desc": "金币获取额外+{value}%",
                "icon": "✨",
                "max_rank": 5,
                "effect_key": "gold_mult",
                "effect_per_rank": 0.06,
            },
        ],
    },
    "war": {
        "name": "战争",
        "icon": "⚔️",
        "desc": "提升战斗属性",
        "color": "#FF4444",
        "talents": [
            {
                "id": "t_atk_boost",
                "name": "力量强化",
                "desc": "攻击力+{value}%",
                "icon": "⚔️",
                "max_rank": 5,
                "effect_key": "atk_mult",
                "effect_per_rank": 0.03,
            },
            {
                "id": "t_def_boost",
                "name": "坚韧体魄",
                "desc": "防御力+{value}%",
                "icon": "🛡️",
                "max_rank": 5,
                "effect_key": "def_mult",
                "effect_per_rank": 0.03,
            },
            {
                "id": "t_hp_boost",
                "name": "生命力",
                "desc": "生命值+{value}%",
                "icon": "❤️",
                "max_rank": 5,
                "effect_key": "hp_mult",
                "effect_per_rank": 0.04,
            },
            {
                "id": "t_crit_boost",
                "name": "致命精准",
                "desc": "暴击率+{value}%",
                "icon": "💥",
                "max_rank": 5,
                "effect_key": "crit_rate",
                "effect_per_rank": 0.015,
            },
            {
                "id": "t_dmg_boost",
                "name": "战争之王",
                "desc": "全伤害+{value}%",
                "icon": "👑",
                "max_rank": 5,
                "effect_key": "dmg_mult",
                "effect_per_rank": 0.04,
            },
        ],
    },
}
