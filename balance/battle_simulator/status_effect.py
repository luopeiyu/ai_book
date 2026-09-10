"""
状态效果系统
"""


from typing import Optional, List, TYPE_CHECKING
from enums import DamageType, StackType




from abc import ABC, abstractmethod

class StatusEffect(ABC):
    """状态效果抽象基类"""
    
    # 每个子类需要定义自己的叠加方式
    STACK_TYPE: StackType = StackType.REPLACE
    
    def __init__(self, duration: int, source_hero):
        self.duration = duration
        self.source_hero = source_hero
        self.applied = False  # 是否已经应用过初始效果
    
    @property
    @abstractmethod
    def name(self) -> str:
        """状态效果名称"""
        pass
    
    @abstractmethod
    def apply_initial_effect(self, target, context) -> str:
        """应用初始效果（仅在第一次应用时调用）"""
        pass
    
    @abstractmethod
    def apply_periodic_effect(self, target, context) -> str:
        """应用周期性效果（每回合调用）"""
        pass
    
    @abstractmethod
    def remove_effect(self, target, context) -> str:
        """移除状态效果"""
        pass
    
    def can_stack_with(self, other) -> bool:
        """检查是否可以与另一个同类型状态效果叠加"""
        return isinstance(other, self.__class__)
    
    def stack_with(self, other) -> str:
        """与另一个同类型状态效果叠加"""
        if self.STACK_TYPE == StackType.REPLACE:
            self.duration = other.duration
            return f"状态效果被替换"
        elif self.STACK_TYPE == StackType.EXTEND:
            self.duration += other.duration
            return f"状态效果持续时间延长"
        elif self.STACK_TYPE == StackType.REFRESH:
            self.duration = other.duration
            return f"状态效果时间被刷新"
        elif self.STACK_TYPE == StackType.ACCUMULATE:
            return self._accumulate_effect(other)
        
        return ""
    
    def _accumulate_effect(self, other: 'StatusEffect') -> str:
        """累积效果（子类可重写）"""
        return "状态效果累积"
    
    def update(self, target, context) -> tuple[bool, str]:
        """更新状态效果，返回(是否应该移除, 消息)"""
        messages = []
        
        # 首次应用效果
        if not self.applied:
            initial_msg = self.apply_initial_effect(target, context)
            if initial_msg:
                messages.append(initial_msg)
            self.applied = True
        
        # 应用周期性效果
        periodic_msg = self.apply_periodic_effect(target, context)
        if periodic_msg:
            messages.append(periodic_msg)
        
        # 减少持续时间
        self.duration -= 1
        
        # 检查是否应该移除
        should_remove = self.duration <= 0
        if should_remove:
            remove_msg = self.remove_effect(target, context)
            if remove_msg:
                messages.append(remove_msg)
        
        return should_remove, " ".join(messages)

class StunEffect(StatusEffect):
    """眩晕效果"""
    STACK_TYPE = StackType.REFRESH
    
    def __init__(self, duration: int, source_hero):
        super().__init__(duration, source_hero)
    
    @property
    def name(self) -> str:
        return "眩晕"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】被施加了〖眩晕〗效果"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        return ""  # 眩晕效果在can_act中检查
    
    def remove_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖眩晕〗效果消失了"

class ChargeEffect(StatusEffect):
    """蓄力效果"""
    STACK_TYPE = StackType.EXTEND
    
    def __init__(self, duration: int, multiplier: float, source_hero):
        super().__init__(duration, source_hero)
        self.multiplier = multiplier
    
    @property
    def name(self) -> str:
        return "蓄力"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】开始〖蓄力〗"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        return ""
    
    def remove_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖蓄力〗效果消失了"
    
    def get_attack_multiplier(self) -> float:
        return self.multiplier

class DoubleAttackEffect(StatusEffect):
    """双重攻击效果"""
    STACK_TYPE = StackType.EXTEND
    
    def __init__(self, duration: int, source_hero):
        super().__init__(duration, source_hero)
        self.attacks_remaining = 2  # 默认双击一次（两次攻击）
    
    @property
    def name(self) -> str:
        return "双重攻击"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】获得〖双重攻击〗效果"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        return ""
    
    def remove_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖双重攻击〗效果消失了"

class MineEffect(StatusEffect):
    """地雷效果"""
    STACK_TYPE = StackType.REPLACE
    
    def __init__(self, duration: int, source_hero):
        super().__init__(duration, source_hero)
        self.has_exploded = False
    
    @property
    def name(self) -> str:
        return "地雷"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】被绑定了〖地雷〗"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        if self.duration <= 1 and not self.has_exploded:
            # 地雷爆炸
            self.has_exploded = True
            if context:
                explosion_msg = self.trigger_explosion(target, context)
                return explosion_msg
            else:

                return f"〖地雷〗在【{target_id}】身上爆炸了！"
        elif not self.has_exploded:
            return f"【{target_id}】身上的〖地雷〗还有{self.duration-1}回合爆炸"
        return ""
    
    def remove_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        if not self.has_exploded:
            return f"【{target_id}】身上的〖地雷〗被解除了"
        return ""
    
    def trigger_explosion(self, target, context) -> str:
        """触发地雷爆炸"""
        from enums import DamageType
        target_id = context.get_hero_identifier(target)
        # 确定目标所在的队伍
        if target.is_controlled() and hasattr(target, 'original_team'):
            # 如果目标被控制，爆炸影响原队伍
            if target in context.team1.get_all_heroes():
                target_team = context.team2  # 原来的队伍
            else:
                target_team = context.team1
        else:
            # 正常情况，影响当前队伍
            target_team = context.get_ally_team(target)
            
        results = []
        for hero in target_team.get_alive_heroes():
            damage = int(hero.current_hp * 0.5)
            actual_damage = hero.take_damage(damage, DamageType.FIXED)
            if self.source_hero:
                self.source_hero.battle_stats.damage_dealt += actual_damage
            hero_id = context.get_hero_identifier(hero)
            results.append(f"【{hero_id}】受到{actual_damage}点爆炸伤害")
            
        explosion_details = "，".join(results) if results else "但没有造成伤害"
        return f"〖地雷〗在【{target_id}】身上爆炸！{explosion_details}！"
    
    def should_trigger_explosion(self, target) -> bool:
        """检查是否应该触发爆炸"""
        return self.duration <= 1 and not self.has_exploded

class ArmorEffect(StatusEffect):
    """护甲效果"""
    STACK_TYPE = StackType.REPLACE
    
    def __init__(self, duration: int, hits: int, source_hero):
        super().__init__(duration, source_hero)
        self.hits_remaining = hits
    
    @property
    def name(self) -> str:
        return "护甲"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target.current_defense = int(target.base_defense * 1.5)
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】获得〖护甲〗效果，可承受{self.hits_remaining}次攻击"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        return ""
    
    def remove_effect(self, target, context=None) -> str:
        target.current_defense = target.base_defense
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖护甲〗效果消失了"
    
    def apply_damage_reduction(self, damage: int, damage_type: DamageType) -> int:
        """应用伤害减免"""
        if self.hits_remaining > 0:
            self.hits_remaining -= 1
            if damage_type == DamageType.FIXED:
                return int(damage * 2 / 3)
            
            # 如果护甲耗尽，移除效果
            if self.hits_remaining <= 0:
                self.duration = 0
                
        return damage

class PoisonEffect(StatusEffect):
    """毒药效果"""
    STACK_TYPE = StackType.EXTEND
    
    def __init__(self, duration: int, damage: int, source_hero):
        super().__init__(duration, source_hero)
        self.damage = damage
    
    @property
    def name(self) -> str:
        return "毒药"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】中毒了"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        actual_damage = target.take_damage(self.damage, DamageType.FIXED)
        if self.source_hero:
            self.source_hero.battle_stats.damage_dealt += actual_damage
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】受到{actual_damage}点〖毒药〗伤害"
    
    def remove_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖毒药〗效果消失了"
    
    def _accumulate_effect(self, other) -> str:
        self.damage += other.damage
        self.duration = max(self.duration, other.duration)
        return f"〖毒药〗效果加强，伤害增加到{self.damage}"

class BigPoisonEffect(StatusEffect):
    """大毒药效果"""
    STACK_TYPE = StackType.REFRESH
    
    def __init__(self, duration: int, source_hero):
        super().__init__(duration, source_hero)
    
    @property
    def name(self) -> str:
        return "大毒药"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】中了〖剧毒〗"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        damage = int(target.current_hp * 0.3)
        actual_damage = target.take_damage(damage, DamageType.FIXED)
        if self.source_hero:
            self.source_hero.battle_stats.damage_dealt += actual_damage
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】受到{actual_damage}点〖剧毒〗伤害"
    
    def remove_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖剧毒〗效果消失了"

class HiddenEffect(StatusEffect):
    """隐身效果"""
    STACK_TYPE = StackType.REFRESH
    
    def __init__(self, duration: int, source_hero):
        super().__init__(duration, source_hero)
    
    @property
    def name(self) -> str:
        return "隐身"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】进入〖隐身〗状态"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        return ""  # 隐身没有周期性效果
    
    def remove_effect(self, target, context=None) -> str:
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖隐身〗效果消失了"

class SpeedBoostEffect(StatusEffect):
    """速度提升效果"""
    STACK_TYPE = StackType.REFRESH
    
    def __init__(self, duration: int, source_hero):
        super().__init__(duration, source_hero)
    
    @property
    def name(self) -> str:
        return "速度提升"
    
    def apply_initial_effect(self, target, context=None) -> str:
        target.current_speed = target.base_speed * 2
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】获得〖速度提升〗效果"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        return ""  # 速度提升没有周期性效果
    
    def remove_effect(self, target, context=None) -> str:
        target.current_speed = target.base_speed
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】的〖速度提升〗效果消失了"

class ControlledEffect(StatusEffect):
    """被控制效果"""
    STACK_TYPE = StackType.REPLACE
    
    def __init__(self, duration: int, source_hero, original_team=None):
        super().__init__(duration, source_hero)
        self.original_team = original_team  # 保存原队伍信息
    
    @property
    def name(self) -> str:
        return "被控制"
    
    def apply_initial_effect(self, target, context=None) -> str:
        # 在应用控制效果时，保存原队伍信息
        
        target_id = context.get_hero_identifier(target)
        return f"【{target_id}】被〖控制〗了"
    
    def apply_periodic_effect(self, target, context=None) -> str:
        return ""  # 控制效果的逻辑在技能中处理
    
    def remove_effect(self, target, context=None) -> str:
        """移除控制效果，归还到原队伍"""
        target_id = context.get_hero_identifier(target) 

        # 从当前队伍移除
        current_team = context.get_ally_team(target)
        if target in current_team.heroes:
            current_team.heroes.remove(target)
        
        # 归还到原队伍
        original_team = self.original_team
        if target not in original_team.heroes:
            original_team.heroes.append(target)
        
        return f"【{target_id}】摆脱了〖控制〗，回到了原队伍"
