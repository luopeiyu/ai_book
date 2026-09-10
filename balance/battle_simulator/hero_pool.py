"""
英雄池管理
"""

from typing import Dict, Optional
from enums import HeroClass, HeroElement
from hero import Hero

# 全局英雄池
HERO_POOL: Dict[int, tuple] = {
    # 英雄配置数据格式: (id, name, class, element, attack, defense, hp, speed, basic_skill_id)
    
    # 战士 (ID 0-7) - 基础技能: 普通攻击(1)
    0: (0, "阿里斯", HeroClass.WARRIOR, HeroElement.FIRE, 120, 80, 1000, 50, 0),
    1: (1, "塞琳达", HeroClass.WARRIOR, HeroElement.WATER, 110, 90, 1100, 45, 0),
    2: (2, "盖乌斯", HeroClass.WARRIOR, HeroElement.EARTH, 100, 100, 1200, 40, 0),
    3: (3, "索伦", HeroClass.WARRIOR, HeroElement.AIR, 130, 70, 900, 60, 0),
    4: (4, "露西娅", HeroClass.WARRIOR, HeroElement.LIGHT, 115, 85, 1050, 50, 0),
    5: (5, "卡西乌斯", HeroClass.WARRIOR, HeroElement.DARK, 125, 75, 950, 55, 0),
    6: (6, "达尔温", HeroClass.WARRIOR, HeroElement.FIRE, 200, 120, 2000, 60, 0),
    7: (7, "弗罗斯特", HeroClass.WARRIOR, HeroElement.WATER, 190, 130, 2100, 55, 0),
        
    # 法师 (ID 8-15) - 基础技能: 群体攻击(8)
    8: (8, "梅林达", HeroClass.MAGE, HeroElement.FIRE, 150, 50, 800, 70, 0),
    9: (9, "阿奎纳", HeroClass.MAGE, HeroElement.WATER, 140, 60, 850, 65, 0),
    10: (10, "泰拉斯", HeroClass.MAGE, HeroElement.EARTH, 130, 70, 900, 60, 0),
    11: (11, "艾弗里", HeroClass.MAGE, HeroElement.AIR, 160, 40, 750, 80, 0),
    12: (12, "塞拉菲娜", HeroClass.MAGE, HeroElement.LIGHT, 145, 55, 825, 70, 0),
    13: (13, "默德雷德", HeroClass.MAGE, HeroElement.DARK, 155, 45, 775, 75, 0),
    14: (14, "伊格尼斯", HeroClass.MAGE, HeroElement.FIRE, 250, 100, 1800, 80, 0),
    15: (15, "尼普顿", HeroClass.MAGE, HeroElement.WATER, 240, 110, 1900, 75, 0),
        
    # 弓箭手 (ID 16-23) - 基础技能: 溅射攻击(9)
    16: (16, "奥里恩", HeroClass.ARCHER, HeroElement.FIRE, 140, 60, 850, 90, 0),
    17: (17, "阿蒂米丝", HeroClass.ARCHER, HeroElement.WATER, 135, 65, 875, 85, 0),
    18: (18, "狄安娜", HeroClass.ARCHER, HeroElement.EARTH, 125, 75, 925, 80, 0),
    19: (19, "阿波罗", HeroClass.ARCHER, HeroElement.AIR, 150, 50, 800, 100, 0),
    20: (20, "加百列", HeroClass.ARCHER, HeroElement.LIGHT, 142, 58, 862, 88, 0),
    21: (21, "拉斐尔", HeroClass.ARCHER, HeroElement.DARK, 148, 52, 838, 92, 0),
    22: (22, "亨特", HeroClass.ARCHER, HeroElement.AIR, 220, 80, 1600, 95, 0),
    23: (23, "席尔瓦", HeroClass.ARCHER, HeroElement.EARTH, 210, 90, 1700, 90, 0),
        
    # 刺客 (ID 24-31) - 基础技能: 暴力一击(2)
    24: (24, "维德", HeroClass.ASSASSIN, HeroElement.FIRE, 160, 40, 700, 110, 0),
    25: (25, "凯拉", HeroClass.ASSASSIN, HeroElement.WATER, 155, 45, 725, 105, 0),
    26: (26, "斯通", HeroClass.ASSASSIN, HeroElement.EARTH, 145, 55, 775, 95, 0),
    27: (27, "泽菲尔", HeroClass.ASSASSIN, HeroElement.AIR, 170, 30, 650, 120, 0),
    28: (28, "奥瑞利亚", HeroClass.ASSASSIN, HeroElement.LIGHT, 162, 38, 712, 108, 0),
    29: (29, "夜莺", HeroClass.ASSASSIN, HeroElement.DARK, 168, 32, 688, 115, 0),
    30: (30, "幻影", HeroClass.ASSASSIN, HeroElement.DARK, 280, 60, 1400, 125, 0),
    31: (31, "疾风", HeroClass.ASSASSIN, HeroElement.AIR, 270, 70, 1500, 120, 0),
        
    # 辅助 (ID 32-39) - 基础技能: 治疗(10)
    32: (32, "希拉里", HeroClass.SUPPORT, HeroElement.LIGHT, 80, 90, 1000, 75, 0),
    33: (33, "莫甘娜", HeroClass.SUPPORT, HeroElement.DARK, 85, 85, 950, 80, 0),
    34: (34, "德鲁伊德", HeroClass.SUPPORT, HeroElement.EARTH, 75, 95, 1050, 70, 0),
    35: (35, "艾瑞尔", HeroClass.SUPPORT, HeroElement.AIR, 90, 80, 900, 85, 0),
    36: (36, "弗拉德", HeroClass.SUPPORT, HeroElement.FIRE, 95, 75, 875, 90, 0),
    37: (37, "尼瑞达", HeroClass.SUPPORT, HeroElement.WATER, 88, 88, 975, 78, 0),
    38: (38, "大主教", HeroClass.SUPPORT, HeroElement.LIGHT, 150, 150, 2500, 85, 0),
    39: (39, "暗牧", HeroClass.SUPPORT, HeroElement.DARK, 160, 140, 2400, 90, 0),   
}




def create_hero_instance(hero_id: int, secondary_skill_id: int) -> Optional[Hero]:
    """创建英雄实例（用于战斗）"""
    if hero_id not in HERO_POOL:
        return None
        
    config = HERO_POOL[hero_id]
    hero = Hero(
        hero_id=config[0],         # 英雄ID
        name=config[1],            # 英雄名称
        hero_class=config[2],      # 英雄职业
        element=config[3],         # 英雄元素
        attack=config[4],          # 攻击力
        defense=config[5],         # 防御力
        hp=config[6],              # 生命值
        speed=config[7],           # 速度
        basic_skill_id=config[8],  # 基础技能ID
        secondary_skill_id=secondary_skill_id
    )
    
    return hero

