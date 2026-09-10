"""
队伍相关类定义
"""

from typing import List, Optional, Tuple
from hero_pool import create_hero_instance


from hero import Hero

class Team:
    """阵容类"""
    def __init__(self, team_config: List[Tuple[int, int]]):
        """
        初始化队伍
        :param team_config: [(hero_id, secondary_skill_id), ...]
        """
        self.heroes: List[Optional['Hero']] = []
        for hero_id, secondary_skill_id in team_config:
            hero = create_hero_instance(hero_id, secondary_skill_id)
            if hero:
                self.heroes.append(hero)
            
    def get_alive_heroes(self) -> List[Hero]:
        """获取存活的英雄"""
        return [hero for hero in self.heroes if hero.is_alive]
        
    def get_all_heroes(self) -> List[Hero]:
        """获取所有英雄（包括死亡的）"""
        return self.heroes
        
    def get_hero_index(self, hero: Hero) -> Optional[int]:
        """获取英雄索引"""
        try:
            return self.heroes.index(hero)
        except ValueError:
            return None
            
    def is_defeated(self) -> bool:
        """是否被击败"""
        return len(self.get_alive_heroes()) == 0
    