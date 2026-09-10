import gymnasium as gym
import numpy as np
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3 import PPO
import random

from match3_game import BaseLevelConfig, play_by_ai

GEM_TYPE_NUM = 5  # 宝石颜色数量 (0-4)
BOARD_SIZE = 6

class LevelGenerationEnv(gym.Env):
    def __init__(self, moves_range, score_range):
        super(LevelGenerationEnv, self).__init__()

        # 动作空间：选择放置的宝石颜色 (0-4)
        self.action_space = gym.spaces.Discrete(GEM_TYPE_NUM)
        
        state_size = BOARD_SIZE * BOARD_SIZE * GEM_TYPE_NUM + BOARD_SIZE * BOARD_SIZE + 2
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(state_size,), dtype=np.float32)

        self.board = None
        self.current_pos = 0  # 当前生成位置 (0-35)
        self.target_moves = 30
        self.target_score = 3600
        # 步数和分数的目标范围需要区分并明确
        self.target_moves_range = moves_range
        self.target_score_range = score_range

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.target_moves = random.choice(self.target_moves_range)
        allowed_scores = BaseLevelConfig.calc_score_range(BOARD_SIZE, self.target_moves)
        # 取 target_score_range 和 allowed_scores 的交集
        score_range = list(set(self.target_score_range) & set(allowed_scores))
        self.target_score = random.choice(score_range)
                  
            
        self.board = BaseLevelConfig.get_radom_board(BOARD_SIZE)
        self.current_pos = 0

        obs = self.get_observation()

        return obs, {}

    def get_observation(self):
        # 1. 棋盘one-hot编码 (6*6*5 = 180维)
        board_onehot = np.zeros((BOARD_SIZE, BOARD_SIZE, GEM_TYPE_NUM))
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                color = self.board[y][x]
                board_onehot[y][x][color] = 1.0
        board_onehot_flat = board_onehot.flatten()
        
        # 2. 当前位置one-hot编码 (36维)
        position_onehot = np.zeros(BOARD_SIZE * BOARD_SIZE)
        if self.current_pos < BOARD_SIZE * BOARD_SIZE:
            position_onehot[self.current_pos] = 1.0
        
        # 3. 目标参数归一化 (2维)
        max_moves = int(BOARD_SIZE*BOARD_SIZE/3)
        max_score = int(BOARD_SIZE*BOARD_SIZE)*100
        normalized_moves = self.target_moves / max_moves
        normalized_score = self.target_score / max_score
        
        # 组合所有状态
        state = np.concatenate([
            board_onehot_flat,      # 180维
            position_onehot,        # 36维  
            [normalized_moves], [normalized_score]  # 2维
        ]).astype(np.float32)
        
        return state

    def step(self, action):
        # 在当前位置放置宝石
        y = self.current_pos // BOARD_SIZE
        x = self.current_pos % BOARD_SIZE
        self.board[y][x] = action
        
        self.current_pos += 1
        
        # 检查是否完成整个棋盘生成
        done = (self.current_pos >= BOARD_SIZE * BOARD_SIZE)
        
        if done:
            # 棋盘生成完成，计算奖励
            reward = self.calculate_final_reward()
        else:
            reward = 0.0
        return self.get_observation(), reward, done, False, {}        
        

    def calculate_final_reward(self):
        # 创建关卡配置
        level_config = BaseLevelConfig()
        level_config.board = self.board
        level_config.moves = self.target_moves
        level_config.score = self.target_score
        
        is_win, moves, score = play_by_ai(level_config)
        
        # 步数差异奖励
        moves_diff = abs(moves - self.target_moves)
        moves_reward = max(0, 1.0 - moves_diff / self.target_moves)
        moves_reward = moves_reward ** 2  # 平方关系，更重视准确匹配
        
        # 分数差异奖励
        score_diff = abs(score - self.target_score)
        score_reward = max(0, 1.0 - score_diff / self.target_score)
        score_reward = score_reward ** 2
        
        # 惩罚
        penalty = 0
        if moves != self.target_moves:
            penalty += 0.1
        
        if not is_win:
            penalty += 0.1
        
        reward = 0.5 * moves_reward + 0.5 * score_reward - 1.0 * penalty
        
        return reward

class LevelGenerationTrainer:

        
    def create_env(self, moves_range, score_range):
        def _init():
            env = LevelGenerationEnv(moves_range, score_range)
            return env
        return _init
        
    def train(self, total_timesteps=1500000, moves_range=None, score_range=None):
        env = make_vec_env(
            self.create_env(moves_range, score_range),
            n_envs=6,
            vec_env_cls=SubprocVecEnv
        )
        
        model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=0.0003,
            n_steps=256,
            batch_size=256,
            n_epochs=10,
            gamma=0.999,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0,  # 改
            tensorboard_log="./logs/"
        )
            
        model.learn(
            total_timesteps=total_timesteps,
            tb_log_name="level_ppo_6"
        )
        
        model.save("models/level_generator_6")

class LevelGenerator:
    def __init__(self, model_path="models/level_generator_6"):
        self.model = PPO.load(model_path)
    
    def generate_level_config(self, target_moves, target_score):
        env = LevelGenerationEnv(moves_range=[target_moves], score_range=[target_score])
        obs, info = env.reset()
        while True:
            action, _ = self.model.predict(obs)
            obs, reward, done, truncated, info = env.step(action)
            if done:
                break
            
        level_config = BaseLevelConfig()
        level_config.board = env.board
        level_config.moves = target_moves
        level_config.score = target_score
        return level_config
    
    
    def compute_match_score(self, target_moves, target_score, actual_moves, actual_score):
        moves_diff = abs(actual_moves - target_moves)
        moves_reward = max(0, 1.0 - moves_diff / target_moves)
        moves_reward = moves_reward ** 2
        
        score_diff = abs(actual_score - target_score)
        score_reward = max(0, 1.0 - score_diff / target_score)
        score_reward = score_reward ** 2
        
        return 0.5 * moves_reward + 0.5 * score_reward
    
    def generate_optimal_level_config(self, target_moves, target_score):
        MAX_ATTEMPTS = 30
        best_level_config = None
        best_match_score = 0
        
        for i in range(MAX_ATTEMPTS):
            level_config = self.generate_level_config(target_moves, target_score)
            is_win, moves, score = play_by_ai(level_config)
            
            match_score = self.compute_match_score(target_moves, target_score, moves, score)
            if match_score > best_match_score:
                best_match_score = match_score
                best_level_config = level_config
                
        return best_level_config, moves, score



    
if __name__ == "__main__":    
    trainer = LevelGenerationTrainer()
    moves_range=[3,4,5,6,7,8,9,10,11,12]
    score_range = list(range(900, 3601, 100))
    trainer.train(total_timesteps=1500000, moves_range=moves_range, score_range=score_range)
    
    generator = LevelGenerator("models/level_generator_6")
    
    test_targets = [(2, 1500), (3, 1500), (8, 3000)]
    for i, (target_moves, target_score) in enumerate(test_targets):
        print(f"\n--- 测试目标 {i+1}: 期望步数{target_moves}, 期望分数{target_score} ---")
        level_config, moves, score = generator.generate_optimal_level_config(target_moves, target_score)
        print(level_config.board)
        print(f"实际步数: {moves}, 实际分数: {score}")
        
    
    
    