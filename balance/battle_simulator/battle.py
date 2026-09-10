"""
战斗系统
"""

from typing import Dict, List, Optional, Tuple
from enums import HeroClass, HeroElement, DamageType, SkillType, BattleResult
from hero import Hero
from team import Team
from status_effect import StatusEffect
from target_selector import select_target
from battle_context import BattleContext



class BattleSimulator:
    """战斗模拟器"""
    
    def __init__(self):
        self.battle_log = []
        self.max_rounds = 50  # 最大回合数
        
    def get_turn_order(self, team1: Team, team2: Team) -> List[Hero]:
        """获取行动顺序（确定性排序）"""
        all_heroes = team1.get_alive_heroes() + team2.get_alive_heroes()
        # 按速度降序排序
        return sorted(all_heroes, key=lambda h: (-h.current_speed, h.hero_id))
        
    def simulate_battle(self, team1_config: List[Tuple[int, int]], 
                       team2_config: List[Tuple[int, int]]) -> Dict:
        """模拟战斗"""
        self.battle_log = []
        
        team1 = Team(team1_config)
        team2 = Team(team2_config)
        context = BattleContext(team1, team2)
        
        self.log(f"战斗开始！")
        
        # 记录队伍配置
        self.log(f"队伍1配置:")
        for i, (hero_id, skill_id) in enumerate(team1_config):
            hero = team1.heroes[i]
            secondary_skill = hero.skills[1]
            self.log(f"  {context.get_hero_identifier(hero)} + {secondary_skill.name} (ID:{skill_id})")
            
        self.log(f"队伍2配置:")
        for i, (hero_id, skill_id) in enumerate(team2_config):
            hero = team2.heroes[i]
            secondary_skill = hero.skills[1]
            self.log(f"  {context.get_hero_identifier(hero)} + {secondary_skill.name} (ID:{skill_id})")
        
        round_count = 0
        while round_count < self.max_rounds:
            round_count += 1
            context.current_round = round_count
            self.log(f"\n===== 第 {round_count} 回合 =====")  
            self.log(f"队伍1:")
            for hero in team1.get_all_heroes():
                self.log(f"  {context.get_hero_identifier(hero)}: {hero.current_hp}/{hero.base_hp}")
            self.log(f"队伍2:")
            for hero in team2.get_all_heroes():
                self.log(f"  {context.get_hero_identifier(hero)}: {hero.current_hp}/{hero.base_hp}")
            
            # 检查胜负
            if team1.is_defeated():
                self.log(f"队伍2 获胜！")
                return self.create_battle_result(team1, team2, BattleResult.TEAM2_WIN, round_count)
            elif team2.is_defeated():
                self.log(f"队伍1 获胜！")
                return self.create_battle_result(team1, team2, BattleResult.TEAM1_WIN, round_count)
                
            # 更新状态效果和技能冷却
            all_heroes = team1.get_all_heroes() + team2.get_all_heroes()
            for hero in all_heroes:
                if hero.is_alive:
                    # 更新状态效果
                    effect_messages = hero.update_status_effects(context)
                    for message in effect_messages:
                        self.log(message)
                    
                    hero.update_cooldowns()
                
            # 获取行动顺序
            turn_order = self.get_turn_order(team1, team2)
            # 为行动顺序添加阵营信息
            turn_order_with_team = [context.get_hero_identifier(hero) for hero in turn_order]
            self.log(f"行动顺序: {' -> '.join(turn_order_with_team)}")
            
            # 执行回合
            for hero in turn_order:
                # 再次检查胜负（可能在状态效果中有英雄死亡）
                if team1.is_defeated() or team2.is_defeated():
                    break
                    
                if not hero.can_act():
                    if hero.is_stunned():
                        self.log(f"【{context.get_hero_identifier(hero)}】被眩晕，无法行动！")
                    continue
                                       
                # 使用所有可用技能
                skills_used = self.use_all_available_skills(hero, context)
                if not skills_used:
                    self.log(f"【{context.get_hero_identifier(hero)}】没有可用的技能！")
                        
                # 检查是否有英雄死亡，及时更新战场状态
                if team1.is_defeated() or team2.is_defeated():
                    break
                    
        # 超过最大回合数，平局
        self.log("战斗超过最大回合数，平局！")
        return self.create_battle_result(team1, team2, BattleResult.DRAW, round_count)
        
    def use_all_available_skills(self, hero: Hero, context: BattleContext) -> bool:
        """使用所有可用的技能"""
        available_skills = hero.get_available_skills()
        if not available_skills:
            return False
            
        skills_used = False
        
        for skill in available_skills:
            # 目标选择
            target = select_target(skill, hero, context)
            if target:
                # 处理双重攻击
                attacks = 1
                from status_effect import DoubleAttackEffect
                double_attack_effect = hero.get_effect_by_type(DoubleAttackEffect)
                if (double_attack_effect 
                        and skill.skill_type == SkillType.ATTACK 
                        and double_attack_effect.attacks_remaining > 0):
                    attacks = 2
                    # 消耗一次双击
                    double_attack_effect.attacks_remaining -= 1
                    if double_attack_effect.attacks_remaining <= 0:
                        hero.status_effects.remove(double_attack_effect)
                    
                for i in range(attacks):
                    if attacks > 1:
                        self.log(f"【{context.get_hero_identifier(hero)}】使用《{skill.name}》的第{i+1}次攻击：")
                    
                    result = skill.use(hero, target, context)
                    self.log(result)
                    skills_used = True
                    
                    # 检查是否有英雄死亡，及时更新战场状态
                    if context.team1.is_defeated() or context.team2.is_defeated():
                        return True
                        
        return skills_used
        
    def create_battle_result(self, team1: Team, team2: Team, winner: BattleResult, rounds: int) -> Dict:
        """创建战斗结果"""
        result = {
            "winner": winner.value,
            "rounds": rounds,
            "team1_stats": [],
            "team2_stats": [],
        }
        
        for team_key, team in [("team1_stats", team1), ("team2_stats", team2)]:
            team_heroes = []
            for hero in team.get_all_heroes():
                hero_result = {
                    "hero_id": hero.hero_id,
                    "name": hero.name,
                    "is_alive": hero.is_alive,
                    "base_hp": hero.base_hp,
                    "remaining_hp": hero.current_hp,
                    "damage_dealt": hero.battle_stats.damage_dealt,
                    "damage_taken": hero.battle_stats.damage_taken,
                    "kills": hero.battle_stats.kills,
                    "deaths": hero.battle_stats.deaths,
                    "skills_used": hero.battle_stats.skills_used,

                }
                team_heroes.append(hero_result)
            result[team_key] = team_heroes
                
        return result
        
    def log(self, message: str):
        """记录战斗日志"""
        self.battle_log.append(message)
        print(message)