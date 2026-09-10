import torch
import numpy as np


# 单个数值
scalar = torch.tensor(42.0)
print(scalar)

# 一维张量（向量）- 数组
vector = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
print(vector)

# 二维张量（矩阵）
matrix = torch.tensor([[1.0], [2.0], [3.0], [4.0], [5.0]])
print(matrix)


# 多维
tensor_3d = torch.tensor([[[1.0, 2.0], [3.0, 4.0]], 
                          [[5.0, 6.0], [7.0, 8.0]]])
print(tensor_3d)
print(tensor_3d.shape) # torch.Size([2, 2, 2])



# 游戏中的训练数据示例
x = torch.tensor([[1.0], [2.0], [3.0], [4.0], [5.0]])  # 玩家等级
y = torch.tensor([[100.0], [200.0], [300.0], [400.0], [500.0]])  # 对应战斗力

print(f"x的形状: {x.shape}")  # 输出: torch.Size([5, 1]) - 5个样本，每个样本1个特征
print(f"y的形状: {y.shape}")  # 输出: torch.Size([5, 1]) - 5个样本，每个样本1个目标值






