import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt



# 定义CNN模型
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        
        # 卷积层
        self.conv1 = nn.Conv2d(1, 3, kernel_size=3, padding=1)
        
        # 全连接层
        self.fc1 = nn.Linear(3*8*8, 1)  # 3个类别
        
    def forward(self, x):
        # 卷积层
        x = torch.relu(self.conv1(x))
        # 展平
        x = x.view(x.size(0), -1)
        # 全连接层
        x = self.fc1(x)
        
        return x

# 创建模型
model = SimpleCNN()


# 地图→难度   简化案例
x = torch.tensor([[[
    [0,0,0,0,0,0,0,0],  
    [0,1,1,1,1,1,1,0],  
    [0,1,2,2,2,2,1,0],  
    [0,1,2,3,3,2,1,0],  
    [0,1,2,3,3,2,1,0],  
    [0,1,2,2,2,2,1,0],  
    [0,1,1,1,1,1,1,0],  
    [0,0,0,0,0,0,0,0]   
]]], dtype=torch.float32)

"""
x = torch.tensor([[[
    [0,1,2,3,4,3,4,0],  # 第一行：棕色，红心，绿色，紫色，蓝色，紫色，蓝色，棕色
    [0,1,4,3,2,3,1,0],  # 第二行：棕色，红心，蓝色，紫色，绿色，紫色，红心，棕色
    [2,4,3,2,3,3,2,3],  # 第三行：绿色，蓝色，紫色，绿色，紫色，紫色，绿色，紫色
    [3,1,3,3,2,3,3,2],  # 第四行：紫色，红心，紫色，紫色，绿色，紫色，紫色，绿色
    [2,3,2,3,4,3,4,1],  # 第五行：绿色，紫色，绿色，紫色，蓝色，紫色，蓝色，红心
    [1,4,3,2,3,2,3,3],  # 第六行：红心，蓝色，紫色，绿色，紫色，绿色，紫色，紫色
    [0,3,4,3,2,3,1,0],  # 第七行：棕色，紫色，蓝色，紫色，绿色，紫色，红心，棕色
    [0,2,3,4,3,2,1,0]   # 第八行：棕色，绿色，紫色，蓝色，紫色，绿色，红心，棕色
]]], dtype=torch.float32)
"""


y = model(x)
print(y)





