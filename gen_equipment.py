"""装备词条系统 + 全量装备生成 → Markdown（含技能加成词条）"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.utils.constants import *

# ============================================================
# 通用词条池
# ============================================================
PREFIX_AFFIXES = [
    # 攻击类
    {"name": "嗜血",     "stat": "atk",    "min": 5,  "max": 30,  "desc": "攻击+n"},
    {"name": "破甲",     "stat": "atk_pct", "min": 3,  "max": 15,  "desc": "攻击+n%"},
    {"name": "暴怒",     "stat": "crit",    "min": 2,  "max": 10,  "desc": "暴击率+n%"},
    {"name": "致命",     "stat": "crit_dmg","min": 5,  "max": 25,  "desc": "暴击伤害+n%"},
    {"name": "穿刺",     "stat": "pen",     "min": 3,  "max": 12,  "desc": "穿透+n%"},
    # 防御类
    {"name": "坚韧",     "stat": "def",     "min": 5,  "max": 30,  "desc": "防御+n"},
    {"name": "铁壁",     "stat": "def_pct", "min": 3,  "max": 15,  "desc": "防御+n%"},
    {"name": "生命",     "stat": "hp",      "min": 20, "max": 150, "desc": "生命+n"},
    {"name": "活力",     "stat": "hp_pct",  "min": 3,  "max": 15,  "desc": "生命+n%"},
    {"name": "减伤",     "stat": "dmg_red", "min": 2,  "max": 8,   "desc": "减伤+n%"},
    # 速度类
    {"name": "疾风",     "stat": "spd",     "min": 0.1,"max": 0.8, "desc": "速度+n"},
    {"name": "闪避",     "stat": "dodge",   "min": 2,  "max": 8,   "desc": "闪避率+n%"},
    # 特殊类
    {"name": "吸血",     "stat": "lifesteal","min": 2, "max": 10,  "desc": "生命偷取+n%"},
    {"name": "反噬",     "stat": "thorn",    "min": 3, "max": 15,  "desc": "反伤+n%"},
    {"name": "贪婪",     "stat": "gold",    "min": 5,  "max": 20,  "desc": "金币获取+n%"},
    {"name": "启迪",     "stat": "exp",     "min": 5,  "max": 20,  "desc": "经验获取+n%"},
]

SUFFIX_AFFIXES = [
    {"name": "深渊之力", "stat": "atk",    "min": 10, "max": 50,  "desc": "攻击+n"},
    {"name": "地狱之火", "stat": "crit",    "min": 3,  "max": 12,  "desc": "暴击率+n%"},
    {"name": "亡灵低语", "stat": "lifesteal","min": 3, "max": 12,  "desc": "生命偷取+n%"},
    {"name": "暗影庇护", "stat": "dodge",   "min": 3,  "max": 10,  "desc": "闪避率+n%"},
    {"name": "恶魔契约", "stat": "crit_dmg","min": 8,  "max": 30,  "desc": "暴击伤害+n%"},
    {"name": "诅咒之血", "stat": "hp",      "min": 30, "max": 200, "desc": "生命+n"},
    {"name": "不灭意志", "stat": "dmg_red", "min": 3,  "max": 10,  "desc": "减伤+n%"},
    {"name": "灵魂收割", "stat": "exp",     "min": 8,  "max": 25,  "desc": "经验获取+n%"},
    {"name": "混沌之触", "stat": "pen",     "min": 5,  "max": 15,  "desc": "穿透+n%"},
    {"name": "末日余烬", "stat": "atk_pct", "min": 5,  "max": 20,  "desc": "攻击+n%"},
    {"name": "虚空低语", "stat": "def_pct", "min": 5,  "max": 20,  "desc": "防御+n%"},
    {"name": "血月狂潮", "stat": "thorn",    "min": 5, "max": 20,  "desc": "反伤+n%"},
]

# ============================================================
# 技能加成词条池（从SKILL_TREES自动生成）
# ============================================================
def _build_skill_affixes():
    """从技能树自动生成技能词条"""
    skill_affixes = []

    for cls_id, tree in SKILL_TREES.items():
        cls_name = HERO_CLASSES[cls_id]["name"]

        for branch_name, branch in tree["branches"].items():
            for skill in branch["skills"]:
                # 技能+1词条（突破上限）
                skill_affixes.append({
                    "name": f"{skill['name']}强化",
                    "stat": "skill_rank",
                    "skill_id": skill["id"],
                    "skill_name": skill["name"],
                    "class": cls_name,
                    "class_id": cls_id,
                    "branch": branch_name,
                    "value": 1,
                    "desc": f"[{cls_name}] {skill['name']} 等级+1",
                    "weight": 3,
                })

            # 分支效果加成词条
            skill_affixes.append({
                "name": f"{branch_name}共鸣",
                "stat": "branch_bonus",
                "class_id": cls_id,
                "class": cls_name,
                "branch": branch_name,
                "min": 5,
                "max": 20,
                "desc": f"[{cls_name}] {branch_name}分支效果+n%",
                "weight": 5,
            })

    return skill_affixes

SKILL_AFFIXES = _build_skill_affixes()

# ============================================================
# 词条数量配置
# ============================================================
AFFIX_COUNT = {
    RARITY_COMMON:    0,
    RARITY_UNCOMMON:  1,
    RARITY_RARE:      2,
    RARITY_EPIC:      3,
    RARITY_LEGENDARY: 4,
    RARITY_MYTHIC:    5,
    RARITY_COSMIC:    6,
}

# 技能词条出现概率（基于品级）
SKILL_AFFIX_CHANCE = {
    RARITY_COMMON:    0,
    RARITY_UNCOMMON:  0,
    RARITY_RARE:      0.15,
    RARITY_EPIC:      0.25,
    RARITY_LEGENDARY: 0.35,
    RARITY_MYTHIC:    0.45,
    RARITY_COSMIC:    0.55,
}

# ============================================================
# 装备名称模板
# ============================================================
WEAPON_NAMES = {
    RARITY_COMMON:    ["铁剑", "木弓", "法杖", "短刀", "长枪", "战斧"],
    RARITY_UNCOMMON:  ["钢刃", "长弓", "橡木杖", "双刃匕首", "战戟", "铁锤"],
    RARITY_RARE:      ["秘银剑", "精灵弓", "符文杖", "淬毒短剑", "龙骨枪", "寒铁斧"],
    RARITY_EPIC:      ["暗影之刃", "风暴之弓", "奥术之杖", "血牙匕首", "雷霆戟", "碎颅锤"],
    RARITY_LEGENDARY: ["灭世魔剑", "末日之弓", "混沌法杖", "暗杀者之牙", "神罚之枪", "毁灭之斧"],
    RARITY_MYTHIC:    ["天罚圣剑", "星陨之弓", "虚空法杖", "影之哀伤", "破晓神枪", "灭世之锤"],
    RARITY_COSMIC:    ["创世之刃", "永恒之弓", "灭世法杖", "虚空之牙", "诸神黄昏", "混沌之锤"],
}

ARMOR_NAMES = {
    RARITY_COMMON:    ["布甲", "皮甲", "锁甲"],
    RARITY_UNCOMMON:  ["强化皮甲", "链甲", "板甲"],
    RARITY_RARE:      ["秘银甲", "精灵锁甲", "符文板甲"],
    RARITY_EPIC:      ["暗影战甲", "风暴皮甲", "奥术长袍"],
    RARITY_LEGENDARY: ["灭世铠甲", "末日之衣", "混沌法袍"],
    RARITY_MYTHIC:    ["天罚圣铠", "星陨战衣", "虚空法袍"],
    RARITY_COSMIC:    ["创世之铠", "永恒之衣", "灭世法袍"],
}

ACCESSORY_NAMES = {
    RARITY_COMMON:    ["铜戒指", "玻璃项链", "石质护符"],
    RARITY_UNCOMMON:  ["银戒指", "珍珠项链", "铁质护符"],
    RARITY_RARE:      ["金戒指", "宝石项链", "秘银护符"],
    RARITY_EPIC:      ["暗影指环", "风暴吊坠", "奥术徽章"],
    RARITY_LEGENDARY: ["灭世之戒", "末日之心", "混沌之眼"],
    RARITY_MYTHIC:    ["天罚之戒", "星陨之心", "虚空之眼"],
    RARITY_COSMIC:    ["创世之戒", "永恒之心", "灭世之眼"],
}


def roll_affix_value(affix, rarity_mult):
    base_min = affix["min"]
    base_max = affix["max"] * rarity_mult
    val = random.uniform(base_min, base_max)
    if isinstance(affix["min"], int):
        return int(val)
    return round(val, 1)


def format_affix_text(affix, value):
    text = affix["desc"].replace("+n", f"+{value}")
    return text


def generate_equipment(stage, slot, rarity, seed=None):
    if seed is not None:
        random.seed(seed)

    rmult = RARITY_CONFIG[rarity]["stat_mult"]
    slot_info = EQUIPMENT_SLOTS[slot]

    name_map = {
        SLOT_MAIN_HAND: WEAPON_NAMES,
        SLOT_CHEST: ARMOR_NAMES,
        SLOT_ACCESSORY: ACCESSORY_NAMES,
    }
    name = random.choice(name_map[slot][rarity])

    # 基础属性
    base = 5 + stage * 2.5
    hp = 0; atk = 0; defense = 0; speed = 0.0

    if slot == SLOT_MAIN_HAND:
        atk = int(base * rmult * random.uniform(0.9, 1.1))
    elif slot == SLOT_CHEST:
        hp = int(base * 3 * rmult * random.uniform(0.9, 1.1))
        defense = int(base * 0.6 * rmult * random.uniform(0.9, 1.1))
    else:
        hp = int(base * rmult * random.uniform(0.9, 1.1))
        atk = int(base * 0.35 * rmult * random.uniform(0.9, 1.1))
        defense = int(base * 0.35 * rmult * random.uniform(0.9, 1.1))
        speed = round(rmult * random.uniform(0.1, 0.5), 1)

    # 词条
    affix_count = AFFIX_COUNT[rarity]
    affixes = []
    if affix_count > 0:
        # 决定是否包含技能词条
        skill_chance = SKILL_AFFIX_CHANCE[rarity]
        has_skill_affix = random.random() < skill_chance

        if has_skill_affix and affix_count >= 2:
            # 1个技能词条 + (n-1)个通用词条
            skill_af = random.choice(SKILL_AFFIXES)
            if skill_af["stat"] == "skill_rank":
                affixes.append({
                    "name": skill_af["name"],
                    "desc": skill_af["desc"],
                    "stat": skill_af["stat"],
                    "value": skill_af["value"],
                    "skill_id": skill_af.get("skill_id"),
                    "class": skill_af.get("class"),
                    "branch": skill_af.get("branch"),
                })
            else:
                val = roll_affix_value(skill_af, rmult)
                affixes.append({
                    "name": skill_af["name"],
                    "desc": format_affix_text(skill_af, val),
                    "stat": skill_af["stat"],
                    "value": val,
                    "class": skill_af.get("class"),
                    "branch": skill_af.get("branch"),
                })
            remaining = affix_count - 1
        else:
            remaining = affix_count

        # 通用词条
        all_pool = PREFIX_AFFIXES + SUFFIX_AFFIXES
        chosen = random.sample(all_pool, min(remaining, len(all_pool)))
        for af in chosen:
            val = roll_affix_value(af, rmult)
            affixes.append({
                "name": af["name"],
                "desc": format_affix_text(af, val),
                "stat": af["stat"],
                "value": val,
            })

    return {
        "name": name,
        "slot": slot_info["name"],
        "slot_icon": slot_info["icon"],
        "rarity": RARITY_CONFIG[rarity]["name"],
        "rarity_color": RARITY_CONFIG[rarity]["color"],
        "stage": stage,
        "hp": hp,
        "atk": atk,
        "defense": defense,
        "speed": speed,
        "affixes": affixes,
    }


def generate_all_equipment(stage=100):
    all_items = []
    seed_counter = 0
    for rarity in RARITY_CONFIG:
        for slot in [SLOT_MAIN_HAND, SLOT_CHEST, SLOT_ACCESSORY]:
            for i in range(3):  # 每种3件
                item = generate_equipment(stage, slot, rarity, seed=seed_counter)
                seed_counter += 1
                all_items.append(item)
    return all_items


def write_markdown(items, filepath):
    lines = []
    lines.append("# 暗黑任务栏RPG - 全装备图鉴 (Stage 100)")
    lines.append("")
    lines.append(f"> 自动生成 | 共 {len(items)} 件装备 | 含技能加成词条")
    lines.append("")
    lines.append("## 词条系统说明")
    lines.append("")
    lines.append("| 品级 | 词条数 | 技能词条概率 | 说明 |")
    lines.append("|------|--------|-------------|------|")

    for rarity in [RARITY_COSMIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_EPIC, RARITY_RARE, RARITY_UNCOMMON, RARITY_COMMON]:
        rname = RARITY_CONFIG[rarity]["name"]
        cnt = AFFIX_COUNT[rarity]
        sk = int(SKILL_AFFIX_CHANCE[rarity] * 100)
        desc = "无词条" if cnt == 0 else f"{cnt}条通用词条"
        if sk > 0:
            desc += f"，{sk}%概率出现1条技能词条"
        lines.append(f"| {rname} | {cnt} | {sk}% | {desc} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    rarity_order = [RARITY_COSMIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_EPIC, RARITY_RARE, RARITY_UNCOMMON, RARITY_COMMON]

    for rarity in rarity_order:
        rname = RARITY_CONFIG[rarity]["name"]
        rmult = RARITY_CONFIG[rarity]["stat_mult"]
        affix_n = AFFIX_COUNT[rarity]

        lines.append(f"## {rname} (x{rmult} | {affix_n}条词条)")
        lines.append("")

        for slot in [SLOT_MAIN_HAND, SLOT_CHEST, SLOT_ACCESSORY]:
            slot_items = [i for i in items if i["slot"] == EQUIPMENT_SLOTS[slot]["name"] and i["rarity"] == rname]
            if not slot_items:
                continue

            slot_name = EQUIPMENT_SLOTS[slot]["name"]
            lines.append(f"### {slot_name}")
            lines.append("")

            for item in slot_items:
                lines.append(f"#### {item['name']}")
                lines.append("")
                lines.append(f"- **部位**: {item['slot']} | **品级**: {item['rarity']} | **等级**: {item['stage']}")

                stat_parts = []
                if item["hp"] > 0:
                    stat_parts.append(f"HP+{item['hp']}")
                if item["atk"] > 0:
                    stat_parts.append(f"ATK+{item['atk']}")
                if item["defense"] > 0:
                    stat_parts.append(f"DEF+{item['defense']}")
                if item["speed"] > 0:
                    stat_parts.append(f"SPD+{item['speed']}")
                if stat_parts:
                    lines.append(f"- **基础属性**: {' | '.join(stat_parts)}")

                if item["affixes"]:
                    lines.append(f"- **词条** ({len(item['affixes'])}条):")
                    for af in item["affixes"]:
                        is_skill = af.get("stat") in ("skill_rank", "branch_bonus")
                        if is_skill:
                            lines.append(f"  - **[{af.get('class', '?')}]** {af['desc']} ⚡")
                        else:
                            lines.append(f"  - {af['name']}: {af['desc']}")
                else:
                    lines.append(f"- **词条**: 无")

                lines.append("")

    # 技能词条汇总
    lines.append("---")
    lines.append("")
    lines.append("## 全部技能加成词条")
    lines.append("")
    lines.append("### 技能等级+1词条")
    lines.append("")
    lines.append("| 职业 | 分支 | 技能名 | 效果 |")
    lines.append("|------|------|--------|------|")
    for af in SKILL_AFFIXES:
        if af["stat"] == "skill_rank":
            lines.append(f"| {af['class']} | {af['branch']} | {af['skill_name']} | 等级+1（突破上限） |")

    lines.append("")
    lines.append("### 分支效果加成词条")
    lines.append("")
    lines.append("| 职业 | 分支 | 效果 |")
    lines.append("|------|------|------|")
    for af in SKILL_AFFIXES:
        if af["stat"] == "branch_bonus":
            lines.append(f"| {af['class']} | {af['branch']} | {af['desc'].replace('+n%', '+5%~20%')} |")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Written {len(items)} items to {filepath}")


if __name__ == "__main__":
    items = generate_all_equipment(100)
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "装备图鉴.md")
    write_markdown(items, outpath)
