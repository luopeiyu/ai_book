import random
import copy
import numpy as np


class BaseLevelConfig:
    def __init__(self):
        self.board = None
        self.moves = 30
        self.score = 1000

    def get_radom_board(size=6):
        board = [[random.randint(0, 4) for _ in range(size)] for _ in range(size)]
        return board
    
    def calc_moves_range(size=6):
        return list(range(1, int(size * size / 3) + 1))
        
    def calc_score_range(size=6, moves=3):
        min_score = moves * 3
        max_score =  int(size * size)
        return [x * 100 for x in range(min_score, max_score+1)]



level_1_config = BaseLevelConfig()
level_1_config.board = [
    [0, 1, 2, 3, 4, 0],
    [1, 2, 3, 4, 0, 1],
    [2, 3, 4, 0, 1, 2],
    [3, 4, 0, 1, 2, 3],
    [4, 1, 1, 2, 3, 4],
    [0, 1, 2, 3, 4, 0],
]

level_1_config.moves = 6
level_1_config.score = 1000
# 3 3 1 → 2 2 1 → 2 3 1→3 4 2


level_2_config = BaseLevelConfig()
level_2_config.board = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 3, 2, 2, 0],
    [3, 3, 0, 0, 0, 2],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [1, 1, 0, 1, 1, 0],
]
level_2_config.moves = 2
level_2_config.score = 1100
# 只有消除最下面的，才能2步完成 胜：2 4 1 → 3 3 2 败：3 2 2 → 3 1 1




level_3_config = BaseLevelConfig()
level_3_config.board = [
    [4, 4, 1, 4, 1, 1],
    [2, 2, 4, 4, 1, 2],
    [1, 2, 4, 1, 2, 2],
    [1, 4, 0, 2, 4, 1],
    [0, 1, 0, 0, 3, 1],
    [1, 0, 4, 4, 0, 4]
]
level_3_config.score = 1500
level_3_config.moves = 3


class Match3Game:
    def __init__(self):
        self.size = 6
        self.board = None
        self.target_score = 1000
        self.target_moves = 30
        self.score = 0
        self.moves_left = 30
    
    def reset(self, level_config):
        self.size = len(level_config.board)
        self.board = copy.deepcopy(level_config.board)
        self.target_moves = level_config.moves
        self.target_score = level_config.score
        self.moves_left = self.target_moves
        self.score = 0

    def is_win(self):
        return self.score >= self.target_score and self.moves_left >= 0
    
    def is_game_over(self):
        return self.moves_left <= 0

    def temp_swap_gem(self, temp_board, x, y, dir):
        # dir: 0: 上, 1: 下, 2: 左, 3: 右
        tb = temp_board
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return tb
        if dir == 0 and y > 0:
            tb[y][x], tb[y-1][x] = tb[y-1][x], tb[y][x]
        elif dir == 1 and y < self.size - 1:
            tb[y][x], tb[y+1][x] = tb[y+1][x], tb[y][x]
        elif dir == 2 and x > 0:
            tb[y][x], tb[y][x-1] = tb[y][x-1], tb[y][x]
        elif dir == 3 and x < self.size - 1:
            tb[y][x], tb[y][x+1] = tb[y][x+1], tb[y][x]
        else:
            return tb
        
        return tb

    def has_match_horizontal(self, board, x, y):
        
        # 打印棋盘，并标注x和y上的宝石
        gem_type = board[y][x]
        if gem_type == 0:
            return False
        if x <= 0 or x >= self.size - 1:
            return False
        
        if board[y][x-1] == gem_type and board[y][x+1] == gem_type:
            return True
        return False
    
    def has_match_vertical(self, board, x, y):
        gem_type = board[y][x]
        if gem_type == 0:
            return False
        if y <= 0 or y >= self.size - 1:
            return False
        
        if board[y-1][x] == gem_type and board[y+1][x] == gem_type:
            return True
        return False

    def find_matches(self, board):
        matched = np.zeros((self.size, self.size))
        for y in range(0, self.size):
            for x in range(0, self.size):
                if self.has_match_horizontal(board, x, y):
                    matched[y][x] = 1
                    matched[y][x-1] = 1
                    matched[y][x+1] = 1
                if self.has_match_vertical(board, x, y):
                    matched[y][x] = 1
                    matched[y-1][x] = 1
                    matched[y+1][x] = 1
        
        match_count = np.sum(matched)
        return match_count, matched

    def drop_and_fill(self, board, matched):
        # 1. 先将matched位置全部置为-1
        for y in range(self.size):
            for x in range(self.size):
                if matched[y][x] == 1:
                    board[y][x] = -1

        # 2. 按列处理掉落
        for x in range(self.size):
            current_y = self.size - 1
            # 从下往上遍历，把非-1的宝石往下移动
            for y in range(self.size - 1, -1, -1):
                if board[y][x] != -1:
                    if current_y != y:
                        board[current_y][x] = board[y][x]
                    current_y -= 1
            # 上面剩下的空位全部填0
            for y in range(current_y, -1, -1):
                board[y][x] = 0

        return board

    def action(self, x, y, dir):
        # dir:0: 上, 1: 下, 2: 左, 3: 右
        # 返回  is_win, is_loss, is_vaild
        temp_board = copy.deepcopy(self.board)
        temp_board = self.temp_swap_gem(temp_board, x, y, dir)
        
        # 检查是否产生匹配
        match_count, matched = self.find_matches(temp_board)
        if match_count == 0:
            return False, False, False
        # 消除匹配
        while match_count > 0:
            self.score += match_count * 100
            self.drop_and_fill(temp_board, matched)
            match_count, matched = self.find_matches(temp_board)
        # 更新棋盘和步数
        self.board = temp_board
        self.moves_left -= 1

        # 返回
        if self.is_win():
            return True, False, True
        
        if self.is_game_over():
            return False, True, True
        
        return False, False, True
     
    def draw(self):
        print("=" * 20)
        for y in range(self.size):
            for x in range(self.size):
                print(self.board[y][x], end=' ')
            print()
        
        print(f"步数: {self.moves_left}/{self.target_moves}")
        print(f"分数: {int(self.score)}/{int(self.target_score)}")
        
        
class GameAgent:    
    def predict(self, game):
        # 返回 (isok, x, y, dir)，没有可消除的移动则返回 (False, None, None, None)
        max_match = -1
        best_move = (False, None, None, None)
        for y in range(game.size):
            for x in range(game.size):
                for dir in range(4):  # 0:上, 1:下, 2:左, 3:右
                    # 越界判断
                    if dir == 0 and y == 0:
                        continue
                    if dir == 1 and y == game.size - 1:
                        continue
                    if dir == 2 and x == 0:
                        continue
                    if dir == 3 and x == game.size - 1:
                        continue
                    temp_board = copy.deepcopy(game.board)
                    temp_board = game.temp_swap_gem(temp_board, x, y, dir)
                    match_count, matched = game.find_matches(temp_board)
                    if match_count > 0 and match_count > max_match:
                        max_match = match_count
                        best_move = (True, x, y, dir)
        return best_move


def play_by_ai(game_config):
    game = Match3Game()
    game.reset(game_config)
    agent = GameAgent()
    
    is_win, is_loss, is_ok = False, False, True
    while not is_win and not is_loss and is_ok:
        # game.draw()
        is_ok, x, y, dir = agent.predict(game)
        # print(f"AI预测: {is_ok}, {x}, {y}, {dir}")
        if is_ok:
            is_win, is_loss, is_valid = game.action(x, y, dir)
        
    moves = game.target_moves - game.moves_left
    return is_win, moves, game.score


def play_by_human(game_config):
    game = Match3Game()
    game.reset(game_config)
    
    is_win, is_loss, is_valid = False, False, True
    while not is_win and not is_loss and is_valid:
        game.draw()
        x, y, dir = input("请输入移动的宝石坐标和方向(x y dir): ").split()
        x, y, dir = int(x), int(y), int(dir)
        is_win, is_loss, is_valid = game.action(x, y, dir)
    
    game.draw()
    if is_win:
        print("胜利")
    elif is_loss:
        print("失败")
    else:
        print("无效的移动")

    step = game.target_moves - game.moves_left
    return is_win, step, game.score


      
if __name__ == "__main__":
    #play_by_human(level_3_config)
    print(play_by_ai(level_3_config))
    #print(BaseLevelConfig.calc_moves_range(6))
    #print(BaseLevelConfig.calc_score_range(6,10))
    
    