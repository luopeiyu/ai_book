import torch
import torch.nn as nn
import numpy as np
import torch.optim as optim
class SimpleMLP(nn.Module):
    def __init__(self):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(1, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 1)
        self.relu1 = nn.ReLU()
        self.relu2 = nn.ReLU()
    
    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x
    
x = torch.tensor([[1.0], [2.0], [3.0], [4.0], [5.0]])
y = torch.tensor([[100.0], [200.0], [300.0], [400.0], [500.0]])

model = SimpleMLP()

optimizer = optim.Adam(model.parameters(), lr=0.01)
criterion = nn.MSELoss()
for epoch in range(500):
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
    
torch.save(model.state_dict(), "models/dl_5_model.pth")



