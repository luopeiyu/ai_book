"""
伤害计算系统
"""

from enums import HeroClass, HeroElement
from damage_constants import CLASS_COUNTER, ELEMENT_COUNTER, CLASS_MODIFIER, ELEMENT_MODIFIER


class DamageCalculator:
    """伤害计算器"""
    
    @classmethod
    def calculate_damage_modifier(cls, attacker, defender) -> float:
        """计算伤害修正系数"""
        modifier = 1.0
        
        # 职业克制
        if CLASS_COUNTER.get(attacker.hero_class) == defender.hero_class:
            modifier *= CLASS_MODIFIER
            
        # 元素克制
        if ELEMENT_COUNTER.get(attacker.element) == defender.element:
            modifier *= ELEMENT_MODIFIER
            
        return modifier
    
    @classmethod
    def apply_damage_with_modifiers(cls, attacker, defender, base_damage: int) -> int:
        """应用属性克制修正的伤害计算"""
        modifier = cls.calculate_damage_modifier(attacker, defender)
        modified_damage = int(base_damage * modifier)
        return max(0, modified_damage - defender.current_defense)
    
    @classmethod
    def calculate_physical_damage(cls, attacker, defender, damage_multiplier: float = 1.0) -> int:
        """计算物理伤害"""
        base_damage = int(attacker.get_effective_attack() * damage_multiplier)
        return cls.apply_damage_with_modifiers(attacker, defender, base_damage)
    



# 创建全局实例
damage_calc = DamageCalculator() 