from hero import Hero
from team import Team

class BattleContext:
    """战斗上下文"""
    def __init__(self, team1: Team, team2: Team):
        self.team1 = team1
        self.team2 = team2
        self.current_round = 0
        
    def get_ally_team(self, hero: Hero) -> Team:
        """获取英雄的盟友队伍"""
        if hero in self.team1.get_all_heroes():
            return self.team1
        return self.team2
        
    def get_enemy_team(self, hero: Hero) -> Team:
        """获取英雄的敌方队伍"""
        if hero in self.team1.get_all_heroes():
            return self.team2
        return self.team1
    
    def get_hero_identifier(self, hero: Hero) -> str:
        """获取英雄的完整标识符"""
        if hero in self.team1.get_all_heroes():
            position = self.team1.get_all_heroes().index(hero) + 1
            return f"T1-{position}.{hero.name}"
        else:
            position = self.team2.get_all_heroes().index(hero) + 1
            return f"T2-{position}.{hero.name}"
    
    def get_hero_identifier_short(self, hero: Hero) -> str:
        """获取英雄的简短标识符（用于日志）"""
        if hero in self.team1.get_all_heroes():
            position = self.team1.get_all_heroes().index(hero) + 1
            return f"T1-{position}"
        else:
            position = self.team2.get_all_heroes().index(hero) + 1
            return f"T2-{position}"