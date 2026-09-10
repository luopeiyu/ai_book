import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt



class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 3, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64*3, 1) 
        
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        
        return x


class SimpleLinear(nn.Module):
    def __init__(self):
        super(SimpleLinear, self).__init__()
        self.fc1 = nn.Linear(64, 64*3)
        self.fc2 = nn.Linear(64*3, 1)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)


# 创建模型
model = SimpleCNN()
linear_model = SimpleLinear()

# 统计CNN模型的参数
cnn_params = sum(p.numel() for p in model.parameters())
print(f"CNN模型参数数量: {cnn_params}")

# 统计线性模型的参数
linear_params = sum(p.numel() for p in linear_model.parameters())
print(f"线性模型参数数量: {linear_params}")

# 比较参数数量
print(f"参数数量差异: {abs(cnn_params - linear_params)}")


print("CNN模型各层参数详情:")
print(f"conv1.weight: {model.conv1.weight.numel()}")
print(f"conv1.bias: {model.conv1.bias.numel()}")
print(f"fc1.weight: {model.fc1.weight.numel()}")
print(f"fc1.bias: {model.fc1.bias.numel()}")

print("\n线性模型各层参数详情:")
print(f"fc1.weight: {linear_model.fc1.weight.numel()}")
print(f"fc1.bias: {linear_model.fc1.bias.numel()}")
print(f"fc2.weight: {linear_model.fc2.weight.numel()}")
print(f"fc2.bias: {linear_model.fc2.bias.numel()}")


