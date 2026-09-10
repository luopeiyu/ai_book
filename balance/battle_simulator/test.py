"""
测试文件
"""

import random

from battle import BattleSimulator
from enums import BattleResult
def test_single_battle():
    """测试单场战斗"""  
    # 预设的战斗配置
    team1_config = [(1, 0), (2, 11), (4, 15)]  
    team2_config = [(3, 2), (6, 11), (8, 17)]  
    simulator = BattleSimulator()
    result = simulator.simulate_battle(team1_config, team2_config)
    print(result)


def test_single_battle_multiple_times(count: int = 100):
    """测试同一队伍"""
    team1_config = [(1, 1), (1, 1), (1, 1)]  
    team2_config = [(1, 1), (1, 1), (1, 1)] 
    
    simulator = BattleSimulator()
    team1_win = 0
    team2_win = 0
    draw = 0
    for i in range(count):
        result = simulator.simulate_battle(team1_config, team2_config)
        if result['winner'] == "team1_win":
            team1_win += 1
        elif result['winner'] == "team2_win":
            team2_win += 1
        else:
            draw += 1
    print(f"胜利次数: {team1_win}, {team2_win}, {draw}")


def test_random_battles(num_battles: int = 100):
    """测试多场随机战斗"""
    
    simulator = BattleSimulator()

    
    for i in range(num_battles):
        print(f"第{i+1}场战斗")
        # 随机生成队伍配置，每队3个英雄
        team1_config = [(random.randint(0, 39), random.randint(0, 17)) for _ in range(3)]
        team2_config = [(random.randint(0, 39), random.randint(0, 17)) for _ in range(3)]
        
        print(team1_config)
        print(team2_config)
        result = simulator.simulate_battle(team1_config, team2_config)
        print(result)



if __name__ == "__main__":
    test_single_battle()
    # test_random_battles(1000) 
    # test_single_battle_multiple_times(100)