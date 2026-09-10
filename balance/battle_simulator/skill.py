"""
技能系统
"""
import random
from typing import Optional, List, Tuple, Dict
from enums import DamageType, SkillType
from status_effect import (
    PoisonEffect, BigPoisonEffect, HiddenEffect, ArmorEffect, 
    SpeedBoostEffect, ControlledEffect, MineEffect, DoubleAttackEffect,
    ChargeEffect, StunEffect
)
from damage_calculator import damage_calc


class Skill:
    """技能基类"""
    def __init__(self, skill_id: int, name: str, description: str, skill_type: SkillType, cooldown: int = 0):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.cooldown = cooldown  # 技能冷却时间
        self.current_cooldown = 0  # 当前冷却时间
        self.use_count = 0  # 使用次数计数器
        
    def can_use(self, caster , target , battle_context) -> bool:
        """是否可以使用技能"""
        return caster.is_alive and caster.can_act() and self.current_cooldown <= 0
        
    def use(self, caster, target, battle_context) -> str:
        """使用技能"""
        caster.battle_stats.skills_used += 1
        self.use_count += 1
        # 设置冷却时间
        if self.cooldown > 0:
            self.current_cooldown = self.cooldown
        return self.execute(caster, target, battle_context)
        
    def execute(self, caster, target, battle_context) -> str:
        """执行技能效果"""
        raise NotImplementedError

# 具体技能实现

class NormalAttack(Skill):
    def __init__(self):
        super().__init__(1, "普通攻击", "基础物理攻击", SkillType.ATTACK, cooldown=0)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】攻击【{target_id}】，但【{target_id}】处于隐身状态，攻击无效！"
        
        damage = damage_calc.calculate_physical_damage(caster, target)
        actual_damage = target.take_damage(damage, DamageType.PHYSICAL)
        caster.battle_stats.damage_dealt += actual_damage
        
        if not target.is_alive:
            caster.battle_stats.kills += 1
        return f"【{caster_id}】攻击【{target_id}】，造成{actual_damage}点伤害！"

class ViolentStrike(Skill):
    def __init__(self):
        super().__init__(2, "暴力一击", "每2次使用造成双倍伤害，其他次数miss", SkillType.ATTACK, cooldown=0)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】使用《暴力一击》攻击【{target_id}】，但【{target_id}】处于隐身状态，攻击无效！"
        
        # 每2次使用成功一次
        if self.use_count % 2 == 0:
            # 2倍伤害
            damage = damage_calc.calculate_physical_damage(caster, target, 2.0)
            actual_damage = target.take_damage(damage, DamageType.PHYSICAL)
            caster.battle_stats.damage_dealt += actual_damage
            
            if not target.is_alive:
                caster.battle_stats.kills += 1
            return f"【{caster_id}】使用《暴力一击》攻击【{target_id}】，造成{actual_damage}点暴击伤害！"
        else:
            return f"【{caster_id}】使用《暴力一击》攻击【{target_id}】，但是失手了！"

class Charge(Skill):
    def __init__(self):
        super().__init__(3, "蓄力", "本回合不攻击，下回合伤害翻倍", SkillType.BUFF, cooldown=0)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)

        # 设定持续时间为2（本回合+下回合），保证下回合生效后自动失效
        effect = ChargeEffect(2, 2.0, caster)
        stack_msg = caster.add_status_effect(effect, battle_context)
        return f"【{caster_id}】开始《蓄力》。{stack_msg}"

class AdvancedCharge(Skill):
    def __init__(self):
        super().__init__(4, "高级蓄力", "本回合不攻击，下2回合攻击力翻倍", SkillType.BUFF, cooldown=1)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)

        # 持续3回合：本回合蓄力，下两回合增伤
        effect = ChargeEffect(3, 2.0, caster)
        stack_msg = caster.add_status_effect(effect, battle_context)
        return f"【{caster_id}】开始《高级蓄力》。{stack_msg}"

class SuperCharge(Skill):
    def __init__(self):
        super().__init__(5, "超级蓄力", "下个回合攻击2次", SkillType.BUFF, cooldown=2)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)

        # 持续2回合：本回合蓄力，下回合触发双击（内部会在使用后立即移除）
        effect = DoubleAttackEffect(2, caster)
        stack_msg = caster.add_status_effect(effect, battle_context)
        return f"【{caster_id}】进入《超级蓄力》状态。{stack_msg}"

class Poison(Skill):
    def __init__(self):
        super().__init__(6, "毒药", "连续2回合，每回合扣除100点血", SkillType.DEBUFF, cooldown=0)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】对【{target_id}】使用《毒药》，但【{target_id}】处于隐身状态，无法中毒！"
        
        duration = 2
        # 双重攻击仅影响攻击技能，毒药持续回合不受影响
        
        effect = PoisonEffect(duration, 100, caster)
        stack_msg = target.add_status_effect(effect, battle_context)
        return f"【{caster_id}】对【{target_id}】使用《毒药》。{stack_msg}"

class BigPoison(Skill):
    def __init__(self):
        super().__init__(7, "大毒药", "连续3回合，每回合扣除30%血量", SkillType.DEBUFF, cooldown=1)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】对【{target_id}】使用《大毒药》，但【{target_id}】处于隐身状态，无法中毒！"
        
        duration = 3
        # 双重攻击仅影响攻击技能
        
        effect = BigPoisonEffect(duration, caster)
        stack_msg = target.add_status_effect(effect, battle_context)
        return f"【{caster_id}】对【{target_id}】使用《大毒药》。{stack_msg}"

class GroupAttack(Skill):
    def __init__(self):
        super().__init__(8, "群体攻击", "攻击敌方全体", SkillType.ATTACK, cooldown=1)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        results = []
        enemy_team = battle_context.get_enemy_team(caster)
        
        # 按站位顺序攻击所有可见敌人
        for i, enemy in enumerate(enemy_team.heroes):
            if enemy and enemy.is_alive and not enemy.is_hidden():
                damage = damage_calc.calculate_physical_damage(caster, enemy)
                actual_damage = enemy.take_damage(damage, DamageType.PHYSICAL)
                caster.battle_stats.damage_dealt += actual_damage
                if not enemy.is_alive:
                    caster.battle_stats.kills += 1
                results.append(f"对位置{i+1}的【{enemy.name}】造成{actual_damage}点伤害")
        
        if not results:
            return f"【{caster_id}】使用《群体攻击》，但没有可攻击的目标！"
        
        return f"【{caster_id}】使用《群体攻击》：" + "，".join(results) + "！"

class SplashAttack(Skill):
    def __init__(self):
        super().__init__(9, "溅射攻击", "主目标受到完整伤害，相邻敌人受到一半伤害", SkillType.ATTACK, cooldown=0)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】使用《溅射攻击》，但主目标【{target_id}】处于隐身状态，攻击无效！"
        
        results = []
        enemy_team = battle_context.get_enemy_team(caster)
        
        # 主目标受到完整伤害
        main_damage = damage_calc.calculate_physical_damage(caster, target)
        actual_main_damage = target.take_damage(main_damage, DamageType.PHYSICAL)
        caster.battle_stats.damage_dealt += actual_main_damage
        
        # 获取主目标的位置
        target_position = enemy_team.get_hero_index(target)
        results.append(f"对位置{target_position+1}的【{target_id}】造成{actual_main_damage}点伤害")
        
        if not target.is_alive:
            caster.battle_stats.kills += 1
            
        # 相邻敌人受到一半伤害
        if target_position is not None:
            adjacent_positions = [target_position - 1, target_position + 1]
            for pos in adjacent_positions:
                if 0 <= pos < len(enemy_team.heroes):
                    adjacent_enemy = enemy_team.heroes[pos]
                    if adjacent_enemy and adjacent_enemy.is_alive and not adjacent_enemy.is_hidden():
                        # 一半伤害
                        splash_damage = damage_calc.calculate_physical_damage(caster, adjacent_enemy, 0.5)
                        actual_splash_damage = adjacent_enemy.take_damage(splash_damage, DamageType.PHYSICAL)
                        caster.battle_stats.damage_dealt += actual_splash_damage
                        results.append(f"溅射对位置{pos+1}的【{adjacent_enemy.name}】造成{actual_splash_damage}点伤害")
                        if not adjacent_enemy.is_alive:
                            caster.battle_stats.kills += 1
        
        return f"【{caster_id}】使用《溅射攻击》：" + "，".join(results) + "！"

class Heal(Skill):
    def __init__(self):
        super().__init__(10, "治疗", "增加血量为(施法者攻击力+受治疗者防御力)/2", SkillType.HEAL, cooldown=0)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if not target.is_alive:
            return f"【{caster_id}】尝试《治疗》【{target_id}】，但【{target_id}】已经死亡！"
        
        heal_amount = (caster.current_attack + target.current_defense) // 2
        # 双重攻击不影响治疗量
        
        actual_heal = target.heal(heal_amount)
        return f"【{caster_id}】《治疗》【{target_id}】，恢复{actual_heal}点生命值！"

class Revive(Skill):
    def __init__(self):
        super().__init__(11, "复活", "复活己方死亡英雄，恢复50%生命值", SkillType.REVIVE, cooldown=2)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_alive:
            return f"【{caster_id}】尝试《复活》【{target_id}】，但【{target_id}】还活着！"
        
        hp_percentage = 0.5
        # 双重攻击不影响复活量
        
        target.revive(hp_percentage)
        return f"【{caster_id}】《复活》了【{target_id}】，恢复{int(hp_percentage*100)}%生命值！"

class Stun(Skill):
    def __init__(self):
        super().__init__(12, "眩晕", "每3次使用成功眩晕敌人一次", SkillType.DEBUFF, cooldown=0)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】尝试《眩晕》【{target_id}】，但【{target_id}】处于隐身状态，眩晕无效！"
        
        # 每3次使用成功一次
        if self.use_count % 3 == 0:

            effect = StunEffect(2, caster)
            stack_msg = target.add_status_effect(effect, battle_context)
            return f"【{caster_id}】成功《眩晕》了【{target_id}】。{stack_msg}"
        else:
            return f"【{caster_id}】尝试《眩晕》【{target_id}】，但是失败了！"

class Invisibility(Skill):
    def __init__(self):
        super().__init__(13, "隐身", "目标隐身2回合，无法被技能影响", SkillType.BUFF, cooldown=2)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        duration = 2
        # 双重攻击不影响隐身持续
        
        effect = HiddenEffect(duration, caster)
        stack_msg = target.add_status_effect(effect, battle_context)
        return f"【{caster_id}】对【{target_id}】使用《隐身》。{stack_msg}"

class Armor(Skill):
    def __init__(self):
        super().__init__(14, "护甲", "防御力变为1.5倍，可以承受2次伤害", SkillType.BUFF, cooldown=1)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        duration = 2
        hits = 2
        # 双重攻击不影响护甲参数
        
        effect = ArmorEffect(duration, hits, caster)
        stack_msg = target.add_status_effect(effect, battle_context)
        return f"【{caster_id}】为【{target_id}】施加《护甲》。{stack_msg}"

class SpeedBoost(Skill):
    def __init__(self):
        super().__init__(15, "速度提高", "速度值乘2，2次行动内有效", SkillType.BUFF, cooldown=2)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        duration = 2
        # 双重攻击不影响速度提升
        
        effect = SpeedBoostEffect(duration, caster)
        target.add_status_effect(effect, battle_context)
        return f"【{caster_id}】为【{target_id}】提升《速度》，速度翻倍{duration}次行动！"

class Recruit(Skill):
    def __init__(self):
        super().__init__(16, "笼络", "每3次使用成功笼络敌方角色一次", SkillType.SPECIAL, cooldown=1)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】尝试《笼络》【{target_id}】，但【{target_id}】处于隐身状态，笼络无效！"
        
        if self.use_count % 3 == 0:
            # 保存原队伍信息
            original_team = battle_context.get_ally_team(target)
            caster_team = battle_context.get_ally_team(caster)
            
            # 从原队伍移除，加入施法者队伍
            if target in original_team.heroes:
                original_team.heroes.remove(target)
                caster_team.heroes.append(target)
            
            # 创建控制效果，传入原队伍信息
            effect = ControlledEffect(1, caster, original_team)
            target.add_status_effect(effect, battle_context)
            return f"【{caster_id}】成功《笼络》了【{target_id}】，【{target_id}】将为我方战斗1回合！"
        else:
            return f"【{caster_id}】尝试《笼络》【{target_id}】，但是失败了！"

class Betray(Skill):
    def __init__(self):
        super().__init__(17, "背叛", "每5次使用成功背叛一次", SkillType.SPECIAL, cooldown=1)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if self.use_count % 5 == 0:
            # 保存原队伍信息
            original_team = battle_context.get_ally_team(caster)
            enemy_team = battle_context.get_enemy_team(caster)
            
            # 从原队伍移除，加入敌方队伍
            if caster in original_team.heroes:
                original_team.heroes.remove(caster)
                enemy_team.heroes.append(caster)
            
            # 创建控制效果，传入原队伍信息
            effect = ControlledEffect(3, caster, original_team)
            caster.add_status_effect(effect, battle_context)
            return f"【{caster_id}】《背叛》了自己的队伍，将为敌方战斗3回合！"
        else:
            return f"【{caster_id}】尝试《背叛》，但是犹豫了！"

class Mine(Skill):
    def __init__(self):
        super().__init__(18, "地雷", "给目标绑定地雷，2回合后引爆，所在阵营全体扣血50%", SkillType.DEBUFF, cooldown=2)
        
    def execute(self, caster, target, battle_context):
        caster_id = battle_context.get_hero_identifier(caster)
        target_id = battle_context.get_hero_identifier(target)
        if target.is_hidden():
            return f"【{caster_id}】尝试给【{target_id}】绑定《地雷》，但【{target_id}】处于隐身状态，绑定失败！"
        
        effect = MineEffect(2, caster)
        stack_msg = target.add_status_effect(effect, battle_context)
        return f"【{caster_id}】给【{target_id}】绑定了《地雷》。{stack_msg}"



