"""
三消游戏关卡生成器
支持不同难度和风格的关卡生成
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass
import json
import copy

from match3_game import Match3Game, GemType


class DifficultyLevel(Enum):
    """难度等级"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class LevelType(Enum):
    """关卡类型"""
    SCORE = "score"          # 分数目标
    MOVES_LIMITED = "moves"  # 限制移动次数
    TIME_LIMITED = "time"    # 限时模式（暂不实现）
    CLEAR_ALL = "clear"      # 清除所有特定宝石


@dataclass
class LevelConfig:
    """关卡配置"""
    level_id: int
    difficulty: DifficultyLevel
    level_type: LevelType
    board: np.ndarray
    target_score: int
    moves_limit: int
    special_objectives: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'level_id': self.level_id,
            'difficulty': self.difficulty.value,
            'level_type': self.level_type.value,
            'board': self.board.tolist(),
            'target_score': self.target_score,
            'moves_limit': self.moves_limit,
            'special_objectives': self.special_objectives or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LevelConfig':
        """从字典创建关卡配置"""
        return cls(
            level_id=data['level_id'],
            difficulty=DifficultyLevel(data['difficulty']),
            level_type=LevelType(data['level_type']),
            board=np.array(data['board']),
            target_score=data['target_score'],
            moves_limit=data['moves_limit'],
            special_objectives=data.get('special_objectives', {})
        )


class LevelGenerator:
    """关卡生成器"""
    
    def __init__(self, board_width: int = 8, board_height: int = 8, gem_types: int = 6):
        self.board_width = board_width
        self.board_height = board_height
        self.gem_types = gem_types
        
        # 难度参数配置
        self.difficulty_configs = {
            DifficultyLevel.EASY: {
                'target_score_range': (500, 1000),
                'moves_range': (35, 50),
                'gem_types_used': 4,  # 只使用4种宝石类型
                'guaranteed_moves': 15,  # 保证至少15个有效移动
            },
            DifficultyLevel.MEDIUM: {
                'target_score_range': (1000, 2000),
                'moves_range': (25, 35),
                'gem_types_used': 5,
                'guaranteed_moves': 10,
            },
            DifficultyLevel.HARD: {
                'target_score_range': (2000, 3500),
                'moves_range': (20, 30),
                'gem_types_used': 6,
                'guaranteed_moves': 8,
            },
            DifficultyLevel.EXPERT: {
                'target_score_range': (3500, 5000),
                'moves_range': (15, 25),
                'gem_types_used': 6,
                'guaranteed_moves': 5,
            }
        }
        
        # 关卡模板
        self.level_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化关卡模板"""
        return {
            'standard': {
                'description': '标准关卡',
                'gem_distribution': 'uniform',  # 均匀分布
                'obstacles': False,
                'special_patterns': []
            },
            'corner_challenge': {
                'description': '角落挑战',
                'gem_distribution': 'corners',  # 角落集中
                'obstacles': False,
                'special_patterns': ['corner_focus']
            },
            'center_burst': {
                'description': '中心爆发',
                'gem_distribution': 'center',  # 中心集中
                'obstacles': False,
                'special_patterns': ['center_focus']
            },
            'striped': {
                'description': '条纹模式',
                'gem_distribution': 'striped',  # 条纹分布
                'obstacles': False,
                'special_patterns': ['horizontal_stripes', 'vertical_stripes']
            },
            'scattered': {
                'description': '分散模式',
                'gem_distribution': 'scattered',  # 分散分布
                'obstacles': False,
                'special_patterns': ['random_clusters']
            }
        }
    
    def generate_level(self, difficulty: DifficultyLevel, level_type: LevelType = LevelType.SCORE,
                      template: str = 'standard', level_id: int = None) -> LevelConfig:
        """生成关卡"""
        if level_id is None:
            level_id = random.randint(10000, 99999)
        
        config = self.difficulty_configs[difficulty]
        template_config = self.level_templates.get(template, self.level_templates['standard'])
        
        # 生成棋盘
        board = self._generate_board(difficulty, template_config)
        
        # 设置目标和限制
        target_score = random.randint(*config['target_score_range'])
        moves_limit = random.randint(*config['moves_range'])
        
        # 根据关卡类型调整参数
        if level_type == LevelType.MOVES_LIMITED:
            # 限制移动次数的关卡，降低目标分数
            target_score = int(target_score * 0.7)
        elif level_type == LevelType.CLEAR_ALL:
            # 清除特定宝石类型的关卡
            target_gem_type = random.randint(1, config['gem_types_used'])
            special_objectives = {'clear_gem_type': target_gem_type}
        else:
            special_objectives = None
        
        # 验证并优化关卡
        board, target_score, moves_limit = self._optimize_level(
            board, target_score, moves_limit, difficulty
        )
        
        return LevelConfig(
            level_id=level_id,
            difficulty=difficulty,
            level_type=level_type,
            board=board,
            target_score=target_score,
            moves_limit=moves_limit,
            special_objectives=special_objectives
        )
    
    def _generate_board(self, difficulty: DifficultyLevel, template_config: Dict[str, Any]) -> np.ndarray:
        """根据难度和模板生成棋盘"""
        config = self.difficulty_configs[difficulty]
        gem_types_used = config['gem_types_used']
        
        distribution_type = template_config['gem_distribution']
        
        if distribution_type == 'uniform':
            board = self._generate_uniform_board(gem_types_used)
        elif distribution_type == 'corners':
            board = self._generate_corner_focused_board(gem_types_used)
        elif distribution_type == 'center':
            board = self._generate_center_focused_board(gem_types_used)
        elif distribution_type == 'striped':
            board = self._generate_striped_board(gem_types_used)
        elif distribution_type == 'scattered':
            board = self._generate_scattered_board(gem_types_used)
        else:
            board = self._generate_uniform_board(gem_types_used)
        
        # 应用特殊模式
        for pattern in template_config.get('special_patterns', []):
            board = self._apply_special_pattern(board, pattern, gem_types_used)
        
        return board
    
    def _generate_uniform_board(self, gem_types_used: int) -> np.ndarray:
        """生成均匀分布的棋盘"""
        game = Match3Game(self.board_width, self.board_height, gem_types_used)
        return game._generate_initial_board()
    
    def _generate_corner_focused_board(self, gem_types_used: int) -> np.ndarray:
        """生成角落集中的棋盘"""
        board = np.zeros((self.board_height, self.board_width), dtype=int)
        
        # 定义角落区域
        corner_size = 3
        corners = [
            (0, 0, corner_size, corner_size),  # 左上
            (0, self.board_width - corner_size, corner_size, corner_size),  # 右上
            (self.board_height - corner_size, 0, corner_size, corner_size),  # 左下
            (self.board_height - corner_size, self.board_width - corner_size, corner_size, corner_size)  # 右下
        ]
        
        # 为每个角落分配特定的宝石类型
        corner_gems = random.sample(range(1, gem_types_used + 1), min(4, gem_types_used))
        
        for i, (start_row, start_col, height, width) in enumerate(corners):
            gem_type = corner_gems[i % len(corner_gems)]
            for row in range(start_row, min(start_row + height, self.board_height)):
                for col in range(start_col, min(start_col + width, self.board_width)):
                    # 80%概率放置指定宝石，20%概率随机
                    if random.random() < 0.8:
                        board[row, col] = gem_type
                    else:
                        board[row, col] = random.randint(1, gem_types_used)
        
        # 填充其余位置
        for row in range(self.board_height):
            for col in range(self.board_width):
                if board[row, col] == 0:
                    board[row, col] = random.randint(1, gem_types_used)
        
        # 移除初始匹配
        return self._remove_initial_matches(board, gem_types_used)
    
    def _generate_center_focused_board(self, gem_types_used: int) -> np.ndarray:
        """生成中心集中的棋盘"""
        board = np.zeros((self.board_height, self.board_width), dtype=int)
        
        center_row = self.board_height // 2
        center_col = self.board_width // 2
        
        # 特殊宝石类型放在中心
        center_gem = random.randint(1, gem_types_used)
        
        for row in range(self.board_height):
            for col in range(self.board_width):
                # 计算到中心的距离
                distance = abs(row - center_row) + abs(col - center_col)
                max_distance = center_row + center_col
                
                # 距离越近，放置中心宝石的概率越高
                center_prob = 1.0 - (distance / max_distance)
                center_prob = center_prob ** 2  # 增强中心效应
                
                if random.random() < center_prob:
                    board[row, col] = center_gem
                else:
                    board[row, col] = random.randint(1, gem_types_used)
        
        return self._remove_initial_matches(board, gem_types_used)
    
    def _generate_striped_board(self, gem_types_used: int) -> np.ndarray:
        """生成条纹模式的棋盘"""
        board = np.zeros((self.board_height, self.board_width), dtype=int)
        
        # 随机选择条纹方向
        horizontal = random.choice([True, False])
        stripe_width = random.randint(2, 3)
        
        gem_sequence = list(range(1, gem_types_used + 1))
        random.shuffle(gem_sequence)
        
        for row in range(self.board_height):
            for col in range(self.board_width):
                if horizontal:
                    stripe_index = (row // stripe_width) % len(gem_sequence)
                else:
                    stripe_index = (col // stripe_width) % len(gem_sequence)
                
                # 90%概率遵循条纹模式，10%概率随机
                if random.random() < 0.9:
                    board[row, col] = gem_sequence[stripe_index]
                else:
                    board[row, col] = random.randint(1, gem_types_used)
        
        return self._remove_initial_matches(board, gem_types_used)
    
    def _generate_scattered_board(self, gem_types_used: int) -> np.ndarray:
        """生成分散集群模式的棋盘"""
        board = np.zeros((self.board_height, self.board_width), dtype=int)
        
        # 随机生成集群中心
        num_clusters = random.randint(3, 6)
        cluster_centers = []
        
        for _ in range(num_clusters):
            center_row = random.randint(1, self.board_height - 2)
            center_col = random.randint(1, self.board_width - 2)
            gem_type = random.randint(1, gem_types_used)
            cluster_centers.append((center_row, center_col, gem_type))
        
        # 为每个位置分配宝石
        for row in range(self.board_height):
            for col in range(self.board_width):
                # 找到最近的集群中心
                min_distance = float('inf')
                closest_gem = random.randint(1, gem_types_used)
                
                for center_row, center_col, gem_type in cluster_centers:
                    distance = abs(row - center_row) + abs(col - center_col)
                    if distance < min_distance:
                        min_distance = distance
                        closest_gem = gem_type
                
                # 距离越近，使用集群宝石的概率越高
                cluster_prob = max(0.1, 1.0 - min_distance / 5.0)
                
                if random.random() < cluster_prob:
                    board[row, col] = closest_gem
                else:
                    board[row, col] = random.randint(1, gem_types_used)
        
        return self._remove_initial_matches(board, gem_types_used)
    
    def _apply_special_pattern(self, board: np.ndarray, pattern: str, gem_types_used: int) -> np.ndarray:
        """应用特殊模式"""
        if pattern == 'corner_focus':
            # 强化角落区域的特定宝石
            special_gem = random.randint(1, gem_types_used)
            for row in [0, 1, self.board_height-2, self.board_height-1]:
                for col in [0, 1, self.board_width-2, self.board_width-1]:
                    if random.random() < 0.3:
                        board[row, col] = special_gem
        
        elif pattern == 'center_focus':
            # 在中心放置特殊宝石
            center_row = self.board_height // 2
            center_col = self.board_width // 2
            special_gem = random.randint(1, gem_types_used)
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if 0 <= center_row + dr < self.board_height and 0 <= center_col + dc < self.board_width:
                        if random.random() < 0.4:
                            board[center_row + dr, center_col + dc] = special_gem
        
        return board
    
    def _remove_initial_matches(self, board: np.ndarray, gem_types_used: int) -> np.ndarray:
        """移除初始匹配，确保棋盘可玩"""
        game = Match3Game(self.board_width, self.board_height, gem_types_used)
        game.board = board.copy()
        
        # 循环检查并移除匹配
        max_iterations = 50
        iteration = 0
        
        while iteration < max_iterations:
            matches = game._find_matches(game.board)
            if not matches:
                break
            
            # 随机改变匹配中的一些宝石
            for match in matches:
                for pos in match.positions[::2]:  # 每隔一个位置修改
                    # 选择一个不会形成新匹配的宝石类型
                    candidates = list(range(1, gem_types_used + 1))
                    row, col = pos
                    
                    # 排除可能形成匹配的类型
                    if col > 0 and col < self.board_width - 1:
                        if game.board[row, col-1] == game.board[row, col+1]:
                            candidates = [g for g in candidates if g != game.board[row, col-1]]
                    
                    if row > 0 and row < self.board_height - 1:
                        if game.board[row-1, col] == game.board[row+1, col]:
                            candidates = [g for g in candidates if g != game.board[row-1, col]]
                    
                    if candidates:
                        game.board[row, col] = random.choice(candidates)
            
            iteration += 1
        
        return game.board
    
    def _optimize_level(self, board: np.ndarray, target_score: int, moves_limit: int,
                       difficulty: DifficultyLevel) -> Tuple[np.ndarray, int, int]:
        """优化关卡参数以确保平衡性"""
        config = self.difficulty_configs[difficulty]
        
        # 创建游戏测试关卡
        game = Match3Game(self.board_width, self.board_height, config['gem_types_used'])
        game.board = board.copy()
        game.set_level_config(target_score, moves_limit)
        
        # 检查可用移动数量
        valid_moves = game.get_valid_moves()
        
        if len(valid_moves) < config['guaranteed_moves']:
            # 移动太少，增加一些容易匹配的模式
            board = self._add_easy_matches(board, config['gem_types_used'])
        
        # 通过模拟调整难度
        simulation_results = self._simulate_level(board, target_score, moves_limit, config['gem_types_used'])
        
        avg_completion_rate = simulation_results['completion_rate']
        avg_score_ratio = simulation_results['avg_score_ratio']
        
        # 根据模拟结果调整参数
        if avg_completion_rate < 0.2:  # 太难
            target_score = int(target_score * 0.8)
            moves_limit = min(moves_limit + 5, config['moves_range'][1])
        elif avg_completion_rate > 0.8:  # 太容易
            target_score = int(target_score * 1.2)
            moves_limit = max(moves_limit - 3, config['moves_range'][0])
        
        return board, target_score, moves_limit
    
    def _add_easy_matches(self, board: np.ndarray, gem_types_used: int) -> np.ndarray:
        """添加一些容易匹配的模式"""
        board = board.copy()
        
        # 随机选择几个位置创建容易的匹配机会
        for _ in range(3):
            row = random.randint(1, self.board_height - 2)
            col = random.randint(1, self.board_width - 2)
            gem_type = random.randint(1, gem_types_used)
            
            # 在该位置周围放置相同宝石
            if random.choice([True, False]):  # 水平模式
                if col + 1 < self.board_width:
                    board[row, col] = gem_type
                    board[row, col + 1] = gem_type
            else:  # 垂直模式
                if row + 1 < self.board_height:
                    board[row, col] = gem_type
                    board[row + 1, col] = gem_type
        
        return self._remove_initial_matches(board, gem_types_used)
    
    def _simulate_level(self, board: np.ndarray, target_score: int, moves_limit: int,
                       gem_types_used: int) -> Dict[str, float]:
        """模拟关卡进行平衡性测试"""
        num_simulations = 10
        completion_count = 0
        score_ratios = []
        
        for _ in range(num_simulations):
            game = Match3Game(self.board_width, self.board_height, gem_types_used)
            game.board = board.copy()
            game.set_level_config(target_score, moves_limit)
            
            # 随机游戏模拟
            while not game.is_game_over:
                valid_moves = game.get_valid_moves()
                if not valid_moves:
                    break
                
                move = random.choice(valid_moves)
                game.make_move(move)
            
            if game.is_level_completed():
                completion_count += 1
            
            score_ratio = game.score / target_score
            score_ratios.append(score_ratio)
        
        return {
            'completion_rate': completion_count / num_simulations,
            'avg_score_ratio': sum(score_ratios) / len(score_ratios)
        }
    
    def generate_level_series(self, num_levels: int, difficulty_progression: bool = True) -> List[LevelConfig]:
        """生成一系列关卡"""
        levels = []
        
        if difficulty_progression:
            # 难度逐渐增加
            difficulties = [DifficultyLevel.EASY] * (num_levels // 4) + \
                          [DifficultyLevel.MEDIUM] * (num_levels // 4) + \
                          [DifficultyLevel.HARD] * (num_levels // 4) + \
                          [DifficultyLevel.EXPERT] * (num_levels - 3 * (num_levels // 4))
        else:
            # 随机难度
            difficulties = [random.choice(list(DifficultyLevel)) for _ in range(num_levels)]
        
        templates = list(self.level_templates.keys())
        level_types = [LevelType.SCORE, LevelType.MOVES_LIMITED]
        
        for i, difficulty in enumerate(difficulties):
            template = random.choice(templates)
            level_type = random.choice(level_types)
            
            level = self.generate_level(
                difficulty=difficulty,
                level_type=level_type,
                template=template,
                level_id=i + 1
            )
            levels.append(level)
        
        return levels
    
    def save_levels(self, levels: List[LevelConfig], filename: str):
        """保存关卡到文件"""
        levels_data = [level.to_dict() for level in levels]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(levels_data, f, indent=2, ensure_ascii=False)
    
    def load_levels(self, filename: str) -> List[LevelConfig]:
        """从文件加载关卡"""
        with open(filename, 'r', encoding='utf-8') as f:
            levels_data = json.load(f)
        
        return [LevelConfig.from_dict(data) for data in levels_data]


if __name__ == "__main__":
    # 测试关卡生成器
    generator = LevelGenerator()
    
    print("=== 关卡生成器测试 ===")
    
    # 生成不同难度的关卡
    for difficulty in DifficultyLevel:
        print(f"\n生成{difficulty.value}难度关卡:")
        level = generator.generate_level(difficulty)
        
        print(f"关卡ID: {level.level_id}")
        print(f"目标分数: {level.target_score}")
        print(f"移动限制: {level.moves_limit}")
        
        # 简单展示棋盘
        gem_chars = {0: '.', 1: 'R', 2: 'B', 3: 'G', 4: 'Y', 5: 'P', 6: 'O'}
        print("棋盘:")
        for row in level.board:
            print(' '.join(gem_chars.get(gem, '?') for gem in row))
    
    # 生成关卡系列
    print(f"\n=== 生成10个关卡系列 ===")
    levels = generator.generate_level_series(10)
    
    # 保存关卡
    generator.save_levels(levels, "gen_level/sample_levels.json")
    print("关卡已保存到 sample_levels.json")
    
    # 显示统计信息
    difficulty_counts = {}
    for level in levels:
        diff = level.difficulty.value
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
    
    print("难度分布:", difficulty_counts)
