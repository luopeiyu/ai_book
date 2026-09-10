import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os
import numpy as np
import matplotlib.pyplot as plt

class PlayerDataset(Dataset):
    """玩家数据集类"""
    
    def __init__(self, data_dir="player_data"):
        self.data_dir = data_dir
        self.players = []
        # 读取所有JSON文件
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                player_data = json.load(f)
                self.players.append(player_data)
        
        print(f"加载了 {len(self.players)} 个玩家数据")

        
    def __len__(self):
        return len(self.players)
    
    def __getitem__(self, idx):
        player = self.players[idx]
        # 输入：等级、攻击力、生命值、防御力、暴击率（5个特征）
        x = torch.tensor([
            player['level'], 
            player['attack'] , 
            player['hp'],
            player['defense'],  
            player['crit_rate'] 
        ], dtype=torch.float32)
        
        # 输出：战力
        y = torch.tensor([player['combat_power'] ], dtype=torch.float32)
        return x, y

class SimpleMLP(nn.Module):
    def __init__(self):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(5, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 1)
        self.relu1 = nn.ReLU()
        self.relu2 = nn.ReLU()
    
    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

train_dataset = PlayerDataset(data_dir="player_data_train")
train_dataloader = DataLoader(train_dataset, batch_size=10, shuffle=True)

test_dataset = PlayerDataset(data_dir="player_data_test")

model = SimpleMLP()

optimizer = optim.Adam(model.parameters(), lr=0.01)
criterion = nn.MSELoss()
for epoch in range(100):
    for x, y in train_dataloader:
        # 清空梯度
        optimizer.zero_grad()
        
        # 前向传播
        outputs = model(x)
        loss = criterion(outputs, y)
        
        # 反向传播
        loss.backward()
        print("epoch", epoch, "loss", loss.item())
        # 更新参数
        optimizer.step()

#验证
x0,y0 = test_dataset[0]
outputs = model(x0)
loss = criterion(outputs, y0)
print("x", x0, "y", y0, "outputs", outputs, "loss", loss.item())

x1,y1 = test_dataset[1]
outputs = model(x1)
loss = criterion(outputs, y1)
print("x", x1, "y", y1, "outputs", outputs, "loss", loss.item())

