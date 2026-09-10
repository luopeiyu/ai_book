"""
基于PPO的阵容选择强化学习系统
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from typing import Dict, List, Tuple, Any, Optional
import json
import random
from dataclasses import dataclass
from http_client import BattleSimulatorClient
from fitness import calculate_individual_fitness


# 常量定义
HERO_POOL = list(range(40))   # 0-39 共40个英雄
SKILL_POOL = list(range(18))  # 0-17 共18个技能
TEAM_SIZE = 3  # 每队3个英雄


class CoachManager:

    def __init__(self, initial_coaches: List[List[Tuple[int, int]]] = None, 
                 replace_count: int = 1,
                 max_coaches: int = 30, 
                 update_interval: int = 10000):
        
        if initial_coaches is None:   
            self.coaches = self.generate_random_coaches()
        else:
            self.coaches = initial_coaches.copy()
        self.replace_count = replace_count
        self.max_coaches = max_coaches

    def generate_random_coaches(self, count: int = 5) -> List[List[Tuple[int, int]]]:
        """生成默认教练队伍"""
        coach_teams = []
        for _ in range(count):
            heroes = random.sample(HERO_POOL, TEAM_SIZE)
            skills = [random.choice(SKILL_POOL) for _ in range(TEAM_SIZE)]
            team_config = list(zip(heroes, skills))
            coach_teams.append(team_config)
        return coach_teams

    
    def get_random_coach(self) -> List[Tuple[int, int]]:
        """随机获取一个教练队伍"""
        return random.choice(self.coaches)    
    

    def add_coaches(self, new_coaches):
        # 添加新教练  
        self.coaches.extend(new_coaches)
        
        # 如果超过最大数量，移除最旧的
        if len(self.coaches) > self.max_coaches:
            remove_count = len(self.coaches) - self.max_coaches
            self.coaches = self.coaches[remove_count:]
        print(f"更新教练队伍池，当前数量: {len(self.coaches)}")
        
        
class TeamSelectionEnv(gym.Env):
    """阵容选择环境"""
    
    def __init__(self, client: BattleSimulatorClient, coach_teams: List[List[Tuple[int, int]]] = None, hero_pool: List[int] = None):
        super(TeamSelectionEnv, self).__init__()
        
        self.client = client
        self.coach_manager = CoachManager(coach_teams)
        
        # 使用 one-hot 编码
        # 教练队伍编码: 3 * (40 + 18) = 174 (每个英雄用40维one-hot + 18维技能one-hot)
        # 当前队伍编码: 3 * (40 + 18) = 174
        # 可用英雄标记: 40
        # 步骤信息: 6 (6步one-hot)
        # 总计: 174 + 174 + 40 + 6 = 394
        self.observation_space = spaces.Box(
            low=0, high=1, 
            shape=(394,), 
            dtype=np.float32
        )
        
        # 动作空间：选择英雄ID或技能ID
        self.action_space = spaces.Discrete(len(HERO_POOL) + len(SKILL_POOL))
        
        # 状态变量
        self.current_coach_config = []
        self.current_team_config = []
        self.hero_pool = hero_pool
        self.available_heroes = set(self.hero_pool)
        self.current_phase = 0  # 当前阶段 0-5 (3个英雄 + 3个技能)
        self.selected_hero = None # 当前选择英雄
        self.step_count = 0     # 当前步数
        self.MAX_STEP = 100    # 最大步数
        

    
    def encode_team(self, team_config: List[Tuple[int, int]]) -> np.ndarray:
        """使用one-hot编码队伍配置"""
        # 每个队伍: 3 * (40 + 18) = 174维
        encoding = np.zeros(3 * (len(HERO_POOL) + len(SKILL_POOL)), dtype=np.float32)
        for i, (hero_id, skill_id) in enumerate(team_config):
            if i < TEAM_SIZE:  # 最多3个英雄
                # 英雄one-hot编码
                hero_start = i * (len(HERO_POOL) + len(SKILL_POOL))
                encoding[hero_start + hero_id] = 1.0
                
                # 技能one-hot编码
                skill_start = hero_start + len(HERO_POOL)
                encoding[skill_start + skill_id] = 1.0
        
        return encoding
    

    def get_observation(self) -> np.ndarray:
        """获取当前状态观测 - one-hot版本"""
        obs = np.zeros(394, dtype=np.float32)
        
        # 教练队伍编码 (174维)
        coach_encoding = self.encode_team(self.current_coach_config)
        obs[:174] = coach_encoding
        
        # 当前队伍编码 (174维)
        current_team_encoding = self.encode_team(self.current_team_config)
        obs[174:348] = current_team_encoding
        
        # 可用英雄标记 (40维)
        available_heroes_mask = np.zeros(40, dtype=np.float32)
        for hero_id in self.available_heroes:
            available_heroes_mask[hero_id] = 1.0
        obs[348:388] = available_heroes_mask
        
        # 步骤信息 (8维)
        # 当前步骤one-hot编码 (6维：步骤0-5)
        if 0 <= self.current_phase < 6:
            obs[388 + self.current_phase] = 1.0
        
        return obs
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """重置环境"""
        super().reset(seed=seed)
        
        # 随机选择一个教练队伍
        self.current_coach_config = self.coach_manager.get_random_coach()
        self.current_team_config = []
        self.available_heroes = set(self.hero_pool)
        self.current_phase = 0
        self.step_count = 0
        self.selected_hero = None
        
        obs = self.get_observation()
        info = {}
        return obs, info
    
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """执行一步动作"""
        reward = 0.0
        terminated = False  # 任务完成
        truncated = False   # 超时截断
        info = {}
        
        action = int(action)
        # 当前阶段 0-5 (3个英雄 + 3个技能)
        if self.current_phase in [0,2,4]:
            # 选择英雄
            hero_id = int(action)
            if hero_id not in self.available_heroes:
                reward = -0.5  # 选择不可用英雄的惩罚
            else:
                self.selected_hero = hero_id
                self.available_heroes.remove(hero_id)
                reward = 0.1  # 成功选择英雄的小奖励
                self.current_phase += 1
        elif self.current_phase in [1,3,5]:
            # 选择技能
            skill_id = int(action) - len(HERO_POOL)
            if skill_id < 0 or skill_id >= len(SKILL_POOL):
                reward = -0.5  # 选择不可用技能的惩罚
            else:
                team_config = (self.selected_hero, skill_id)
                self.current_team_config.append(team_config)
                reward = 0.1  # 成功选择技能的小奖励
                self.current_phase += 1
                self.selected_hero = None
        # 计算步数
        self.step_count += 1
        if self.step_count >= self.MAX_STEP:
            truncated = True
            if len(self.current_team_config) < TEAM_SIZE:
                reward -= 1.0  # 未完成队伍的惩罚
                
        # 完成队伍
        if self.current_phase == 6:
            terminated = True
            final_reward = self.calculate_final_reward()
            reward += final_reward
        # 返回观测、奖励、terminated、truncated和信息
        return self.get_observation(), reward, terminated, truncated, info
    
    def calculate_final_reward(self) -> float:
        if self.client is None:
            return 0.0
        
        # 与教练队伍战斗
        battle_results = self.client.simulate_single_battle_bidirection(
            self.current_team_config, 
            self.current_coach_config
        )
        
        fitness = calculate_individual_fitness(battle_results)
        return fitness

    def update_coaches(self, new_coaches):
        self.coach_manager.add_coaches(new_coaches)
        
    def get_coach_teams(self):
        return self.coach_manager.coaches

# 动态更新教练队伍回调
class DynamicCoachCallback(BaseCallback):
    def __init__(self):
        super().__init__()
        self.step_count = 0
        self.interval = 10000
    
    def collect_strong_teams_from_model(self, model, coach_teams, count: int = 10) -> List[List[Tuple[int, int]]]:
        predictor = TeamSelectionPredictor(None)
        predictor.model = model
        coach_teams = random.choice(coach_teams)
        """从当前模型收集强队伍作为新教练"""
        print(f"从模型收集 {count} 支强队伍...")
        
        predict_teams = []
        attempts = 0
        max_attempts = count * 5  # 多尝试几次
        
        while len(predict_teams) < count and attempts < max_attempts:
            attempts += 1
            isok, predicted_team = predictor.predict(coach_teams)
            if not isok:
                continue
            
            predict_teams.append(predicted_team)
            
        print(f"成功收集 {len(predict_teams)} 支队伍")
        return predict_teams

    
    def _on_step(self) -> bool:
        # 定期更新教练队伍
        self.step_count += 1
        if self.step_count > 0 and self.step_count % self.interval == 0:
            
            # 收集强队伍作为新教练
            coach_teams = self.training_env.env_method('get_coach_teams')[0]
            new_coaches = self.collect_strong_teams_from_model(self.model, coach_teams, 5)
            
            self.training_env.env_method('update_coaches', new_coaches)
            
            # 记录coach的数量
            coach_teams = self.training_env.env_method('get_coach_teams')[0]
            coach_count = len(coach_teams)
            self.logger.record('custom/coach_count', coach_count)
        return True



class TeamSelectionTrainer:
    """阵容选择训练器"""
    
    def __init__(self, 
                 client: BattleSimulatorClient,
                 coach_teams: Optional[List[List[Tuple[int, int]]]] = None,
                 n_envs: int = 2):
        """
        初始化训练器
        
        Args:
            client: 战斗模拟器客户端
            coach_teams: 教练队伍列表
            n_envs: 并行环境数量
        """
        self.client = client
        self.coach_teams = coach_teams
        self.n_envs = n_envs
        
    def create_env(self):
        """创建环境实例"""
        def _init():
            local_client = BattleSimulatorClient()
            env = TeamSelectionEnv(local_client, self.coach_teams)
            return env
        return _init
    
    def train(self, 
              total_timesteps: int = 100000,
              learning_rate: float = 3e-4,
              save_path: str = "./output/ppo_team_selection_3"):
        """训练PPO模型"""
        print("创建训练环境...")
        
        # 创建向量化环境，确保包含 episode 统计
        env = make_vec_env(
            self.create_env(),
            n_envs=self.n_envs,
            vec_env_cls=SubprocVecEnv,
        )
        
        print("初始化PPO模型...")
        
        # 策略网络
        policy_kwargs = dict(
            net_arch=dict(pi=[256, 256], vf=[256, 256])
        )
        
        # 创建PPO模型
        model = PPO(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,  
            n_steps=512,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            policy_kwargs=policy_kwargs,
            verbose=1,
            tensorboard_log="./logs/",  
        )
        

        print(f"开始训练 {total_timesteps} 步...")
        
        # 开始训练
        
        callback = DynamicCoachCallback()
        callback.interval = 5000  # 调试
        
        model.learn(
            total_timesteps=total_timesteps,
            tb_log_name="ppo_team_selection_3",
            callback=callback
        )
        
        # 保存最终模型
        model.save(save_path)
        print(f"训练完成！模型已保存到: {save_path}")
        
        # 关闭环境
        env.close()
    

class TeamSelectionPredictor:
    """阵容选择预测器"""
    
    def __init__(self, model_path):
        if model_path is not None:
            self.model = PPO.load(model_path)
        else:
            self.model = None

    def predict(self, coach_team: List[Tuple[int, int]], hero_pool: List[int]) -> int:
        env = TeamSelectionEnv(None, [coach_team], hero_pool) # 创建临时环境
        while True:
            obs = env.get_observation()
            action, _ = self.model.predict(obs, deterministic=True)
            _, _, terminated, truncated, _ = env.step(action)
            
            if terminated :
                return True , env.current_team_config
            elif truncated:
                return False, None




def evaluate():
    # 测试
    coach_teams = [] # 通过更换教练跑出的最强队伍
    coach_teams.append([(30, 15), (21, 16), (1, 15)])
    coach_teams.append([(30, 15), (31, 16), (1, 15)])
    coach_teams.append([(30, 15), (24, 16), (1, 15)])
    coach_teams.append([(0, 16), (31, 16), (1, 15)])
    coach_teams.append([(9, 15), (19, 15), (1, 15)])
    coach_teams.append([(17, 15), (19, 15), (1, 15)])
    coach_teams.append([(19, 5), (12, 6), (32, 15)])
    coach_teams.append([(17, 15), (0, 7), (37, 15)])
    coach_teams.append([(31, 15), (15, 15), (36, 17)])
    coach_teams.append([(31, 17), (15, 15), (30, 17)])
    
    client = BattleSimulatorClient()
    predictor = TeamSelectionPredictor(model_path="./models/ppo_team_selection_2")
    
    success_count = 0
    total_count = len(coach_teams)
    win_count = 0
    hero_pool = [i for i in range(20)]
    for coach_team in coach_teams:
        isok, predicted_team = predictor.predict(coach_team, hero_pool)
        if not isok:
            continue
        
        success_count += 1
        battle_result = client.simulate_single_battle_bidirection(predicted_team, coach_team)
        
        if battle_result[0]['winner'] == 'team1_win':
            win_count += 0.5
        if battle_result[1]['winner'] == 'team1_win':
            win_count += 0.5
        
    print(f"成功率: {success_count}/{total_count}")
    print(f"胜率: {win_count}/{success_count}")



def train():
    """主函数"""
    print("初始化PPO阵容选择训练...")
    
    # 创建客户端
    client = BattleSimulatorClient()
    
    try:
        health = client.health_check()
        print(f"服务状态: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"无法连接到战斗模拟器API: {e}")
        return
    
    
    # 训练
    trainer = TeamSelectionTrainer(
        client=client,
        coach_teams = None,
        n_envs=4  # 减少并行环境数量以避免API压力
    )
    
    trainer.train(
        total_timesteps=100000,
        learning_rate=3e-4,
        save_path="./models/ppo_team_selection_3"
    )
    



if __name__ == "__main__":
    # train()
    evaluate()
