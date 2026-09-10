"""
目标选择系统
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from enums import SkillType

class TargetSelector(ABC):
    """目标选择器抽象基类"""
    
    @abstractmethod
    def select_target(self, skill, caster, context):
        """选择目标"""
        pass

class OffensiveTargetSelector(TargetSelector):
    """攻击型技能目标选择器 - 对应位置攻击"""
    
    def select_target(self, skill, caster, context):
        """选择敌方目标：优先攻击对应位置，如果对应位置不存在则攻击相邻位置"""
        # 获取施法者在自己队伍中的位置
        ally_team = context.get_ally_team(caster)
        caster_position = ally_team.get_hero_index(caster)
        
        if caster_position is None:
            return None
            
        enemy_team = context.get_enemy_team(caster)
        
        # 定义攻击优先级：对应位置 -> 左邻 -> 右邻 -> 其他位置
        priority_positions = [caster_position]
        if caster_position > 0:
            priority_positions.append(caster_position - 1)
        if caster_position < 4:  # 最多5个位置(0-4)
            priority_positions.append(caster_position + 1)
        # 添加其他位置
        for i in range(5):
            if i not in priority_positions:
                priority_positions.append(i)
        
        # 按优先级查找可攻击的目标
        for pos in priority_positions:
            if (pos < len(enemy_team.heroes) and 
                enemy_team.heroes[pos] and 
                enemy_team.heroes[pos].is_alive and 
                not enemy_team.heroes[pos].is_hidden()):
                return enemy_team.heroes[pos]
        
        return None

class SupportiveTargetSelector(TargetSelector):
    """支援型技能目标选择器"""
    
    def select_target(self, skill, caster, context):
        """选择己方目标：优先血量最低的盟友"""
        ally_team = context.get_ally_team(caster)
        alive_allies = ally_team.get_alive_heroes()
        
        if not alive_allies:
            return None
        
        # 优先治疗血量最低的盟友，血量相同时按ID排序确保确定性
        return min(alive_allies, key=lambda h: (h.current_hp, h.hero_id))

class ReviveTargetSelector(TargetSelector):
    """复活技能目标选择器"""
    
    def select_target(self, skill, caster, context):
        """选择复活目标：第一个死亡的盟友"""
        ally_team = context.get_ally_team(caster)
        dead_allies = [hero for hero in ally_team.get_all_heroes() if not hero.is_alive]
        
        if not dead_allies:
            return None
        
        # 选择第一个死亡的盟友（按ID排序确保确定性）
        return min(dead_allies, key=lambda h: h.hero_id)

class SelfTargetSelector(TargetSelector):
    """自我目标选择器"""
    
    def select_target(self, skill, caster, context):
        """选择自己作为目标"""
        return caster



def select_target(skill, caster, context):
    """简单的目标选择函数"""
    if skill.skill_type == SkillType.ATTACK or skill.skill_type == SkillType.DEBUFF:
        return OffensiveTargetSelector().select_target(skill, caster, context)
    elif skill.skill_type == SkillType.HEAL or skill.skill_type == SkillType.BUFF:
        return SupportiveTargetSelector().select_target(skill, caster, context)
    elif skill.skill_type == SkillType.REVIVE:
        return ReviveTargetSelector().select_target(skill, caster, context)
    elif skill.skill_type == SkillType.SPECIAL:
        return OffensiveTargetSelector().select_target(skill, caster, context)
    else:
        return OffensiveTargetSelector().select_target(skill, caster, context)

