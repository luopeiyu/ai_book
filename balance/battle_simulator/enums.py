"""
枚举定义
"""

from enum import Enum

class HeroClass(Enum):
    """英雄职业"""
    WARRIOR = "warrior"      # 战士
    MAGE = "mage"           # 法师
    ARCHER = "archer"       # 弓箭手
    ASSASSIN = "assassin"   # 刺客
    SUPPORT = "support"     # 辅助

class HeroElement(Enum):
    """英雄元素"""
    FIRE = "fire"      # 火元素
    WATER = "water"    # 水元素
    EARTH = "earth"    # 土元素
    AIR = "air"        # 风元素
    LIGHT = "light"    # 光元素
    DARK = "dark"      # 暗元素

class DamageType(Enum):
    """伤害类型"""
    PHYSICAL = "physical"  # 物理伤害：受防御力减免
    MAGICAL = "magical"    # 魔法伤害：无视防御力（没用到）
    FIXED = "fixed"        # 固定伤害：无视防御力的固定数值伤害
    MINE = "mine"          # 地雷伤害：特殊的爆炸伤害

class SkillType(Enum):
    """技能类型"""
    ATTACK = "attack"    # 攻击技能：对敌方造成伤害
    HEAL = "heal"        # 治疗技能：恢复友方生命值
    REVIVE = "revive"    # 复活技能：复活死亡的友方英雄
    BUFF = "buff"        # 增益技能：为友方添加正面效果
    DEBUFF = "debuff"    # 减益技能：为敌方添加负面效果
    SPECIAL = "special"  # 特殊技能：具有特殊机制的技能

class BattleResult(Enum):
    """战斗结果"""
    TEAM1_WIN = "team1_win"  # 队伍1获胜
    TEAM2_WIN = "team2_win"  # 队伍2获胜
    DRAW = "draw"            # 平局

class StackType(Enum):
    """状态效果叠加方式"""
    REPLACE = "replace"      # 替换：新效果替换旧效果
    EXTEND = "extend"        # 延长：延长持续时间
    ACCUMULATE = "accumulate" # 累积：效果值累积
    REFRESH = "refresh"      # 刷新：重置持续时间但保持效果值