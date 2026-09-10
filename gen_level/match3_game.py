"""
三消游戏核心模拟器
"""

import numpy as np
import random
from typing import List, Tuple, Set, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import copy


class GemType(Enum):
    """宝石类型"""
    EMPTY = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    PURPLE = 5
    ORANGE = 6


@dataclass
class Move:
    """移动操作"""
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]


@dataclass
class MatchGroup:
    """匹配组"""
    positions: List[Tuple[int, int]]
    gem_type: GemType
    is_horizontal: bool


@dataclass
class GameState:
    """游戏状态"""
    board: np.ndarray
    score: int
    moves_left: int
    is_game_over: bool
    target_score: int


class Match3Game:
    """三消游戏核心类"""
    
    def __init__(self, width: int = 8, height: int = 8, gem_types: int = 6):
        self.width = width
        self.height = height
        self.gem_types = gem_types  # 不包括EMPTY
        self.board = np.zeros((height, width), dtype=int)
        self.score = 0
        self.moves_left = 30
        self.target_score = 1000
        self.is_game_over = False
        
        # 游戏规则参数
        self.min_match_length = 3
        self.points_per_gem = 10
        self.combo_multiplier = 1.5
        
        self.reset()
    
    def reset(self) -> GameState:
        """重置游戏"""
        self.score = 0
        self.moves_left = 30
        self.is_game_over = False
        self.board = self._generate_initial_board()
        return self.get_state()
    
    def _generate_initial_board(self) -> np.ndarray:
        """生成初始棋盘，确保没有初始匹配"""
        board = np.zeros((self.height, self.width), dtype=int)
        
        for row in range(self.height):
            for col in range(self.width):
                # 生成候选宝石类型
                candidates = list(range(1, self.gem_types + 1))
                
                # 排除会形成水平匹配的类型
                if col >= 2:
                    if board[row, col-1] == board[row, col-2] != 0:
                        if board[row, col-1] in candidates:
                            candidates.remove(board[row, col-1])
                
                # 排除会形成垂直匹配的类型
                if row >= 2:
                    if board[row-1, col] == board[row-2, col] != 0:
                        if board[row-1, col] in candidates:
                            candidates.remove(board[row-1, col])
                
                # 如果没有候选，则随机选择
                if not candidates:
                    candidates = list(range(1, self.gem_types + 1))
                
                board[row, col] = random.choice(candidates)
        
        return board
    
    def get_state(self) -> GameState:
        """获取当前游戏状态"""
        return GameState(
            board=self.board.copy(),
            score=self.score,
            moves_left=self.moves_left,
            is_game_over=self.is_game_over,
            target_score=self.target_score
        )
    
    def get_valid_moves(self) -> List[Move]:
        """获取所有有效移动"""
        valid_moves = []
        
        for row in range(self.height):
            for col in range(self.width):
                # 检查右侧交换
                if col < self.width - 1:
                    move = Move((row, col), (row, col + 1))
                    if self._is_valid_move(move):
                        valid_moves.append(move)
                
                # 检查下方交换
                if row < self.height - 1:
                    move = Move((row, col), (row + 1, col))
                    if self._is_valid_move(move):
                        valid_moves.append(move)
        
        return valid_moves
    
    def _is_valid_move(self, move: Move) -> bool:
        """检查移动是否有效（会产生匹配）"""
        # 临时交换
        temp_board = self.board.copy()
        self._swap_gems(temp_board, move.from_pos, move.to_pos)
        
        # 检查是否产生匹配
        matches = self._find_matches(temp_board)
        return len(matches) > 0
    
    def _swap_gems(self, board: np.ndarray, pos1: Tuple[int, int], pos2: Tuple[int, int]):
        """交换两个位置的宝石"""
        board[pos1], board[pos2] = board[pos2], board[pos1]
    
    def make_move(self, move: Move) -> Tuple[GameState, int, bool]:
        """执行移动，返回新状态、得分增量、是否结束"""
        if self.is_game_over:
            return self.get_state(), 0, True
        
        if not self._is_valid_move(move):
            # 无效移动，扣除步数但不得分
            self.moves_left -= 1
            self._check_game_over()
            return self.get_state(), 0, self.is_game_over
        
        # 执行交换
        self._swap_gems(self.board, move.from_pos, move.to_pos)
        
        # 处理连锁反应
        total_score = 0
        combo_count = 0
        
        while True:
            matches = self._find_matches(self.board)
            if not matches:
                break
            
            # 消除匹配的宝石
            points = self._remove_matches(matches)
            total_score += int(points * (self.combo_multiplier ** combo_count))
            combo_count += 1
            
            # 重力下落
            self._apply_gravity()
            
            # 填充新宝石
            self._fill_empty_spaces()
        
        self.score += total_score
        self.moves_left -= 1
        self._check_game_over()
        
        return self.get_state(), total_score, self.is_game_over
    
    def _find_matches(self, board: np.ndarray) -> List[MatchGroup]:
        """找到所有匹配组"""
        matches = []
        visited = set()
        
        # 检查水平匹配
        for row in range(self.height):
            col = 0
            while col < self.width:
                if board[row, col] == 0:  # 跳过空格
                    col += 1
                    continue
                
                # 找到连续相同的宝石
                gem_type = board[row, col]
                count = 1
                start_col = col
                
                while col + count < self.width and board[row, col + count] == gem_type:
                    count += 1
                
                if count >= self.min_match_length:
                    positions = [(row, start_col + i) for i in range(count)]
                    # 检查这些位置是否已经被访问过
                    if not any(pos in visited for pos in positions):
                        matches.append(MatchGroup(positions, GemType(gem_type), True))
                        visited.update(positions)
                
                col += max(1, count)
        
        # 检查垂直匹配
        for col in range(self.width):
            row = 0
            while row < self.height:
                if board[row, col] == 0:  # 跳过空格
                    row += 1
                    continue
                
                # 找到连续相同的宝石
                gem_type = board[row, col]
                count = 1
                start_row = row
                
                while row + count < self.height and board[row + count, col] == gem_type:
                    count += 1
                
                if count >= self.min_match_length:
                    positions = [(start_row + i, col) for i in range(count)]
                    # 检查这些位置是否已经被访问过
                    if not any(pos in visited for pos in positions):
                        matches.append(MatchGroup(positions, GemType(gem_type), False))
                        visited.update(positions)
                
                row += max(1, count)
        
        return matches
    
    def _remove_matches(self, matches: List[MatchGroup]) -> int:
        """移除匹配的宝石并返回得分"""
        total_gems = 0
        
        for match in matches:
            for pos in match.positions:
                if self.board[pos] != 0:
                    self.board[pos] = 0
                    total_gems += 1
        
        return total_gems * self.points_per_gem
    
    def _apply_gravity(self):
        """应用重力，让宝石下落"""
        for col in range(self.width):
            # 收集非空宝石
            gems = []
            for row in range(self.height - 1, -1, -1):
                if self.board[row, col] != 0:
                    gems.append(self.board[row, col])
                    self.board[row, col] = 0
            
            # 重新放置宝石
            for i, gem in enumerate(gems):
                self.board[self.height - 1 - i, col] = gem
    
    def _fill_empty_spaces(self):
        """填充空白位置"""
        for col in range(self.width):
            for row in range(self.height):
                if self.board[row, col] == 0:
                    self.board[row, col] = random.randint(1, self.gem_types)
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        if self.moves_left <= 0:
            self.is_game_over = True
        elif self.score >= self.target_score:
            self.is_game_over = True
        elif len(self.get_valid_moves()) == 0:
            self.is_game_over = True
    
    def is_level_completed(self) -> bool:
        """检查关卡是否完成"""
        return self.score >= self.target_score
    
    def get_level_progress(self) -> float:
        """获取关卡进度（0-1）"""
        return min(1.0, self.score / self.target_score)
    
    def set_level_config(self, target_score: int, moves_limit: int):
        """设置关卡配置"""
        self.target_score = target_score
        self.moves_left = moves_limit
    
    def get_board_visual(self) -> str:
        """获取棋盘的可视化字符串"""
        gem_chars = {
            0: '.',
            1: 'R',  # Red
            2: 'B',  # Blue
            3: 'G',  # Green
            4: 'Y',  # Yellow
            5: 'P',  # Purple
            6: 'O'   # Orange
        }
        
        result = ""
        for row in self.board:
            for gem in row:
                result += gem_chars.get(gem, '?') + ' '
            result += '\n'
        
        result += f"Score: {self.score}/{self.target_score}, Moves: {self.moves_left}\n"
        return result


if __name__ == "__main__":
    # 简单测试
    game = Match3Game()
    print("初始棋盘:")
    print(game.get_board_visual())
    
    valid_moves = game.get_valid_moves()
    print(f"有效移动数: {len(valid_moves)}")
    
    if valid_moves:
        move = valid_moves[0]
        print(f"执行移动: {move.from_pos} -> {move.to_pos}")
        state, score, done = game.make_move(move)
        print(f"得分: {score}")
        print(game.get_board_visual())
