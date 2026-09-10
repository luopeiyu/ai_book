"""
队伍战力评估系统
基于监督学习的回归模型，预测队伍的战力值
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import json
import random
import matplotlib.pyplot as plt
from http_client import BattleSimulatorClient
import time
from collections import defaultdict
import os
from team_ppo_4 import TeamSelectionPredictor
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import random
from torch.utils.data import WeightedRandomSampler
# 常量定义
HERO_POOL = list(range(40))   # 0-39 共40个英雄
SKILL_POOL = list(range(18))  # 0-17 共18个技能
TEAM_SIZE = 3  # 每队3个英雄

@dataclass
class TeamScoreData:
    """阵容得分数据样本"""
    team_config: List[Tuple[int, int]]  # 队伍配置
    score: float                     # 得分值
    win_count: int                     # 胜利次数
    battles_count: int                  # 对战次数

    def __eq__(self, other):
        return self.team_config == other.team_config

class TeamEncoder:
    """队伍编码器"""
    
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
    
class ScoreNet(nn.Module):
    """阵容得分评估神经网络"""
    
    def __init__(self):
        super(ScoreNet, self).__init__()
        
        prev_dim = 174 # 特征维度
        hidden_dims: List[int] = [256, 128, 64]
        layers = []

        # 构建隐藏层
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.BatchNorm1d(hidden_dim)
            ])
            prev_dim = hidden_dim
        
        # 输出层
        layers.append(nn.Linear(prev_dim, 1))
        
        self.network = nn.Sequential(*layers)
        
    def forward(self, x):
        return self.network(x)

class ELOScoreDataSetGenerator:
    """ELO得分数据生成器"""
    
    def __init__(self, client: BattleSimulatorClient):
        self.client = client
        self.encoder = TeamEncoder()
        self.teams = [] # 队伍ELO评级
        self.predictor = TeamSelectionPredictor(model_path="./models/ppo_team_selection_4")
        
    def generate_random_team(self) -> TeamScoreData:
        heroes = random.sample(HERO_POOL, TEAM_SIZE)
        skills = [random.choice(SKILL_POOL) for _ in range(TEAM_SIZE)]
        team_config = list(zip(heroes, skills))
        return TeamScoreData(team_config=team_config, score=1500, win_count=0, battles_count=0)

    def generate_unique_teams(self, count: int) -> List[TeamScoreData]:
        teams = []
        ATTEMPTS = count*3
        attempts = 0
        while len(teams) < count and attempts < ATTEMPTS:
            team = self.generate_random_team()
            if team not in teams:
                teams.append(team)
            attempts += 1
        return teams

    def update_elo_score(self, team1_idx_list,team2_idx_list):
        # 批量模拟战斗
        team1_list = []
        team2_list = []
        for i in range(len(team1_idx_list)):
            team1_list.append(self.teams[team1_idx_list[i]].team_config)
            team2_list.append(self.teams[team2_idx_list[i]].team_config)
        
        results = self.client.simulate_batch_battles_bidirection(team1_list, team2_list)
        
        for i in range(len(results)):
            team1_idx = team1_idx_list[i]
            team1 = self.teams[team1_idx]
            team1_results = results[i] # len(results) = battles_per_round
            
            # 计算双向战斗的总次数
            for j in range(0, len(team1_results), 2): # len(team1_results) = 2*battles_per_round
                team2_idx = team2_idx_list[j//2]            
                team2 = self.teams[team2_idx]
                
                # team1 vs team2 的两次结果
                bidirection_results = []
                bidirection_results.append(team1_results[j//2])
                bidirection_results.append(team1_results[j//2+1])
                team1_win_count = 0
                for battle_result in bidirection_results:
                    if battle_result['winner'] == 'team1_win':
                        team1_win_count += 1
                    elif battle_result['winner'] == 'draw':
                        team1_win_count += 0.5
                          
                # 根据胜负更新属性
                team1.battles_count += 1
                team2.battles_count += 1
                
                # ELO计算
                K = 32  # K因子，决定评分变化幅度
                expected_score_team1 = 1 / (1 + 10**((team2.score - team1.score) / 400))
                expected_score_team2 = 1 - expected_score_team1
                
                actual_score_team1 = team1_win_count / 2.0  # 归一化到[0,1]
                actual_score_team2 = 1 - actual_score_team1
                
                # 更新ELO评分
                team1.score += K * (actual_score_team1 - expected_score_team1)
                team2.score += K * (actual_score_team2 - expected_score_team2)
                
                # 更新胜场统计
                if team1_win_count > 1:
                    team1.win_count += 1
                elif team1_win_count == 1:
                    team1.win_count += 0.5
                    team2.win_count += 0.5
                else:
                    team2.win_count += 1
                    
    def generate_teams_from_elite_py_ppo(self, elite_teams: List[TeamScoreData]) -> List[TeamScoreData]:
        """使用PPO模型生成队伍"""
        teams = []
        for coach_team in elite_teams:
            MAX_ATTEMPTS = 5 # 最大尝试次数
            for _ in range(MAX_ATTEMPTS):
                isok, new_team_config = self.predictor.predict(coach_team.team_config)
                if isok :
                    new_team = TeamScoreData(team_config=new_team_config, score=1500, win_count=0, battles_count=0)
                    if new_team not in self.teams: # 避免重复
                        teams.append(new_team)
                        break
        return teams

            
    def generate_elo_dataset(self, init_count: int = 1000, rounds: int = 50000, 
                             battles_per_round: int = 100,add_team_num_per_round: int = 30) -> List[TeamScoreData]:
        """
        生成ELO得分数据集
        """
        # 随机生成count个不重复队伍
        self.teams = self.generate_unique_teams(init_count)
        
        # 进行多轮循环比赛
        for round_num in range(rounds):
            print(f"进行第{round_num+1}/{ rounds}轮比赛, 当前队伍数量: {len(self.teams)}")
            # 随机选择N个队伍进行对战

            team1_idx_list = random.choices(range(len(self.teams)), k=battles_per_round)
            team2_idx_list = random.choices(range(len(self.teams)), k=battles_per_round)    
            
            # 更新队伍ELO得分
            self.update_elo_score(team1_idx_list, team2_idx_list)
            
            # 选取最强的N支队伍
            sorted_teams = sorted(self.teams, key=lambda x: x.score, reverse=True)
            coach_teams = sorted_teams[:add_team_num_per_round]
            new_teams = self.generate_teams_from_elite_py_ppo(coach_teams)
            self.teams.extend(new_teams)
             
        # 删除没有战斗次数的队伍
        self.teams = [team for team in self.teams if team.battles_count > 0]
        print(f"删除未战斗队伍，最终队伍数量: {len(self.teams)}")
        return self.teams
        
    def show_score_histogram(self):
        """显示teams中score的直方图"""
        scores = [team.score for team in self.teams]
        plt.hist(scores, bins=20, edgecolor='black')
        plt.show()  
    
    def save_dataset(self, path: str):
        """保存数据集"""
        data_to_save = []
        for team in self.teams:
            team_dict = {
                'team_config': team.team_config,
                'score': team.score,
                'win_count': team.win_count,
                'battles_count': team.battles_count
            }
            data_to_save.append(team_dict)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False)
    
    def load_dataset(self, path: str) -> List[TeamScoreData]:
        """加载数据集"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.teams = []
            for team_dict in data:
                team = TeamScoreData(
                    team_config=team_dict['team_config'],
                    score=team_dict['score'],
                    win_count=team_dict['win_count'],
                    battles_count=team_dict['battles_count']
                )
                self.teams.append(team)
        return self.teams
    
    
class TeamScoreDataset(Dataset):
    """队伍得分数据集"""
    
    def __init__(self, teams: List[TeamScoreData]):
        self.teams = teams
        self.encoder = TeamEncoder()
        
    
    def __len__(self):
        return len(self.teams)
    
    def __getitem__(self, idx):
        team = self.teams[idx]
        x = self.encoder.encode_team(team.team_config)
        y = (team.score-1500)/1000 # 简单的归一化使得有较多数值落在 [-1,1] 区间
        return torch.FloatTensor(x), torch.FloatTensor([y])




class WeightedTeamScoreDataset(Dataset):
    """加权队伍得分数据集"""
    
    def __init__(self, teams: List[TeamScoreData]):
        self.teams = teams
        self.encoder = TeamEncoder()
        scores = [team.score for team in teams]
        self.mean_score = np.mean(scores)
        self.std_score = np.std(scores)
        self.weights = []
        # 计算分数分布，创建直方图bins
        scores = [team.score for team in teams]
        hist, bin_edges = np.histogram(scores, bins=200)
        
        # 为每个队伍计算权重，使直方图尽可能平坦
        for team in teams:
            # 找到该队伍得分所在的bin
            bin_idx = np.digitize(team.score, bin_edges) - 1
            bin_idx = max(0, min(bin_idx, len(hist) - 1))  # 确保索引在有效范围内
            
            # 计算权重：bin中样本越多，权重越小
            bin_count = hist[bin_idx]
            if bin_count > 0:
                weight = 1.0 / bin_count
            else:
                weight = 1.0
            self.weights.append(weight)
        
        # 归一化权重，使平均权重为1
        avg_weight = np.mean(self.weights)
        self.weights = [w / avg_weight for w in self.weights]

    
    def __len__(self):
        return len(self.teams)
    
    def __getitem__(self, idx):
        team = self.teams[idx]
        weight = self.weights[idx]
        x = self.encoder.encode_team(team.team_config)
        y = (team.score-self.mean_score)/self.std_score # 归一化使得有较多数值落在 [-1,1] 区间
        return torch.FloatTensor(x), torch.FloatTensor([y]), torch.FloatTensor([weight])

    def show_score_histogram(self):
        scores = []
        weights = []
        for i in range(len(self.teams)):
            team = self.teams[i]
            scores.append(team.score)
            weights.append(self.weights[i])
        
        plt.hist(scores, bins=20, weights=weights, edgecolor='black')
        plt.show()
        
class TeamScoreTrainer:
    """队伍得分训练器"""
    
    def __init__(self, train_teams: List[TeamScoreData], valid_teams: List[TeamScoreData], log_dir: str = "./logs/team_score"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ScoreNet().to(self.device)
        self.train_dataset = WeightedTeamScoreDataset(train_teams)
        self.valid_dataset = TeamScoreDataset(valid_teams)
        self.train_dataset.show_score_histogram()

        self.train_loader = DataLoader(self.train_dataset, batch_size=64, shuffle=False)
        self.valid_loader = DataLoader(self.valid_dataset, batch_size=64, shuffle=False)
        
        # 损失函数和优化器
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # TensorBoard记录器，自动生成时间戳目录
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        full_log_dir = f"{log_dir}_{timestamp}"
        self.writer = SummaryWriter(full_log_dir)
        
        # 训练历史记录
        self.best_val_loss = float('inf')
        
        print(f"训练设备: {self.device}")
        print(f"训练样本数: {len(self.train_dataset)}")
        print(f"验证样本数: {len(self.valid_dataset)}")

    def weighted_mse_loss(self, outputs, targets, weights):
        """加权MSE损失函数"""
        diff = outputs - targets
        weighted_squared_diff = weights * diff ** 2
        return torch.mean(weighted_squared_diff)
    
    def train_epoch(self):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, (x, y, weights) in enumerate(self.train_loader):
            x, y, weights = x.to(self.device), y.to(self.device), weights.to(self.device)
            self.optimizer.zero_grad()
            outputs = self.model(x)
            # 确保输出维度一致
            loss = self.weighted_mse_loss(outputs, y, weights)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        return total_loss / len(self.train_loader)
    
    def validate(self):
        """验证模型"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for x, y in self.valid_loader:
                x, y = x.to(self.device), y.to(self.device)
                outputs = self.model(x)
                loss = self.criterion(outputs, y)
                total_loss += loss.item()

        val_loss = total_loss / len(self.valid_loader)
        
        return val_loss
    
    def train(self, epochs: int = 200, save_path: str = "./models/team_score_model_2.pth"):
        """训练模型"""
        print(f"开始训练，共 {epochs} 个epoch")
        
        
        for epoch in range(epochs):
            # 训练
            train_loss = self.train_epoch()
            
            # 验证
            val_loss = self.validate()
            
            # TensorBoard记录
            self.writer.add_scalar('Loss/Train', train_loss, epoch)
            self.writer.add_scalar('Loss/Validation', val_loss, epoch)
            
            # 保存最佳模型
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                torch.save(self.model.state_dict(), save_path)
                print(f"Epoch {epoch+1}: 训练损失={train_loss:.6f}, 验证损失={val_loss:.6f} (最佳)")
            elif (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}: 训练损失={train_loss:.6f}, 验证损失={val_loss:.6f}")
        
        print(f"训练完成！最佳验证损失: {self.best_val_loss:.6f}")
        print(f"模型已保存到: {save_path}")
        
        # 关闭TensorBoard写入器
        self.writer.close()
    
class TeamScorePredictor:
    """队伍得分预测器"""
    
    def __init__(self, model_path: str):
        self.model = ScoreNet()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        self.encoder = TeamEncoder()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def predict(self, team_config: List[Tuple[int, int]]) -> float:
        """预测队伍得分"""
        x = self.encoder.encode_team(team_config)
        with torch.no_grad():
            output = self.model(torch.FloatTensor(x).unsqueeze(0).to(self.device))
            return output.item()

def evaluate_with_battle(predictor: TeamScorePredictor, client: BattleSimulatorClient, test_teams: List[List[Tuple[int, int]]]):
    """使用已知队伍验证评估器准确性"""
    # 先预测每支队伍的得分
    scores = []
    for team in test_teams:
        scores.append(predictor.predict(team.team_config))
    print("队伍得分预测结果:")
    for i, (team, score) in enumerate(zip(test_teams, scores)):
        print(f"    队伍{i+1}: {team.team_config} -> 得分: {score:.5f}")
        
    # 两两对打，验证如果A胜B，则A的得分是否大于B

    print("")
    print("两两对战验证结果:")
    print("队伍对比\t\t预测得分\t\t实际战斗结果\t预测胜场\t预测是否正确")
    
    correct_predictions = 0
    total_battles = 0
    diff_01_count = 0
    diff_01_correct_count = 0
    
    for i in range(len(test_teams)):
        for j in range(i+1, len(test_teams)):

            # 实际战斗
            team1 = test_teams[i].team_config
            team2 = test_teams[j].team_config
            battle_results = client.simulate_single_battle_bidirection(team1, team2)
            
            # 计算真实胜场
            team1_win_count = 0 # [0, 1, 2]
            for battle_result in battle_results:
                if battle_result.get('winner') == 'team1_win':
                    team1_win_count += 1
                elif battle_result.get('winner') == 'draw':
                    team1_win_count += 0.5
            
            # 计算预测胜场
            predicted_team1_win = 1
            if scores[i] > scores[j]:
                predicted_team1_win = 2
            elif scores[i] < scores[j]:
                predicted_team1_win = 0
            
            # 判断准确率
            is_correct = predicted_team1_win == team1_win_count
            # 统计
            if is_correct:
                correct_predictions += 1
            total_battles += 1
            
            if abs(scores[i] - scores[j]) > 0.1:
                diff_01_count += 1
                if is_correct:
                    diff_01_correct_count += 1
            
            # 打印
            print(f"队伍{i+1} vs 队伍{j+1}\t\t{scores[i]:.5f} vs {scores[j]:.5f}\t\t{team1_win_count}\t{predicted_team1_win}\t{is_correct}")
            


    # 计算准确率
    if total_battles > 0:
        print(f"预测准确率: {correct_predictions}/{total_battles}")
        print(f"预测差大于0.1的准确率: {diff_01_correct_count}/{diff_01_count}")
    else:
        print("无有效对战结果")
    



def main():
    """主函数 - 战力评估系统演示"""
    print("初始化战力评估系统...")
    
    # 创建客户端
    client = BattleSimulatorClient()
    
    # 测试连接
    try:
        health = client.health_check()
        print(f"服务状态: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"无法连接到战斗模拟器API: {e}")
        return
    
    # 创建数据生成器
    data_generator = ELOScoreDataSetGenerator(client)
    #data_generator.generate_elo_dataset(init_count=200, rounds=1000, battles_per_round=30,add_team_num_per_round=20)
    #data_generator.generate_elo_dataset(init_count=50, rounds=1, battles_per_round=10, add_team_num_per_round=10)
    #data_generator.save_dataset("./elo_score_dataset.json")
    data_generator.load_dataset("./elo_score_dataset.json")
    
    #data_generator.show_score_histogram()
    teams = data_generator.teams
    # 随机划分训练集、验证集和测试集
    teams_shuffled = teams.copy()
    random.seed(42)
    random.shuffle(teams_shuffled)
    
    total_teams = len(teams_shuffled)
    train_end = int(total_teams * 0.8)
    valid_end = int(total_teams * 0.9)
    
    train_teams = teams_shuffled[:train_end]
    valid_teams = teams_shuffled[train_end:valid_end]
    test_teams = teams_shuffled[valid_end:]
    print("训练集:",len(train_teams), "验证集:",len(valid_teams), "测试集:",len(test_teams))
    # 训练
    trainer = TeamScoreTrainer(train_teams, valid_teams)
    trainer.train(epochs=500, save_path="./models/team_score_model_2.pth")
    
    # 评估
    predictor = TeamScorePredictor(model_path="./models/team_score_model_2.pth")
    evaluate_with_battle(predictor, client, test_teams[:10])

if __name__ == "__main__":
    main()
