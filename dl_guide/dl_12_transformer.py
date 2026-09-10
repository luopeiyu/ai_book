import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt

# 定义使用Transformer的模型
class TransformerModel(nn.Module):
    def __init__(self):
        super(TransformerModel, self).__init__()
        
        # 使用PyTorch内置的TransformerEncoder，设置batch_first=True以获得更好的性能
        encoder_layer = nn.TransformerEncoderLayer(d_model=64, nhead=8, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        # 输出层
        self.fc = nn.Linear(64, 1)
        
    def forward(self, x):
        # x shape: (batch_size, seq_len, d_model)
        x = self.transformer(x)
        
        x = x.mean(dim=1)  # 平均池化
        x = self.fc(x)
        return x

# 创建模型
x = torch.randn(1, 10, 64)  # (batch_size, seq_len, d_model)
model = TransformerModel()
y = model(x)
print(y)
