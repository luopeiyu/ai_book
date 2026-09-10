"""
战斗统计相关类定义
"""

from dataclasses import dataclass

@dataclass
class BattleStats:
    """战斗统计"""
    damage_dealt: int = 0      # 造成的总伤害
    damage_taken: int = 0      # 承受的总伤害  
    kills: int = 0             # 击杀数
    deaths: int = 0            # 死亡次数
    skills_used: int = 0       # 使用技能次数 