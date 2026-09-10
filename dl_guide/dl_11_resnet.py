import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
import numpy as np
import matplotlib.pyplot as plt

# 定义使用预训练ResNet的模型
class ResNetModel(nn.Module):
    def __init__(self):
        super(ResNetModel, self).__init__()
        
        # 使用预训练的ResNet18
        self.resnet = models.resnet18(pretrained=False)
        # 修改最后的全连接层
        # print(f"原先fc层的维度: {self.resnet.fc}")
        # print(f"输入特征数: {self.resnet.fc.in_features}")
        # print(f"输出特征数: {self.resnet.fc.out_features}")
        
        self.resnet.fc = nn.Linear(512, 1)
        
    def forward(self, x):
        return self.resnet(x)

# 创建模型
x = torch.randn(1, 3, 224, 224)
model = ResNetModel()
y = model(x)
print(y)
