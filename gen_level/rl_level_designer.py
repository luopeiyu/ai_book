"""
基于PPO的三消游戏关卡设计强化学习系统
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from typing import Dict, List, Tuple, Any, Optional
import random
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from dataclasses import dataclass

from match3_env import LevelDesignEnv
from level_generator import LevelGenerator, DifficultyLevel, LevelType, LevelConfig
from match3_game import Match3Game


@dataclass
class TrainingMetrics:
    """训练指标"""
    episode: int
    mean_reward: float
    mean_level_quality: float
    best_level_quality: float
    training_time: float
    levels_designed: int


class LevelQualityCallback(BaseCallback):
    """关卡质量监控回调"""
    
    def __init__(self, log_dir: str, eval_freq: int = 1000, verbose: int = 1):
        super().__init__(verbose)
        self.log_dir = log_dir
        self.eval_freq = eval_freq
        self.episode_rewards = []
        self.episode_qualities = []
        self.best_levels = []
        self.metrics_history = []
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
    
    def _on_step(self) -> bool:
        # 收集每一步的信息
        if len(self.locals.get('infos', [])) > 0:
            for info in self.locals['infos']:
                if 'level_quality' in info:
                    self.episode_qualities.append(info['level_quality'])
        
        return True
    
    def _on_rollout_end(self) -> None:
        # 每次推演结束时记录指标
        if len(self.episode_qualities) > 0:
            mean_quality = np.mean(self.episode_qualities[-100:])  # 最近100个的平均质量
            
            if self.verbose > 0 and self.num_timesteps % self.eval_freq == 0:
                print(f"步数: {self.num_timesteps}, 平均关卡质量: {mean_quality:.3f}")
        
        # 定期评估并保存最佳关卡
        if self.num_timesteps % self.eval_freq == 0:
            self._evaluate_and_save()
    
    def _evaluate_and_save(self):
        """评估当前模型并保存最佳关卡"""
        # 创建评估环境
        eval_env = LevelDesignEnv()
        
        best_levels = []
        total_quality = 0.0
        num_evaluations = 10
        
        for _ in range(num_evaluations):
            obs, _ = eval_env.reset()
            done = False
            episode_reward = 0.0
            
            while not done:
                # 使用训练好的模型预测动作
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = eval_env.step(action)
                done = terminated or truncated
                episode_reward += reward
            
            # 记录关卡质量
            level_quality = info.get('level_quality', 0.0)
            total_quality += level_quality
            
            # 如果质量足够好，保存关卡
            if level_quality > 0.7:
                level_data = eval_env.get_current_level()
                best_levels.append(level_data)
        
        avg_quality = total_quality / num_evaluations
        
        # 保存指标
        metrics = TrainingMetrics(
            episode=self.num_timesteps,
            mean_reward=np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0.0,
            mean_level_quality=avg_quality,
            best_level_quality=max([l.get('quality_score', 0) for l in best_levels], default=0),
            training_time=datetime.now().timestamp(),
            levels_designed=len(best_levels)
        )
        
        self.metrics_history.append(metrics)
        
        # 保存最佳关卡
        if best_levels:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            levels_file = os.path.join(self.log_dir, f"best_levels_{timestamp}.json")
            
            with open(levels_file, 'w', encoding='utf-8') as f:
                json.dump(best_levels, f, indent=2, ensure_ascii=False)
            
            if self.verbose > 0:
                print(f"保存了 {len(best_levels)} 个高质量关卡到 {levels_file}")
        
        # 保存训练指标
        metrics_file = os.path.join(self.log_dir, "training_metrics.json")
        with open(metrics_file, 'w', encoding='utf-8') as f:
            metrics_data = [
                {
                    'episode': m.episode,
                    'mean_reward': m.mean_reward,
                    'mean_level_quality': m.mean_level_quality,
                    'best_level_quality': m.best_level_quality,
                    'levels_designed': m.levels_designed
                }
                for m in self.metrics_history
            ]
            json.dump(metrics_data, f, indent=2)


class CustomCNN(BaseFeaturesExtractor):
    """自定义CNN特征提取器，用于处理棋盘状态"""
    
    def __init__(self, observation_space: gym.Space, features_dim: int = 256):
        # 只处理棋盘部分
        board_space = observation_space['board']
        super().__init__(observation_space, features_dim)
        
        n_input_channels = 1  # 棋盘只有一个通道
        
        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
        )
        
        # 计算CNN输出维度
        with torch.no_grad():
            sample_board = torch.zeros(1, n_input_channels, board_space.shape[0], board_space.shape[1])
            cnn_output_dim = self.cnn(sample_board).shape[1]
        
        # 额外特征的维度
        extra_features_dim = 3  # target_score, moves_limit, design_progress
        
        # 全连接层
        self.linear = nn.Sequential(
            nn.Linear(cnn_output_dim + extra_features_dim, 512),
            nn.ReLU(),
            nn.Linear(512, features_dim),
            nn.ReLU(),
        )
    
    def forward(self, observations: Dict[str, torch.Tensor]) -> torch.Tensor:
        # 处理棋盘
        board = observations['board'].float()
        
        # 如果是3D张量（batch_size, height, width），添加通道维度
        if len(board.shape) == 3:
            board = board.unsqueeze(1)
        
        cnn_features = self.cnn(board)
        
        # 处理额外特征
        extra_features = torch.cat([
            observations['target_score'].float(),
            observations['moves_limit'].float(),
            observations['design_progress'].float()
        ], dim=1)
        
        # 合并所有特征
        combined_features = torch.cat([cnn_features, extra_features], dim=1)
        
        return self.linear(combined_features)


class CustomActorCriticPolicy(ActorCriticPolicy):
    """自定义Actor-Critic策略"""
    
    def __init__(self, *args, **kwargs):
        kwargs['features_extractor_class'] = CustomCNN
        kwargs['features_extractor_kwargs'] = {'features_dim': 256}
        super().__init__(*args, **kwargs)


class RLLevelDesigner:
    """强化学习关卡设计器"""
    
    def __init__(self, 
                 board_width: int = 8, 
                 board_height: int = 8, 
                 gem_types: int = 6,
                 log_dir: str = "logs/rl_level_designer"):
        
        self.board_width = board_width
        self.board_height = board_height
        self.gem_types = gem_types
        self.log_dir = log_dir
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 模型和环境
        self.model = None
        self.env = None
        
        # 训练历史
        self.training_history = []
        
    def create_environment(self, num_envs: int = 4) -> DummyVecEnv:
        """创建训练环境"""
        def make_env():
            return LevelDesignEnv(self.board_width, self.board_height, self.gem_types)
        
        if num_envs == 1:
            env = DummyVecEnv([make_env])
        else:
            env = SubprocVecEnv([make_env for _ in range(num_envs)])
        
        return env
    
    def create_model(self, 
                     learning_rate: float = 3e-4,
                     n_steps: int = 2048,
                     batch_size: int = 64,
                     n_epochs: int = 10,
                     gamma: float = 0.99,
                     gae_lambda: float = 0.95,
                     clip_range: float = 0.2,
                     ent_coef: float = 0.01,
                     vf_coef: float = 0.5,
                     max_grad_norm: float = 0.5) -> PPO:
        """创建PPO模型"""
        
        if self.env is None:
            self.env = self.create_environment()
        
        model = PPO(
            CustomActorCriticPolicy,
            self.env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            gae_lambda=gae_lambda,
            clip_range=clip_range,
            ent_coef=ent_coef,
            vf_coef=vf_coef,
            max_grad_norm=max_grad_norm,
            verbose=1,
            tensorboard_log=self.log_dir
        )
        
        return model
    
    def train(self, 
              total_timesteps: int = 100000,
              save_freq: int = 10000,
              eval_freq: int = 2000) -> PPO:
        """训练关卡设计智能体"""
        
        print(f"开始训练关卡设计智能体...")
        print(f"总训练步数: {total_timesteps}")
        print(f"日志目录: {self.log_dir}")
        
        # 创建环境和模型
        self.env = self.create_environment(num_envs=4)
        self.model = self.create_model()
        
        # 创建回调
        callback = LevelQualityCallback(
            log_dir=self.log_dir,
            eval_freq=eval_freq,
            verbose=1
        )
        
        # 开始训练
        start_time = datetime.now()
        
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=True
        )
        
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        print(f"训练完成！耗时: {training_time:.2f}秒")
        
        # 保存最终模型
        model_path = os.path.join(self.log_dir, "final_model.zip")
        self.model.save(model_path)
        print(f"模型已保存到: {model_path}")
        
        return self.model
    
    def load_model(self, model_path: str) -> PPO:
        """加载预训练模型"""
        if self.env is None:
            self.env = self.create_environment(num_envs=1)
        
        self.model = PPO.load(model_path, env=self.env)
        print(f"模型已从 {model_path} 加载")
        return self.model
    
    def generate_levels(self, 
                       num_levels: int = 10,
                       quality_threshold: float = 0.6,
                       max_attempts: int = 100) -> List[Dict[str, Any]]:
        """使用训练好的模型生成关卡"""
        
        if self.model is None:
            raise ValueError("模型未加载，请先训练或加载模型")
        
        generated_levels = []
        attempts = 0
        
        # 创建单个环境用于生成
        eval_env = LevelDesignEnv(self.board_width, self.board_height, self.gem_types)
        
        print(f"开始生成 {num_levels} 个关卡...")
        
        while len(generated_levels) < num_levels and attempts < max_attempts:
            obs, _ = eval_env.reset()
            done = False
            
            while not done:
                action, _ = self.model.predict(obs, deterministic=False)
                obs, reward, terminated, truncated, info = eval_env.step(action)
                done = terminated or truncated
            
            # 检查关卡质量
            level_quality = info.get('level_quality', 0.0)
            
            if level_quality >= quality_threshold:
                level_data = eval_env.get_current_level()
                level_data['generation_attempt'] = attempts + 1
                generated_levels.append(level_data)
                
                print(f"生成关卡 {len(generated_levels)}/{num_levels}, 质量: {level_quality:.3f}")
            
            attempts += 1
        
        if len(generated_levels) < num_levels:
            print(f"警告: 只生成了 {len(generated_levels)} 个关卡 (目标: {num_levels})")
        
        return generated_levels
    
    def evaluate_model(self, num_episodes: int = 50) -> Dict[str, float]:
        """评估模型性能"""
        
        if self.model is None:
            raise ValueError("模型未加载，请先训练或加载模型")
        
        eval_env = LevelDesignEnv(self.board_width, self.board_height, self.gem_types)
        
        episode_rewards = []
        episode_qualities = []
        completion_rates = []
        
        print(f"开始评估模型 ({num_episodes} 轮)...")
        
        for episode in range(num_episodes):
            obs, _ = eval_env.reset()
            done = False
            episode_reward = 0.0
            steps = 0
            
            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = eval_env.step(action)
                episode_reward += reward
                done = terminated or truncated
                steps += 1
            
            episode_rewards.append(episode_reward)
            episode_qualities.append(info.get('level_quality', 0.0))
            completion_rates.append(1.0 if terminated else 0.0)
            
            if (episode + 1) % 10 == 0:
                print(f"评估进度: {episode + 1}/{num_episodes}")
        
        # 计算统计指标
        evaluation_results = {
            'mean_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'mean_quality': np.mean(episode_qualities),
            'std_quality': np.std(episode_qualities),
            'completion_rate': np.mean(completion_rates),
            'high_quality_rate': np.mean([q > 0.7 for q in episode_qualities])
        }
        
        print("\n=== 评估结果 ===")
        for key, value in evaluation_results.items():
            print(f"{key}: {value:.3f}")
        
        return evaluation_results
    
    def save_generated_levels(self, levels: List[Dict[str, Any]], filename: str):
        """保存生成的关卡"""
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(levels, f, indent=2, ensure_ascii=False)
        
        print(f"关卡已保存到: {filepath}")
    
    def visualize_training_progress(self):
        """可视化训练进度"""
        metrics_file = os.path.join(self.log_dir, "training_metrics.json")
        
        if not os.path.exists(metrics_file):
            print("训练指标文件不存在")
            return
        
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
        
        if not metrics:
            print("没有训练指标数据")
            return
        
        episodes = [m['episode'] for m in metrics]
        mean_rewards = [m['mean_reward'] for m in metrics]
        mean_qualities = [m['mean_level_quality'] for m in metrics]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 奖励曲线
        ax1.plot(episodes, mean_rewards, 'b-', label='平均奖励')
        ax1.set_xlabel('训练步数')
        ax1.set_ylabel('平均奖励')
        ax1.set_title('训练奖励曲线')
        ax1.legend()
        ax1.grid(True)
        
        # 关卡质量曲线
        ax2.plot(episodes, mean_qualities, 'r-', label='平均关卡质量')
        ax2.set_xlabel('训练步数')
        ax2.set_ylabel('关卡质量')
        ax2.set_title('关卡质量提升曲线')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(self.log_dir, "training_progress.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"训练进度图表已保存到: {chart_path}")
        
        plt.show()


if __name__ == "__main__":
    # 测试强化学习关卡设计器
    designer = RLLevelDesigner()
    
    print("=== 强化学习关卡设计器测试 ===")
    
    # 训练模型
    model = designer.train(total_timesteps=50000)
    
    # 评估模型
    evaluation = designer.evaluate_model(num_episodes=20)
    
    # 生成关卡
    levels = designer.generate_levels(num_levels=5, quality_threshold=0.5)
    
    # 保存生成的关卡
    if levels:
        designer.save_generated_levels(levels, "generated_levels.json")
        
        # 显示生成的关卡信息
        print(f"\n=== 生成的 {len(levels)} 个关卡 ===")
        for i, level in enumerate(levels):
            print(f"关卡 {i+1}:")
            print(f"  目标分数: {level['target_score']}")
            print(f"  移动限制: {level['moves_limit']}")
            print(f"  质量评分: {level['quality_score']:.3f}")
    
    # 可视化训练进度
    designer.visualize_training_progress()
