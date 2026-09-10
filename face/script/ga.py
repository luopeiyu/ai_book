
import random
import numpy as np
import json
from typing import List, Dict, Tuple
import time
from normalize_facial_keypoints import FacialKeypointNormalizer
import matplotlib.pyplot as plt
from simulator import Simulator


class GeneticAlgorithm:
    def __init__(self, simulator: Simulator, 
                 population_size=50, generations=100, 
                 mutation_rate=0.1, crossover_rate=0.8, elite_rate=0.1):
        """
        遗传算法初始化
        
        Args:
            simulator: 模拟器实例
            population_size: 种群大小
            generations: 迭代代数
            mutation_rate: 变异率
            crossover_rate: 交叉率
            elite_rate: 精英保留率
        """
        self.simulator = simulator
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_rate = elite_rate
        self.elite_size = int(population_size * elite_rate)
        
        # 参数范围定义
        self.param_ranges = {
            'headWidth': (-100, 100),
            'headHeight': (-100, 100),
            'noseWidth': (-100, 100),
            'noseLength': (-100, 100),
            'eyeLength': (-100, 100),
            'eyeWidth': (-100, 100),
            'mouthSize': (-100, 100),
        }
        
        self.param_names = list(self.param_ranges.keys())
        
    def create_individual(self) -> List[int]:
        """创建一个个体（随机参数组合）"""
        individual = []
        for param_name in self.param_names:
            min_val, max_val = self.param_ranges[param_name]
            individual.append(random.randint(min_val, max_val))
        return individual
    
    def create_population(self) -> List[List[int]]:
        """创建初始种群"""
        return [self.create_individual() for _ in range(self.population_size)]
    
    def individual_to_params(self, individual: List[int]) -> Dict[str, int]:
        """将个体转换为参数字典"""
        return {param_name: individual[i] for i, param_name in enumerate(self.param_names)}
    
    def calculate_fitness(self, individual: List[int], target_landmarks: List[Dict[str, int]]) -> float:
        """计算适应度（关键点距离的倒数）"""
        params = self.individual_to_params(individual)
        current_landmarks = self.simulator.get_landmarks(params)
        
        if current_landmarks is None:
            return -float('inf')  # 请求失败，适应度为负无穷
        
        # 列表推导式和numpy数组构造
        keypoints = np.array([[landmark['x'], landmark['y']] for landmark in current_landmarks])
        # 归一化关键点
        normalizer = FacialKeypointNormalizer()
        keypoints = normalizer.normalize_keypoints(keypoints)
        
        # 计算所有点之间的欧几里得距离
        distances = np.linalg.norm(keypoints - target_landmarks, axis=1)
        total_distance = np.sum(distances)
        
        # 计算所有点之间的欧几里得距离，其中序号为3 4 5 6的点赋予高权重
        distances = np.linalg.norm(keypoints - target_landmarks, axis=1)
        total_distance = np.sum(distances)
        total_distance = total_distance + np.sum(distances[3:6]) * 10
        

        return -total_distance
    
    def selection(self, population: List[List[int]], fitness_scores: List[float]) -> List[int]:
        """轮盘赌选择"""
        # 将适应度转换为正值用于轮盘赌选择
        min_fitness = min(fitness_scores)
        adjusted_fitness = [f - min_fitness + 1 for f in fitness_scores]
        
        adjusted_fitness = fitness_scores
        total_fitness = sum(adjusted_fitness)
        
        if total_fitness == 0:
            return random.choice(population)
        
        pick = random.uniform(0, total_fitness)
        current = 0
        for i, fitness in enumerate(adjusted_fitness):
            current += fitness
            if current >= pick:
                return population[i]
        return population[-1]
    
    def tournament_selection(self, population: List[List[int]], fitness_scores: List[float], tournament_size=3) -> List[int]:
        """锦标赛选择"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
        return population[winner_index]
    
    def single_point_crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """单点交叉"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    
    def uniform_crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """均匀交叉（随机交叉）"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1, child2 = [], []
        for i in range(len(parent1)):
            if random.random() < 0.5:
                child1.append(parent1[i])
                child2.append(parent2[i])
            else:
                child1.append(parent2[i])
                child2.append(parent1[i])
        return child1, child2
    
    def arithmetic_crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """算术交叉"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        alpha = random.random()
        child1 = [int(alpha * p1 + (1 - alpha) * p2) for p1, p2 in zip(parent1, parent2)]
        child2 = [int((1 - alpha) * p1 + alpha * p2) for p1, p2 in zip(parent1, parent2)]
        
        # 确保参数在有效范围内
        for i, param_name in enumerate(self.param_names):
            min_val, max_val = self.param_ranges[param_name]
            child1[i] = max(min_val, min(max_val, child1[i]))
            child2[i] = max(min_val, min(max_val, child2[i]))
        
        return child1, child2
    
    def crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """随机选择交叉方式"""
        crossover_methods = [
            self.single_point_crossover,
            self.uniform_crossover,
            self.arithmetic_crossover
        ]
        selected_method = random.choice(crossover_methods)
        return selected_method(parent1, parent2)
    
    def mutate(self, individual: List[int]) -> List[int]:
        """变异操作"""
        
        mutated = individual.copy()
        
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                param_name = self.param_names[i]
                min_val, max_val = self.param_ranges[param_name]
                
                # 随机选择变异方式
                mutation_type = random.choice(['gaussian', 'uniform', 'boundary'])
            
                if mutation_type == 'gaussian':
                    # 高斯变异
                    delta = int(random.gauss(0, 15))
                    new_value = mutated[i] + delta
                elif mutation_type == 'uniform':
                    # 均匀变异
                    delta = random.randint(-20, 20)
                    new_value = mutated[i] + delta
                else:  # boundary
                    # 边界变异
                    new_value = random.choice([min_val, max_val])
                
                mutated[i] = max(min_val, min(max_val, new_value))
        return mutated
    
    def get_elite(self, population: List[List[int]], fitness_scores: List[float]) -> List[List[int]]:
        """获取精英个体"""
        # 按适应度排序，获取最优的个体
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        elite_individuals = [population[i].copy() for i in sorted_indices[:self.elite_size]]
        return elite_individuals
    
    def evolve(self, target_landmarks: List[Dict[str, int]]) -> Dict[str, int]:
        """主要的进化过程"""
        print(f"开始遗传算法优化，目标关键点数量: {len(target_landmarks)}")
        print(f"种群大小: {self.population_size}, 迭代代数: {self.generations}")
        print(f"精英保留数量: {self.elite_size}")
        
        # 创建初始种群
        population = self.create_population()
        best_individual = None
        best_fitness_history = []
        best_fitness = -float('inf')
        
        
        for generation in range(self.generations):
            print(f"\n第 {generation + 1}/{self.generations} 代")
            
            # 计算适应度
            fitness_scores = []
            for i, individual in enumerate(population):
                fitness = self.calculate_fitness(individual, target_landmarks)
                fitness_scores.append(fitness)
                
                # 更新最佳个体
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
                    print(f"  发现更好的个体: 适应度 = {fitness:.6f}")
                    print(f"  参数: {self.individual_to_params(individual)}")
                
                # 添加延时避免请求过于频繁
                time.sleep(0.01)
            
            avg_fitness = np.mean(fitness_scores)
            print(f"  平均适应度: {avg_fitness:.6f}, 最佳适应度: {best_fitness:.6f}")
            best_fitness_history.append(best_fitness)
            
            # 精英保留
            elite_individuals = self.get_elite(population, fitness_scores)
            
            # 选择和繁殖生成新个体
            new_population = elite_individuals.copy()  # 保留精英
            
            # 生成剩余个体
            while len(new_population) < self.population_size:
                # 随机选择选择方式
                if random.random() < 0.7:
                    parent1 = self.tournament_selection(population, fitness_scores)
                    parent2 = self.tournament_selection(population, fitness_scores)
                else:
                    parent1 = self.selection(population, fitness_scores)
                    parent2 = self.selection(population, fitness_scores)
                
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            population = new_population[:self.population_size]  # 确保种群大小不变
        
        print(f"\n优化完成！")
        print(f"最佳适应度: {best_fitness:.6f}")
        print(f"最佳参数: {self.individual_to_params(best_individual)}")
        
        return self.individual_to_params(best_individual), best_fitness_history


def get_test_target_landmarks():
    target_landmarks = np.array([
        [158, 205],
        [172, 264],
        [256, 344],
        [167, 198],
        [193, 182],
        [215, 206],
        [177, 219],
        [256, 191],
        [256, 228],
        [234, 290],
        [256, 295]
    ])
    normalizer = FacialKeypointNormalizer()
    target_landmarks = normalizer.normalize_keypoints(target_landmarks)
    print(target_landmarks)
    from normalize_facial_keypoints import visualize_normalization
    visualize_normalization(target_landmarks)
    return target_landmarks

def get_test_target_landmarks2_from_image(image_path):
    from extract_facial_keypoints import FacialKeypointExtractor
    extractor = FacialKeypointExtractor()
    landmarks = extractor.extract_keypoints(image_path)
    normalizer = FacialKeypointNormalizer()
    landmarks = normalizer.normalize_keypoints(landmarks)
    
    from normalize_facial_keypoints import visualize_normalization
    visualize_normalization(landmarks)
    return landmarks

def get_test_target_landmarks_real():
    target_landmarks = np.array([
        [-0.53245253, 0.08003493],
        [-0.47677029, 0.33707445],
        [ 0.0, 0.6539352],
        [-0.5, 0.03567434],
        [-0.33989712, -0.03644505],
        [-0.24051317, 0.0919584],
        [-0.42439137, 0.16572107],
        [ 0.0, 0.0],
        [-0.01, 0.12546322],
        [-0.24381821, 0.38493448],
        [ 0.0, 0.48703121]
    ])
    
    
    
    
    from normalize_facial_keypoints import visualize_normalization
    visualize_normalization(target_landmarks)
    return target_landmarks





def main():
    """主函数示例"""
    # 目标关键点（示例数据）
    
    #target_landmarks = get_test_target_landmarks()
    target_landmarks = get_test_target_landmarks2_from_image("E:/B9/face/style_dataset/filtered_faces/test/realface (191).jpg")
    from calculate_real_keypoint_offset import transform_real_to_anime
    target_landmarks = transform_real_to_anime(target_landmarks)
    #target_landmarks = get_test_target_landmarks_real()

    # 创建遗传算法实例
    simulator = Simulator()
    ga = GeneticAlgorithm(
        simulator=simulator
    )
    
    # 运行优化
    best_params, best_fitness_history = ga.evolve(target_landmarks)
    
    # 绘制适应度变化曲线
    plt.figure(figsize=(10, 5))
    plt.plot(best_fitness_history, label='Best Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness Evolution')
    plt.legend()
    plt.show()
    
    # 验证结果
    ga.simulator.get_landmarks(best_params)

if __name__ == "__main__":
    main()
