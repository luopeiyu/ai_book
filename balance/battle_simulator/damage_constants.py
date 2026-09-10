"""
伤害计算常量定义
包含职业克制、元素克制、修正系数等参数
"""

from enums import HeroClass, HeroElement

# 职业克制关系 (克制者 -> 被克制者)
CLASS_COUNTER = {
    HeroClass.WARRIOR: HeroClass.ARCHER,
    HeroClass.ARCHER: HeroClass.MAGE,
    HeroClass.MAGE: HeroClass.ASSASSIN,
    HeroClass.ASSASSIN: HeroClass.WARRIOR,
    HeroClass.SUPPORT: None  # 辅助不克制任何职业
}

# 元素克制关系
ELEMENT_COUNTER = {
    HeroElement.FIRE: HeroElement.EARTH,
    HeroElement.EARTH: HeroElement.AIR,
    HeroElement.AIR: HeroElement.WATER,
    HeroElement.WATER: HeroElement.FIRE,
    HeroElement.LIGHT: HeroElement.DARK,
    HeroElement.DARK: HeroElement.LIGHT
}

# 伤害修正系数
CLASS_MODIFIER = 1.2    # 职业克制伤害修正
ELEMENT_MODIFIER = 1.15 # 元素克制伤害修正