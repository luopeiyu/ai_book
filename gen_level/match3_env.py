"""
三消游戏关卡设计环境
用于强化学习训练关卡设计智能体
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, Any, List, Optional
import random
import copy

from match3_game import Match3Game, GemType


class LevelDesignEnv(gym.Env):
    """
    关卡设计环境
    智能体的任务是设计有趣且平衡的三消游戏关卡
    """
    
    def __init__(self, board_width: int = 8, board_height: int = 8, gem_types: int = 6):
        super().__init__()
        
        self.board_width = board_width
        self.board_height = board_height
        self.gem_types = gem_types
        self.total_cells = board_width * board_height
        
        # 关卡设计参数范围
        self.min_target_score = 500
        self.max_target_score = 3000
        self.min_moves = 15
        self.max_moves = 50
        
        # 动作空间：设计关卡的各种操作
        # 0-63: 修改棋盘位置的宝石类型 (8x8=64个位置)
        # 64: 增加目标分数
        # 65: 减少目标分数
        # 66: 增加移动次数
        # 67: 减少移动次数
        # 68: 重新随机生成棋盘
        # 69: 完成关卡设计
        self.action_space = spaces.Discrete(70)
        
        # 观测空间：当前关卡状态
        # - 棋盘状态 (8x8)
        # - 目标分数 (归一化)
        # - 移动次数限制 (归一化)
        # - 关卡质量指标
        obs_space = {
            'board': spaces.Box(low=0, high=gem_types, shape=(board_height, board_width), dtype=np.int32),
            'target_score': spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32),
            'moves_limit': spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32),
            'design_progress': spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
        }
        self.observation_space = spaces.Dict(obs_space)
        
        # 当前关卡状态
        self.current_board = None
        self.current_target_score = 1000
        self.current_moves_limit = 30
        self.design_steps = 0
        self.max_design_steps = 50
        
        # 关卡质量评估缓存
        self.quality_cache = {}
        
        self.reset()
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """重置环境，开始设计新关卡"""
        super().reset(seed=seed)
        
        # 生成初始关卡
        self.current_board = self._generate_random_board()
        self.current_target_score = random.randint(self.min_target_score, self.max_target_score)
        self.current_moves_limit = random.randint(self.min_moves, self.max_moves)
        self.design_steps = 0
        
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, info
    
    def step(self, action: int) -> Tuple[Dict, float, bool, bool, Dict]:
        """执行动作，修改关卡设计"""
        self.design_steps += 1
        
        reward = 0.0
        terminated = False
        truncated = False
        
        # 执行动作
        if action < self.total_cells:
            # 修改棋盘位置
            row = action // self.board_width
            col = action % self.board_width
            old_gem = self.current_board[row, col]
            new_gem = random.randint(1, self.gem_types)
            if new_gem != old_gem:
                self.current_board[row, col] = new_gem
                reward += 0.1  # 小的正向奖励鼓励探索
        
        elif action == 64:  # 增加目标分数
            if self.current_target_score < self.max_target_score:
                self.current_target_score += 100
                reward += 0.05
        
        elif action == 65:  # 减少目标分数
            if self.current_target_score > self.min_target_score:
                self.current_target_score -= 100
                reward += 0.05
        
        elif action == 66:  # 增加移动次数
            if self.current_moves_limit < self.max_moves:
                self.current_moves_limit += 1
                reward += 0.05
        
        elif action == 67:  # 减少移动次数
            if self.current_moves_limit > self.min_moves:
                self.current_moves_limit -= 1
                reward += 0.05
        
        elif action == 68:  # 重新随机生成棋盘
            self.current_board = self._generate_random_board()
            reward += 0.2
        
        elif action == 69:  # 完成关卡设计
            terminated = True
            # 评估最终关卡质量
            quality_score = self._evaluate_level_quality()
            reward += quality_score * 10  # 主要奖励来源
        
        # 检查是否超时
        if self.design_steps >= self.max_design_steps:
            truncated = True
            # 如果超时，也评估当前关卡质量
            quality_score = self._evaluate_level_quality()
            reward += quality_score * 5  # 减半的奖励
        
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, reward, terminated, truncated, info
    
    def _generate_random_board(self) -> np.ndarray:
        """生成随机但合理的初始棋盘"""
        # 使用游戏类生成无初始匹配的棋盘
        temp_game = Match3Game(self.board_width, self.board_height, self.gem_types)
        return temp_game._generate_initial_board()
    
    def _get_observation(self) -> Dict:
        """获取当前观测"""
        return {
            'board': self.current_board.copy(),
            'target_score': np.array([(self.current_target_score - self.min_target_score) / 
                                    (self.max_target_score - self.min_target_score)], dtype=np.float32),
            'moves_limit': np.array([(self.current_moves_limit - self.min_moves) / 
                                   (self.max_moves - self.min_moves)], dtype=np.float32),
            'design_progress': np.array([self.design_steps / self.max_design_steps], dtype=np.float32)
        }
    
    def _get_info(self) -> Dict:
        """获取额外信息"""
        quality = self._evaluate_level_quality()
        return {
            'level_quality': quality,
            'target_score': self.current_target_score,
            'moves_limit': self.current_moves_limit,
            'design_steps': self.design_steps
        }
    
    def _evaluate_level_quality(self) -> float:
        """
        评估关卡质量 (0-1)
        考虑因素：
        - 可玩性（是否有足够的有效移动）
        - 平衡性（难度是否合适）
        - 趣味性（是否有策略性）
        """
        # 使用缓存避免重复计算
        board_hash = hash(self.current_board.tobytes())
        config_hash = hash((self.current_target_score, self.current_moves_limit))
        cache_key = (board_hash, config_hash)
        
        if cache_key in self.quality_cache:
            return self.quality_cache[cache_key]
        
        # 创建游戏实例进行测试
        game = Match3Game(self.board_width, self.board_height, self.gem_types)
        game.board = self.current_board.copy()
        game.set_level_config(self.current_target_score, self.current_moves_limit)
        
        # 1. 可玩性检查
        playability_score = self._evaluate_playability(game)
        
        # 2. 平衡性检查
        balance_score = self._evaluate_balance(game)
        
        # 3. 趣味性检查
        fun_score = self._evaluate_fun_factor(game)
        
        # 综合评分
        total_score = (playability_score * 0.4 + balance_score * 0.4 + fun_score * 0.2)
        
        # 缓存结果
        self.quality_cache[cache_key] = total_score
        
        return total_score
    
    def _evaluate_playability(self, game: Match3Game) -> float:
        """评估可玩性：是否有足够的有效移动"""
        valid_moves = game.get_valid_moves()
        move_count = len(valid_moves)
        
        # 理想情况下应该有10-30个有效移动
        if move_count == 0:
            return 0.0
        elif move_count < 5:
            return 0.3
        elif move_count < 10:
            return 0.6
        elif move_count <= 30:
            return 1.0
        else:
            return 0.8  # 太多移动可能让玩家困惑
    
    def _evaluate_balance(self, game: Match3Game) -> float:
        """评估平衡性：通过模拟游戏检查难度"""
        # 简单的随机游戏模拟
        simulation_results = []
        
        for _ in range(5):  # 运行5次模拟
            sim_game = Match3Game(game.width, game.height, game.gem_types)
            sim_game.board = game.board.copy()
            sim_game.set_level_config(game.target_score, game.moves_left)
            
            moves_made = 0
            total_score = 0
            
            # 随机玩游戏
            while not sim_game.is_game_over and moves_made < 100:
                valid_moves = sim_game.get_valid_moves()
                if not valid_moves:
                    break
                
                move = random.choice(valid_moves)
                _, score, _ = sim_game.make_move(move)
                total_score += score
                moves_made += 1
            
            # 记录结果
            success = sim_game.is_level_completed()
            progress = sim_game.get_level_progress()
            simulation_results.append((success, progress, moves_made))
        
        # 分析结果
        success_rate = sum(1 for success, _, _ in simulation_results if success) / len(simulation_results)
        avg_progress = sum(progress for _, progress, _ in simulation_results) / len(simulation_results)
        
        # 理想的平衡：30-70%的成功率，60-90%的平均进度
        balance_score = 0.0
        
        if 0.3 <= success_rate <= 0.7:
            balance_score += 0.5
        elif 0.1 <= success_rate <= 0.9:
            balance_score += 0.3
        
        if 0.6 <= avg_progress <= 0.9:
            balance_score += 0.5
        elif 0.4 <= avg_progress <= 1.0:
            balance_score += 0.3
        
        return min(1.0, balance_score)
    
    def _evaluate_fun_factor(self, game: Match3Game) -> float:
        """评估趣味性：宝石分布的多样性和策略潜力"""
        board = game.board
        
        # 1. 宝石类型分布
        gem_counts = np.bincount(board.flatten(), minlength=self.gem_types + 1)[1:]  # 排除空格
        gem_distribution = gem_counts / gem_counts.sum()
        
        # 计算分布均匀性（香农熵）
        entropy = 0.0
        for p in gem_distribution:
            if p > 0:
                entropy -= p * np.log2(p)
        
        max_entropy = np.log2(self.gem_types)
        distribution_score = entropy / max_entropy
        
        # 2. 潜在连锁反应
        # 检查有多少位置可能形成潜在的匹配
        potential_matches = 0
        for row in range(game.height):
            for col in range(game.width):
                # 检查周围是否有相同宝石（潜在匹配）
                gem_type = board[row, col]
                same_neighbors = 0
                
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < game.height and 0 <= nc < game.width:
                        if board[nr, nc] == gem_type:
                            same_neighbors += 1
                
                if same_neighbors >= 1:
                    potential_matches += 1
        
        potential_score = min(1.0, potential_matches / (self.total_cells * 0.3))
        
        # 综合趣味性评分
        fun_score = (distribution_score * 0.6 + potential_score * 0.4)
        
        return fun_score
    
    def get_current_level(self) -> Dict[str, Any]:
        """获取当前设计的关卡"""
        return {
            'board': self.current_board.copy(),
            'target_score': self.current_target_score,
            'moves_limit': self.current_moves_limit,
            'quality_score': self._evaluate_level_quality()
        }
    
    def render(self, mode: str = 'human') -> Optional[str]:
        """渲染当前关卡设计状态"""
        if mode == 'human':
            print(f"\n=== 关卡设计状态 ===")
            print(f"设计步骤: {self.design_steps}/{self.max_design_steps}")
            print(f"目标分数: {self.current_target_score}")
            print(f"移动限制: {self.current_moves_limit}")
            print(f"质量评分: {self._evaluate_level_quality():.3f}")
            print(f"\n棋盘状态:")
            
            gem_chars = {0: '.', 1: 'R', 2: 'B', 3: 'G', 4: 'Y', 5: 'P', 6: 'O'}
            for row in self.current_board:
                print(' '.join(gem_chars.get(gem, '?') for gem in row))
            print()
        
        elif mode == 'ansi':
            # 返回彩色字符串表示
            color_codes = {
                0: '\033[90m.',  # 灰色
                1: '\033[91mR',  # 红色
                2: '\033[94mB',  # 蓝色  
                3: '\033[92mG',  # 绿色
                4: '\033[93mY',  # 黄色
                5: '\033[95mP',  # 紫色
                6: '\033[96mO'   # 青色
            }
            
            result = ""
            for row in self.current_board:
                for gem in row:
                    result += color_codes.get(gem, '?') + '\033[0m '
                result += '\n'
            
            return result


if __name__ == "__main__":
    # 简单测试
    env = LevelDesignEnv()
    
    obs, info = env.reset()
    print("初始观测:", obs)
    print("初始信息:", info)
    
    # 随机执行一些动作
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"步骤 {i+1}: 动作={action}, 奖励={reward:.3f}, 质量={info['level_quality']:.3f}")
        
        if terminated or truncated:
            break
    
    # 显示最终关卡
    final_level = env.get_current_level()
    print(f"\n最终关卡质量: {final_level['quality_score']:.3f}")
    env.render()
