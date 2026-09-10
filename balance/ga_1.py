"""
阵容挖掘遗传算法
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import time
import matplotlib.pyplot as plt
from dataclasses import dataclass
import json
import copy
from http_client import BattleSimulatorClient

HERO_POOL = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]
SKILL_POOL = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]




class TeamIndividual:
    """队伍个体"""
    
    def __init__(self, team_config: List[Tuple[int, int]]):
        """
        初始化队伍个体
        
        Args:
            team_config: 队伍配置 [(hero_id, skill_id), ...]
        """
        self.team_config = team_config
        self.fitness: float = 0.0
    
    def is_valid(self) -> bool:
        """检查队伍配置是否有效"""
        if len(self.team_config) != 3:
            return False
        
        used_heroes = set()
        
        for hero_id, skill_id in self.team_config:
            # 检查英雄是否重复
            if hero_id in used_heroes:
                return False
            used_heroes.add(hero_id)
        
        return True
    
    def __eq__(self, other):
        return self.team_config == other.team_config
    
    def get_hero_ids(self) -> List[int]:
        """获取英雄ID列表"""
        return [hero_id for hero_id, _ in self.team_config]
    
    @staticmethod
    def repair_individual(individual):
        """修复个体配置中的英雄冲突"""
        team_config = individual.team_config.copy()
        used_heroes = set()
        
        # 记录已使用的英雄，检查冲突
        for i, (hero_id, skill_id) in enumerate(team_config):
            if hero_id in used_heroes:
                # 发现英雄冲突，标记
                team_config[i] = (-1, skill_id)
            else:
                used_heroes.add(hero_id)
        
        # 第二遍：修复英雄冲突
        available_heroes = [h for h in HERO_POOL if h not in used_heroes]
        
        for i, (hero_id, skill_id) in enumerate(team_config):
            if hero_id == -1:  # 需要修复英雄
                if available_heroes:
                    new_hero = random.choice(available_heroes)
                    team_config[i] = (new_hero, skill_id)
                    available_heroes.remove(new_hero)
                    used_heroes.add(new_hero)
                else:
                    # 如果没有可用的英雄，生成一个新的有效配置
                    team_config = TeamIndividual.generate_random_team()
                    break
        
        return TeamIndividual(team_config)
    
    @staticmethod
    def generate_random_team():
        """生成随机队伍配置"""
        hero_ids = random.sample(HERO_POOL, 3)  # 英雄不重复
        skill_ids = [random.choice(SKILL_POOL) for _ in range(3)]  # 技能可以重复
        team_config = list(zip(hero_ids, skill_ids))
        return TeamIndividual(team_config)
    
    def __str__(self) -> str:
        return f"Team{self.team_config} (fitness: {self.fitness:.4f})"

    @staticmethod
    def test():
        """测试"""
        '''
        print("测试 generate_random_team")
        team = TeamIndividual.generate_random_team()
        print(team) # Team[(25, 6), (19, 3), (12, 11)] (fitness: 0.0000)
        
        print("测试 is_valid")
        team = TeamIndividual([(0,0),(1,1),(2,2)])
        print(team.is_valid()) # True
        team = TeamIndividual([(0,0),(1,1),(1,1)])
        print(team.is_valid()) # False
        
        print("测试 __eq__ ==判断") # 如果没有实现__eq__，全部会返回false
        team1 = TeamIndividual([(0,0),(1,1),(2,2)])
        team2 = TeamIndividual([(0,0),(1,1),(2,2)])
        print(team1 == team2) # True
        team3 = TeamIndividual([(0,0),(1,1),(3,2)])
        team4 = TeamIndividual([(0,0),(2,2),(1,1)]) 
        print(team1 == team3) # False
        print(team1 == team4) # False
        '''
        print("测试 __eq__ in判断")  # 如果没有实现__eq__，1234都会被加入herolist，实现后只有134
        team1 = TeamIndividual([(0,0),(1,1),(2,2)])
        team2 = TeamIndividual([(0,0),(1,1),(2,2)])
        team3 = TeamIndividual([(0,0),(1,1),(3,2)])
        team4 = TeamIndividual([(0,0),(2,2),(1,1)]) 
        herolist = []
        for i,team in enumerate([team1, team2, team3, team4]):
            if team not in herolist:
                herolist.append(team)
                print(i,team)

        

class TeamGeneticAlgorithm:
    """队伍遗传算法"""
    
    def __init__(self, 
                 client: BattleSimulatorClient,
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.15,
                 crossover_rate: float = 0.8,
                 elite_rate: float = 0.1,
                 initial_coach_teams: Optional[List[List[Tuple[int, int]]]] = None):
                
        """
        初始化遗传算法
        
        Args:
            client: 战斗模拟器客户端
            population_size: 种群大小
            generations: 迭代代数
            mutation_rate: 变异率
            crossover_rate: 交叉率
            elite_rate: 精英保留率
            fitness_weights: 适应度权重配置
            coach_teams: 教练队伍列表，如果为None则自动生成
        """
        self.client = client
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_rate = elite_rate
        self.elite_size = max(1, int(population_size * elite_rate))
        
        self.coach_teams = initial_coach_teams

        # 统计信息
        self.generation_stats = []
               
    def create_population(self) -> List[TeamIndividual]:
        """创建初始种群（确保无重复）"""
        population = []
        max_attempts = self.population_size * 10  # 最大尝试次数
        attempts = 0
        
        while len(population) < self.population_size and attempts < max_attempts:
            individual = TeamIndividual.generate_random_team()
            if individual not in population:
                population.append(individual)
            attempts += 1
        
        if len(population) < self.population_size:
            print(f"警告：只能生成 {len(population)} 个不重复的有效个体，少于目标 {self.population_size}")
        
        return population
    
    
    def calculate_fitness_batch(self, individuals: List[TeamIndividual]) -> None:
        """
        通过模拟器对战批量计算个体适应度
        
        Args:
            individuals: 需要计算适应度的个体列表
        """
        # 构造参数
        teams1 = [individual.team_config for individual in individuals]
        teams2 = [coach_team.team_config for coach_team in self.coach_teams]
        
        # 批量模拟战斗
        individual_results = self.client.simulate_batch_battles_bidirection(teams1, teams2)
            
        # 计算适应度
        for i, individual in enumerate(individuals):
            self.calculate_individual_fitness(individual, individual_results[i])
                
    
    def calculate_individual_fitness(self, individual: TeamIndividual, battle_results: List[Dict]) -> None:
        """通过已有战斗结果 计算单个个体的适应度"""
        
        # 统计胜场数
        wins = 0
        total_battles = len(battle_results)
        
        for result in battle_results:
            if result['winner'] == 'team1_win':
                wins += 1
            elif result['winner'] == 'draw':
                wins += 0.5  # 平局算半胜
        
        # 胜率作为适应度
        individual.fitness = wins / total_battles if total_battles > 0 else 0.0

           
    def tournament_selection(self, population: List[TeamIndividual], tournament_size: int = 3) -> TeamIndividual:
        """锦标赛选择"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def order_crossover(self, parent1: TeamIndividual, parent2: TeamIndividual) -> Tuple[TeamIndividual, TeamIndividual]:
        """
        顺序交叉 - 保持英雄不重复的约束
        """
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        

        # 随机选择交叉点
        cross_point = random.randint(1, 2)
        
        # 生成子代1
        child1_config = parent1.team_config[:cross_point] + parent2.team_config[cross_point:]
        child1 = TeamIndividual(child1_config)
        
        # 生成子代2
        child2_config = parent2.team_config[:cross_point] + parent1.team_config[cross_point:]
        child2 = TeamIndividual(child2_config)
        
        # 如果子代无效，则进行修复
        if not child1.is_valid():
            child1 = TeamIndividual.repair_individual(child1)
        
        if not child2.is_valid():
            child2 = TeamIndividual.repair_individual(child2)
        
        return child1, child2
    

    
    def mutate(self, individual: TeamIndividual) -> TeamIndividual:
        """变异操作"""
        if random.random() > self.mutation_rate:
            return individual
        
        mutated = copy.deepcopy(individual)
        mutation_type = random.choice(['hero', 'skill', 'both', 'swap_order'])
        
        # 随机选择一个位置进行变异
        position = random.randint(0, 2)
        
        old_hero, old_skill = mutated.team_config[position]
        
        if mutation_type == 'hero':
            # 更换英雄
            new_hero = random.choice(HERO_POOL)
            mutated.team_config[position] = (new_hero, old_skill)
            
        elif mutation_type == 'skill':
            # 更换技能
            new_skill = random.choice(SKILL_POOL)  # 技能可以重复，简化处理
            mutated.team_config[position] = (old_hero, new_skill)
                
        elif mutation_type == 'both':
            # 同时更换英雄和技能
            new_hero = random.choice(HERO_POOL)
            new_skill = random.choice(SKILL_POOL) 
            mutated.team_config[position] = (new_hero, new_skill)
            
        elif mutation_type == 'swap_order':
            # 交换位置
            mutated.team_config[position], mutated.team_config[random.randint(0, 2)] = \
                    mutated.team_config[random.randint(0, 2)], mutated.team_config[position]
        
        if not mutated.is_valid():
            mutated = TeamIndividual.repair_individual(mutated)
        
        return mutated
    
    def get_elite(self, population: List[TeamIndividual]) -> List[TeamIndividual]:
        """获取精英个体"""
        sorted_population = sorted(population, key=lambda x: x.fitness, reverse=True)
        return [copy.deepcopy(ind) for ind in sorted_population[:self.elite_size]]
    
    def evolve(self) -> Tuple[List[TeamIndividual], List[float]]:
        """主要的进化过程"""
        print(f"开始遗传算法优化")
        print(f"种群大小: {self.population_size}, 迭代代数: {self.generations}")
        print(f"教练队伍数量: {len(self.coach_teams)}")
        print(f"精英保留数量: {self.elite_size}")
        
        # 创建初始种群
        print("创建初始种群...")
        population = self.create_population()
        if len(population) < self.population_size:
            raise RuntimeError("无法创建足够的有效个体")
        
        for generation in range(self.generations):
            print(f"\n第 {generation + 1}/{self.generations} 代")
            print(f"当前种群大小: {len(population)}")
            
            self.calculate_fitness_batch(population)
            
            fitness_scores = [ind.fitness for ind in population]
            avg_fitness = np.mean(fitness_scores)
            max_fitness = max(fitness_scores)
            print(f"  平均适应度: {avg_fitness:.3f}, 最佳适应度: {max_fitness:.3f}")
            print(f"  所有个体适应度: {[f'{score:.2f}' for score in fitness_scores]}")
            print(f"  所有个体: {[str(ind) for ind in population]}")
            self.generation_stats.append({
                'generation': generation,
                'avg_fitness': avg_fitness,
                'max_fitness': max_fitness,
            })
            
            # 精英保留
            elite_individuals = self.get_elite(population)
            
            # 生成新种群（确保无重复）
            new_population = copy.deepcopy(elite_individuals)
            
            while len(new_population) < self.population_size:
                # 选择父代
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)
                
                # 交叉
                child1, child2 = self.order_crossover(parent1, parent2)
                
                # 变异
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                # 添加到新种群（避免重复）
                if child1 not in new_population:
                    new_population.append(child1)
                if len(new_population) < self.population_size and child2 not in new_population:
                    new_population.append(child2)
            
            population = new_population[:self.population_size]
        
        print(f"\n优化完成！")
        
        return population, self.generation_stats
    

def plot_fitness_evolution(generation_stats: List[Dict]):
    """绘制适应度进化曲线"""
    plt.figure(figsize=(10, 6))
    
    # 从generation_stats提取数据
    generations = [stat['generation'] for stat in generation_stats]
    avg_fitness = [stat['avg_fitness'] for stat in generation_stats]
    max_fitness = [stat['max_fitness'] for stat in generation_stats]
    
    # 画图
    plt.plot(generations, max_fitness, 'b-', linewidth=2, label='Best Fitness')
    plt.plot(generations, avg_fitness, 'r-', linewidth=2, label='Average Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness Evolution Curve')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()


def calculate_win_rate_matrix(final_population: List[TeamIndividual], coach_teams: List[TeamIndividual], client: BattleSimulatorClient):
    """计算最终种群对教练队伍的胜率矩阵"""
    # 统计相互交叉的N*M胜率表
    battles = []
    N = len(final_population)
    M = len(coach_teams)
    win_rate_matrix = [[0] * M for _ in range(N)]
    
    for i, team in enumerate(final_population):
        for j, coach_team in enumerate(coach_teams):
            battles.append({
                'team1_config': team.team_config,
                'team2_config': coach_team.team_config
            })
    battle_results = client.simulate_batch_battles(battles)
    
    # 统计胜率
    for i, result in enumerate(battle_results):
        team_idx = i // M
        coach_idx = i % M
        winner = result['winner']
        if winner == 'team1_win':
            win_rate_matrix[team_idx][coach_idx] = 1
    
    # 输出胜率矩阵
    print("胜率矩阵:")
    print("队伍\\教练", end="")
    for j in range(M):
        print(f"\t教练{j+1}", end="")
    print()
    
    for i, row in enumerate(win_rate_matrix):
        print(f"队伍{i+1}\t", end="")
        for j, win_rate in enumerate(row):
            print(f"\t{win_rate:.0%}", end="")
        print()

def main():
    """主函数"""

    
    # 创建客户端
    print("初始化客户端...")
    client = BattleSimulatorClient()
    
    print("测试连接...")
    try:
        health = client.health_check()
        print(f"服务状态: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"无法连接到战斗模拟器API: {e}")
        return
    
    coach_teams = [] # 验证跑出来比较强的
    coach_teams.append(TeamIndividual([(9, 15), (19, 15), (1, 15)]))
    coach_teams.append(TeamIndividual([(17, 15), (19, 15), (1, 15)]))
    coach_teams.append(TeamIndividual([(30, 15), (24, 16), (1, 15)]))
    coach_teams.append(TeamIndividual([(0, 16), (31, 16), (1, 15)])) 
    coach_teams.append(TeamIndividual([(21, 1), (30, 2), (3, 1)]))
    coach_teams.append(TeamIndividual([(21, 1), (30, 2), (31, 14)]))
    coach_teams.append(TeamIndividual([(21, 1), (30, 0), (1, 1)]))
    coach_teams.append(TeamIndividual([(17, 5), (30, 2), (1, 1)]))
    coach_teams.append(TeamIndividual([(30, 8), (15, 1), (28, 8)]))
    coach_teams.append(TeamIndividual([(32, 14), (15, 1), (37, 9)]))
    coach_teams.append(TeamIndividual([(32, 14), (15, 1), (23, 3)]))
    coach_teams.append(TeamIndividual([(15, 1), (23, 3), (22, 6)]))
    coach_teams.append(TeamIndividual([(36, 2), (22, 6), (15, 1)]))
    coach_teams.append(TeamIndividual([(15, 1), (22, 8), (36, 2)]))
    coach_teams.append(TeamIndividual([(23, 3), (30, 8), (15, 1)]))
    coach_teams.append(TeamIndividual([(22, 2), (32, 14), (15, 1)]))
    coach_teams.append(TeamIndividual([(30, 8), (15, 10), (7, 3)]))
    coach_teams.append(TeamIndividual([(15, 10), (7, 6), (30, 8)]))
    coach_teams.append(TeamIndividual([(6, 3), (30, 8), (15, 10)]))
    coach_teams.append(TeamIndividual([(15, 1), (6, 2), (39, 2)]))
    coach_teams.append(TeamIndividual([(30, 8), (15, 10), (6, 2)]))
    coach_teams.append(TeamIndividual([(30, 8), (15, 8), (31, 6)]))
    coach_teams.append(TeamIndividual([(30, 8), (15, 8), (7, 3)]))
    coach_teams.append(TeamIndividual([(39, 2), (15, 1), (31, 6)]))
    coach_teams.append(TeamIndividual([(30, 15), (24, 16), (1, 15)]))
    coach_teams.append(TeamIndividual([(0, 16), (31, 16), (1, 15)]))
    coach_teams.append(TeamIndividual([(21, 1), (30, 2), (3, 1)]))
    coach_teams.append(TeamIndividual([(21, 1), (30, 2), (31, 14)]))
    coach_teams.append(TeamIndividual([(21, 1), (30, 0), (1, 1)]))
    coach_teams.append(TeamIndividual([(17, 5), (30, 2), (1, 1)]))
    coach_teams.append(TeamIndividual([(30, 8), (15, 1), (28, 8)]))
    coach_teams.append(TeamIndividual([(32, 14), (15, 1), (37, 9)]))
    coach_teams.append(TeamIndividual([(32, 14), (15, 1), (23, 3)]))
    coach_teams.append(TeamIndividual([(22, 6), (15, 1), (23, 3)]))
    coach_teams.append(TeamIndividual([(22, 6), (15, 1), (36, 2)]))
    coach_teams.append(TeamIndividual([(22, 8), (15, 1), (36, 2)]))
    coach_teams.append(TeamIndividual([(30, 8), (15, 1), (23, 3)]))
    coach_teams.append(TeamIndividual([(15, 1), (32, 14), (22, 2)]))
    coach_teams.append(TeamIndividual([(7, 3), (30, 8), (15, 10)]))
    coach_teams.append(TeamIndividual([(15, 10), (7, 6), (30, 8)]))
    coach_teams.append(TeamIndividual([(6, 3), (30, 8), (15, 10)]))
    coach_teams.append(TeamIndividual([(6, 2), (39, 2), (15, 1)]))
    coach_teams.append(TeamIndividual([(15, 10), (6, 2), (30, 8)]))
    coach_teams.append(TeamIndividual([(31, 6), (30, 8), (15, 8)]))
    coach_teams.append(TeamIndividual([(7, 3), (15, 8), (30, 8)]))
    coach_teams.append(TeamIndividual([(31, 6), (39, 2), (15, 1)]))
    coach_teams.append(TeamIndividual([(31, 6), (39, 2), (14, 17)]))
    coach_teams.append(TeamIndividual([(31, 6), (14, 17), (39, 2)]))
    coach_teams.append(TeamIndividual([(14, 8), (31, 6), (39, 10)]))
    coach_teams.append(TeamIndividual([(14, 17), (31, 6), (39, 14)]))
    coach_teams.append(TeamIndividual([(14, 8), (39, 2), (31, 6)]))
    coach_teams.append(TeamIndividual([(31, 6), (7, 6), (14, 17)]))
    coach_teams.append(TeamIndividual([(6, 6), (14, 17), (31, 6)]))
    coach_teams.append(TeamIndividual([(30, 8), (14, 17), (31, 6)]))
    
    
    # 新测试
    ga = TeamGeneticAlgorithm(client=client,
                              initial_coach_teams=coach_teams,
                              population_size=10,
                              generations=30)
    
    
    
    # 创建遗传算法实例
    #ga = TeamGeneticAlgorithm(
    #    client=client,
    #    population_size=10,  # 减小种群大小以加快测试
    #    generations=15,      # 减少代数以加快测试
    #    mutation_rate=0.2,
    #    crossover_rate=0.8,
    #    elite_rate=0.2,
    #    initial_coach_teams=coach_teams
    #)
    
    final_population, fitness_history = ga.evolve()

    
    # 输出最后一轮的种群
    print(f"最后一轮的种群:")
    sorted_population = sorted(final_population, key=lambda x: x.fitness, reverse=True)
    for i, team in enumerate(sorted_population):
        print(f"  个体{i+1}: {team.team_config} (适应度: {team.fitness:.3f})")

    plot_fitness_evolution(fitness_history)

    calculate_win_rate_matrix(final_population, ga.coach_teams, client)


if __name__ == "__main__":
    # test_fitness()
    # test_coach_teams()
    # test_exchange_team()
    # test_restraint()
    main()
