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
    

model = SimpleMLP()
model.load_state_dict(torch.load("models/dl_5_model.pth"))

x = torch.tensor([[10.0]])

outputs = model(x)  # [[994.6678]]
print(outputs.shape)
print(outputs[0].shape)
n = outputs[0].item() # 转为普通数值
print(n)





