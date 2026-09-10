"""
基于 Gymnasium 和 Stable-Baselines3 的 PPO 简化示例
在固定网格中寻路，使用抽离的游戏逻辑
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from typing import Tuple, Optional, Dict, Any
from grid_game import GridGame


class GridWorldEnv(gym.Env):
    
    def __init__(self):
        super().__init__()
        # 使用抽离的游戏逻辑
        self.game = GridGame(is_render=False) 
        
        # 动作空间：上下左右
        self.action_space = spaces.Discrete(4)
        
        # 观测空间：整个网格
        # 0: 空地, 1: 墙, 2: 智能体, 3: 目标
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
        self.last_distance = 38

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
        
        # 失败惩罚
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
        
        # 在info中添加详细信息用于监控
        info = {
            'win': win,
            'time_up': time_up,
        }
        
        return self.get_observation(), reward, terminated, truncated, info


class CustomMLP(BaseFeaturesExtractor):
    """自定义MLP特征提取器"""
    
    def __init__(self, observation_space: gym.Space, features_dim: int = 256):
        super().__init__(observation_space, features_dim)
        
        self.network = nn.Sequential(
            nn.Flatten(),
            
            # 第一层：400 -> 512
            nn.Linear(400, 512),
            nn.ReLU(),
            
            # 第二层：512 -> 256
            nn.Linear(512, 256),
            nn.ReLU(),
            
            # 第三层：256 -> 128
            nn.Linear(256, 128),
            nn.ReLU(),
            
            # 输出层：128 -> features_dim
            nn.Linear(128, features_dim),
            nn.ReLU()
        )
    
    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        # 数据类型转换
        observations = observations.float()
        return self.network(observations)


class TrainCallback(BaseCallback):
    """网格训练监控回调"""
    
    def __init__(self, verbose: int = 1):
        super().__init__(verbose)
        
        # 统计变量
        self.episode_count = 0
        self.win_count = 0
        
    def _on_step(self) -> bool:
        """每步调用一次"""
        
        # 检查是否有回合结束
        dones = self.locals['dones']  # 长度为4数组，terminated OR truncated
        for i, done in enumerate(dones): 
            if done:
                self.episode_count += 1
                info = self.locals['infos'][i]
                if info['win'] == True:
                    self.win_count += 1
        
        # 定期记录统计信息
        if self.episode_count > 100:
            win_rate = self.win_count / self.episode_count
            # 记录到TensorBoard
            self.logger.record('custom/win_rate', win_rate) 
            self.episode_count = 0
            self.win_count = 0
        return True
    

        


def create_env():
    """创建环境的工厂函数"""
    def _init():
        env = GridWorldEnv()
        return env
    return _init


def train():

    n_envs = 4
    env = make_vec_env(
        create_env(),
        n_envs=n_envs,
        vec_env_cls=DummyVecEnv,
        seed=42
    )
    
    # 自定义MLP策略配置
    policy_kwargs = dict(
        features_extractor_class=CustomMLP,
        features_extractor_kwargs=dict(features_dim=256),
        net_arch=dict(pi=[128, 64], vf=[128, 64]),  # 策略和价值网络架构
        activation_fn=nn.ReLU,
    )
    
    # 创建PPO模型
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=1e-4,  
        n_steps=1024,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        policy_kwargs=policy_kwargs,
        verbose=1,
        tensorboard_log="./logs/",  
    )
    
    # 创建回调
    callback = TrainCallback(verbose=1)
    
    model.learn(
        total_timesteps=500000,
        tb_log_name="ppo_grid_model_5",
        callback=callback
    )
    
    model.save("models/ppo_grid_model_5")
    env.close()
    
    return model


def evaluate(n_episodes: int = 5):
    """评估训练好的模型"""
    env = GridWorldEnv()
    model = PPO.load("models/ppo_grid_model_5")
    
    success_count = 0

    # 使用训练好的模型进行评估  
    for episode in range(n_episodes):
        obs, _ = env.reset()
        print("开始新的一局")
        while True:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            
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
