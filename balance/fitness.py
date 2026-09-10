from typing import List, Dict

def calculate_individual_fitness(battle_results: List[Dict]) -> float:
    """通过已有战斗结果 计算单个个体的适应度"""

    # 权重定义
    win_rate_weight = 0.7          # 胜率权重
    damage_dealt_weight = 0.1      # 输出伤害权重
    remaining_hp_weight = 0.05     # 剩余血量权重
    survival_rate_weight = 0.1     # 存活率权重
    rounds_weight = 0.05            # 战斗回合数权重
    

    # 保存对每一个教练的适应度
    scores = []
    for result in battle_results:
        
        # win 胜负
        win = 0.5
        if result['winner'] == 'team1_win':
            win = 1
        elif result['winner'] == 'team2_win':
            win = 0
        else: # draw平局     
            win = 0.5
            
        # 因为存在笼络、赠与等改变团队结构的技能，需要处理
        my_hero_count = 0
        enemy_hero_count = 0
        for hero_stat in result['team1_stats']:
            my_hero_count += 1
        for hero_stat in result['team2_stats']:
            enemy_hero_count += 1

                
        # 回合数
        norm_rounds = 0
        MAX_ROUNDS = 50
        rounds = result['rounds']
        if win > 0.5:
            norm_rounds = (MAX_ROUNDS - rounds) / MAX_ROUNDS  # 胜利：回合少为好
        else:
            norm_rounds = rounds / MAX_ROUNDS  # 失败：回合多说明抗打击能力强（平局同）
            

        # 输出伤害
        my_damage_dealt = 0
        enemy_damage_dealt = 0
        for hero_stat in result['team1_stats']:
            my_damage_dealt += hero_stat['damage_dealt']
        for hero_stat in result['team2_stats']:
            enemy_damage_dealt += hero_stat['damage_dealt']
                
        all_damage = my_damage_dealt + enemy_damage_dealt # 要考虑分母是0的特殊情况
        if all_damage == 0:
            norm_damage_dealt = 0.5
        else:   
            norm_damage_dealt = my_damage_dealt / all_damage
            
        # 剩余生命比例
        my_remaining_hp = 0
        enemy_remaining_hp = 0
        my_base_hp = 0
        enemy_base_hp = 0
        
        for hero_stat in result['team1_stats']:
            my_remaining_hp += hero_stat['remaining_hp']
            my_base_hp += hero_stat['base_hp']
        for hero_stat in result['team2_stats']:
            enemy_remaining_hp += hero_stat['remaining_hp']
            enemy_base_hp += hero_stat['base_hp']
            
        if my_hero_count == 0:
            norm_remaining_hp = 0
        elif enemy_hero_count == 0:
            norm_remaining_hp = 1
        else:
            my_remaining_hp_ratio = my_remaining_hp / my_base_hp
            enemy_remaining_hp_ratio = enemy_remaining_hp / enemy_base_hp
            all_hp_ratio = my_remaining_hp_ratio + enemy_remaining_hp_ratio
            norm_remaining_hp = 0.5
            if all_hp_ratio > 0:
                norm_remaining_hp = my_remaining_hp_ratio / all_hp_ratio

        # 存活率
        my_alive = 0
        enemy_alive = 0
        HERO_COUNT = 3*2
        for hero_stat in result['team1_stats']:
            if hero_stat['is_alive']:
                my_alive += 1
        for hero_stat in result['team2_stats']:
            if hero_stat['is_alive']:
                enemy_alive += 1
        norm_alive = my_alive / HERO_COUNT
        
        # 计算单场战斗的加权适应度
        battle_fitness = (
            win_rate_weight * win +
            damage_dealt_weight * norm_damage_dealt +
            remaining_hp_weight * norm_remaining_hp +
            survival_rate_weight * norm_alive +
            rounds_weight * norm_rounds
        )
            
        scores.append(battle_fitness)
        
    # 计算平均适应度
    fitness = sum(scores) / len(scores)
    return fitness