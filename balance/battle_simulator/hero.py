"""
英雄类定义
"""

from typing import List, Optional
from enums import HeroClass, HeroElement, DamageType
from battle_stats import BattleStats
from skill_pool import create_skill_instance
from status_effect import StatusEffect, ArmorEffect, HiddenEffect, StunEffect, ChargeEffect, DoubleAttackEffect

class Hero:
    """英雄类"""
    def __init__(self, hero_id: int, name: str, hero_class: HeroClass, element: HeroElement, 
                 attack: int, defense: int, hp: int, speed: int, 
                 basic_skill_id: int, secondary_skill_id: int):
        
        self.hero_id = hero_id
        self.name = name
        self.hero_class = hero_class
        self.element = element
        self.base_attack = attack
        self.base_defense = defense
        self.base_hp = hp
        self.base_speed = speed
        self.basic_skill_id = basic_skill_id
        self.secondary_skill_id = secondary_skill_id
        
        # 技能实例
        basic_skill = create_skill_instance(self.basic_skill_id)
        secondary_skill = create_skill_instance(self.secondary_skill_id)
        self.skills = [basic_skill, secondary_skill]
        
        # 当前状态
        self.current_hp = hp
        self.current_attack = attack
        self.current_defense = defense
        self.current_speed = speed
        
        # 状态效果
        self.status_effects = []
        
        # 战斗统计
        self.battle_stats = BattleStats()
        
        # 基础状态
        self.is_alive = True
        # 控制类效果需要记录原队伍
        self.original_team = None
        
    def get_available_skills(self):
        """获取可用的技能"""
        available_skills = []
        for skill in self.skills:
            if skill.current_cooldown <= 0:
                available_skills.append(skill)
        return available_skills
        
    def update_cooldowns(self):
        """更新技能冷却时间"""
        for skill in self.skills:
            if skill.current_cooldown > 0:
                skill.current_cooldown -= 1
    
    def update_status_effects(self, context=None) -> List[str]:
        """更新状态效果，返回效果消息列表"""
        effects_to_remove = []
        messages = []
        
        for effect in self.status_effects[:]:
            should_remove, message = effect.update(self, context)
            if message:
                messages.append(message)
            if should_remove:
                effects_to_remove.append(effect)
        
        # 移除已过期的状态效果
        for effect in effects_to_remove:
            if effect in self.status_effects:
                self.status_effects.remove(effect)
        
        return messages
        
    def take_damage(self, damage: int, damage_type: DamageType = DamageType.PHYSICAL) -> int:
        """承受伤害"""
        if not self.is_alive or self.is_hidden():
            return 0
            
        actual_damage = damage
        
        # 护甲效果
        armor_effect = self.get_effect_by_type(ArmorEffect)
        if armor_effect:
            actual_damage = armor_effect.apply_damage_reduction(damage, damage_type)
            
        self.current_hp -= actual_damage
        self.battle_stats.damage_taken += actual_damage
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.die()
            
        return actual_damage
        
    def heal(self, amount: int) -> int:
        """治疗"""
        if not self.is_alive:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = min(self.current_hp + amount, self.base_hp)
        return self.current_hp - old_hp
        
    def die(self):
        """死亡"""
        self.is_alive = False
        self.battle_stats.deaths += 1
        self.status_effects.clear()
        
    def revive(self, hp_percentage: float):
        """复活"""
        if self.is_alive:
            return
            
        self.is_alive = True
        self.current_hp = int(self.base_hp * hp_percentage)
        
    def add_status_effect(self, effect: StatusEffect, context=None):
        """添加状态效果"""
        # 检查是否已经有同类型的状态效果
        existing_effect = None
        for i, existing in enumerate(self.status_effects):
            if effect.can_stack_with(existing):
                existing_effect = existing
                break
        
        if existing_effect:
            # 如果已有同类型效果，进行叠加
            stack_msg = existing_effect.stack_with(effect)
            return stack_msg
        else:
            # 如果没有同类型效果，直接添加
            self.status_effects.append(effect)
            hero_id = context.get_hero_identifier(self)
            return f"【{hero_id}】获得〖{effect.name}〗效果"
    
    def can_act(self) -> bool:
        """是否可以行动"""
        return self.is_alive and not self.is_stunned()
    
    def get_effective_attack(self) -> int:
        """获取有效攻击力"""
        multiplier = 1.0
        charge_effect = self.get_effect_by_type(ChargeEffect)
        if charge_effect:
            multiplier = charge_effect.get_attack_multiplier()
        return int(self.current_attack * multiplier)
    
    def is_stunned(self) -> bool:
        """是否被眩晕"""
        return self.get_effect_by_type(StunEffect) is not None
    
    def is_hidden(self) -> bool:
        """是否隐身"""
        return self.get_effect_by_type(HiddenEffect) is not None
    
    def is_controlled(self) -> bool:
        """是否被控制"""
        from status_effect import ControlledEffect
        return self.get_effect_by_type(ControlledEffect) is not None
    
    def has_double_attack(self) -> bool:
        """是否有双重攻击"""
        return self.get_effect_by_type(DoubleAttackEffect) is not None
    
    def get_effect_by_type(self, effect_type):
        """根据类型获取状态效果"""
        for effect in self.status_effects:
            if isinstance(effect, effect_type):
                return effect
        return None