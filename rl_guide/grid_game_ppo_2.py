"""
基于 Gymnasium 和 Stable-Baselines3 的 PPO 简化示例
在固定网格中寻路，使用抽离的游戏逻辑
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from typing import Tuple, Optional, Dict, Any
import time
from grid_game import GridGame


class GridWorldEnv(gym.Env):
    """"""
    
    def __init__(self):
        super().__init__()
        # 使用抽离的游戏逻辑
        self.game = GridGame(is_render=False) 
        
        # 动作空间：上下左右
        self.action_space = spaces.Discrete(4)
        
        # 观测空间：整个网格
        # 0: 空地
        # 1: 墙
        # 2: 智能体
        # 3: 目标
        self.observation_space = spaces.Box(
            low=0, high=3, shape=(20, 20), dtype=np.int32
        )
        
        self.last_distance = 0
        
    def get_observation(self) -> np.ndarray:
        """获取观测状态"""
        
        # 复制地图
        obs = self.game.map.copy().astype(np.int32)
        
        # 标记智能体位置 (2)
        obs[self.game.hero_pos] = 2
        
        # 标记目标位置 (3)
        obs[self.game.target_pos] = 3
        
        return obs
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)
        # 重置游戏状态
        self.game.reset()
        self.last_distance = 34

        return self.get_observation(), {}
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        # 使用游戏逻辑执行动作
        win, hit_wall, time_up = self.game.action(action)
        
        # 胜利奖励
        win_reward = 0
        if win:
            win_reward = 1
            
        # 撞墙惩罚
        hit_wall_reward = 0
        if hit_wall:
            hit_wall_reward = -1
        
        #失败惩罚
        fail_reward = 0
        if time_up:
            fail_reward = -1
            
        # 时间奖励
        step_reward = -1

        # 距离奖励
        distance = abs(self.game.target_pos[0] - self.game.hero_pos[0]) + abs(self.game.target_pos[1] - self.game.hero_pos[1])
        distance_reward = self.last_distance - distance  # -1 0 1三个取值
        self.last_distance = distance
        # 总奖励
        reward = 10*win_reward + distance_reward + 0.05*step_reward + 0.5*hit_wall_reward + 5*fail_reward

        
        # 确定终止状态
        terminated = win
        truncated = time_up
        
        return self.get_observation(), reward, terminated, truncated, {}


def train():
    # 创建单个环境
    env = GridWorldEnv()
    # 创建PPO模型
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        verbose=1
    )
    # 训练
    model.learn(total_timesteps=500000)
    
    # 保存模型
    model.save("models/ppo_grid_model_2")
    
    env.close()


def evaluate(n_episodes: int = 5):
    """评估训练好的模型"""
    env = GridWorldEnv()
    model = PPO.load("models/ppo_grid_model_2")
    
    success_count = 0

    
    for episode in range(n_episodes):
        obs, info = env.reset()

        while True:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            
            
            if terminated:
                success_count += 1
                break
            elif truncated:
                break
        
    env.close()
    print(f"成功率: {success_count}/{n_episodes}")



if __name__ == "__main__":
    train()
    evaluate()
