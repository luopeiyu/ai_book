import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models


class HairTypeDataset(Dataset):
    """头发类型数据集类"""
    
    def __init__(self, data_folder, split='train'):
        self.data_folder = Path(data_folder) / split
        self.data = []
        self.class_weights = None
        self.split = split
        self.load_data()

    
    def load_data(self):
        """加载所有图片和对应的头发类型标签"""
        jpg_files = list(self.data_folder.glob('*.jpg'))
        print(f"找到 {len(jpg_files)} 个图片文件")
        
        for jpg_file in jpg_files:
            json_file = jpg_file.with_suffix('.json')
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                hair_type = data.get('hair_type', '1')
                self.data.append({
                    'image_path': jpg_file,
                    'hair_type': hair_type
                })
        
        # 统计类别分布
        self.analyze_class_distribution()
    
    def analyze_class_distribution(self):
        """分析类别分布"""
        class_counts = [0,0,0,0,0]
        for sample in self.data:
            class_counts[int(sample['hair_type'])-1] += 1
        total_samples = len(self.data)
        for i, count in enumerate(class_counts):
            print(f"  类型 {i+1}: {count} 张图片")
        
        # 计算权重（样本数的倒数）
        weights = []
        for i in range(5):  # 5个类别
            count = class_counts[i] if class_counts[i] > 0 else 1  # 避免除零
            weight = total_samples / count 
            weights.append(weight)
        self.class_weights = torch.FloatTensor(weights)

        print(f"类别权重: {self.class_weights}")

        

    
    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        
        # 加载图片
        image = Image.open(sample['image_path']).convert('RGB')
        
        # 数据增强 - 训练时使用更强的增强
        if self.split == 'train':
            transform = transforms.Compose([
                transforms.Resize((224, 224)),  # ResNet需要224x224输入
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=10),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # ImageNet标准化
            ])
        else:
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        image = transform(image)
        
        # 获取标签 (1-5 转换为 0-4)
        hair_type = int(sample['hair_type']) 
        label = hair_type - 1
        
        return image, torch.tensor(label)

class ResNetHairClassifier(nn.Module):
    """基于ResNet的头发分类模型"""
    
    def __init__(self, num_classes=5, pretrained=True):
        super().__init__()
        
        # 使用ResNet18作为骨干网络，下载目录设置为models目录
        self.backbone = models.resnet18(pretrained=pretrained)
        
        # 获取ResNet最后一层的输入特征数
        num_features = self.backbone.fc.in_features
        
        # 替换最后的分类层
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
        
        # 冻结前面的层，只训练后面几层
        self.freeze_early_layers()
    
    def freeze_early_layers(self):
        """冻结除fc层外的所有层，只训练fc层"""
        # 冻结除fc层外的所有参数
        for name, param in self.backbone.named_parameters():
            if 'fc' not in name:
                param.requires_grad = False
            else:
                param.requires_grad = True
        
        print("已冻结除fc层外的所有层，只训练fc层")
        
        # 打印可训练参数数量
        trainable_params = sum(p.numel() for p in self.backbone.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.backbone.parameters())
        print(f"可训练参数: {trainable_params:,} / 总参数: {total_params:,} ({trainable_params/total_params*100:.1f}%)")
    
    def forward(self, x):
        return self.backbone(x)

class HairClassifierTrainer:
    """头发分类器训练器"""
    
    def __init__(self, data_folder, model_save_path='models/hair_classifier_resnet.pth'):
        self.model_save_path = model_save_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"训练设备: {self.device}")
        
        Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 加载数据集
        self.train_dataset = HairTypeDataset(data_folder, 'train')
        self.test_dataset = HairTypeDataset(data_folder, 'test')
        
        # 创建数据加载器
        self.train_loader = DataLoader(self.train_dataset, batch_size=16, shuffle=True)
        self.test_loader = DataLoader(self.test_dataset, batch_size=8, shuffle=False)
        
        # 创建ResNet模型
        self.model = ResNetHairClassifier(num_classes=5, pretrained=True).to(self.device)
        
        # 计算类别权重并创建加权损失函数
        class_weights = self.train_dataset.class_weights.to(self.device)
        self.criterion = nn.CrossEntropyLoss(weight=class_weights)
        
        # 只优化可训练的参数，使用较小的学习率
        trainable_params = [p for p in self.model.parameters() if p.requires_grad]
        #self.optimizer = optim.Adam(trainable_params, lr=0.001, weight_decay=1e-4)  # 稍大的学习率，因为只训练部分层
        #self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=30, gamma=0.5)
        self.optimizer = optim.Adam(trainable_params, lr=0.001)
        
        
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        self.best_val_acc = 0.0
    
    def train_epoch(self):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in self.train_loader:
            images, labels = images.to(self.device), labels.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        self.train_losses.append(total_loss / len(self.train_loader))
        self.train_accuracies.append(accuracy)
        return total_loss / len(self.train_loader), accuracy
    
    def validate(self):
        """验证模型"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in self.test_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        self.val_losses.append(total_loss / len(self.test_loader))
        self.val_accuracies.append(accuracy)
        return total_loss / len(self.test_loader), accuracy
    
    def train(self, epochs=100):
        """训练模型"""
        print(f"开始训练，共 {epochs} 个epoch")
        
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch()
            val_loss, val_acc = self.validate()
            #self.scheduler.step()
            self.optimizer.step()
            
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.save_model()
                print(f"Epoch {epoch+1}: Train Loss={train_loss:.4f}, Train Acc={train_acc:.2f}%, "
                      f"Val Loss={val_loss:.4f}, Val Acc={val_acc:.2f}% (Best)")
            elif (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}: Train Loss={train_loss:.4f}, Train Acc={train_acc:.2f}%, "
                      f"Val Loss={val_loss:.4f}, Val Acc={val_acc:.2f}%")
        
        print(f"训练完成！最佳验证准确率: {self.best_val_acc:.2f}%")
    
    def save_model(self):
        """保存模型"""
        torch.save(self.model.state_dict(), self.model_save_path)
    
    def evaluate_model(self):
        """详细评估模型"""
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for images, labels in self.test_loader:
                images = images.to(self.device)
                outputs = self.model(images)
                _, predicted = torch.max(outputs, 1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(labels.numpy())
        
        # 计算总体准确率
        accuracy = accuracy_score(all_targets, all_predictions)
        print(f"\n模型评估结果:")
        print(f"测试准确率: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # 按类别统计准确率
        class_correct = [0] * 5
        class_total = [0] * 5
        
        for pred, target in zip(all_predictions, all_targets):
            class_correct[target] += (pred == target)
            class_total[target] += 1
        
        print("\n各类别准确率:")
        for i in range(5):
            if class_total[i] > 0:
                acc = 100 * class_correct[i] / class_total[i]
                print(f"  类型 {i+1}: {acc:.1f}% ({class_correct[i]}/{class_total[i]})")
                
    def plot_training_history(self):
        """绘制训练历史"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # 损失曲线
        ax1.plot(self.train_losses, label='Training Loss')
        ax1.plot(self.val_losses, label='Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.legend()
        ax1.grid(True)
        
        # 准确率曲线
        ax2.plot(self.train_accuracies, label='Training Accuracy')
        ax2.plot(self.val_accuracies, label='Validation Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.set_title('Training and Validation Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()

class HairClassifierPredictor:
    """头发分类预测器"""
    
    def __init__(self, model_path='models/hair_classifier_resnet.pth'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.load_model(model_path)
    
    def load_model(self, model_path):
        """加载训练好的模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        self.model = ResNetHairClassifier(num_classes=5, pretrained=False).to(self.device)
        self.model.load_state_dict(checkpoint)
        self.model.eval()
        
        print(f"ResNet模型已加载")
    
    def predict_from_image(self, image_path):
        """从图片预测头发类型"""
        # 加载并预处理图片
        image = Image.open(image_path).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # 预测
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            print(f"概率: {probabilities}")
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class = predicted.item() + 1
        confidence_score = confidence.item() 

        
        return predicted_class, confidence_score

def main():
    """主函数"""
    # 设置路径
    data_folder = "E:/B9/face/style_dataset/filtered_faces"
    model_save_path = "models/hair_classifier_resnet.pth"
    
    print("=== 使用ResNet预训练模型训练头发分类器 ===")
    
    # 创建训练器并训练
    trainer = HairClassifierTrainer(data_folder, model_save_path)
    trainer.train(epochs=100)
    trainer.evaluate_model()
    trainer.plot_training_history()
    
    # 测试预测
    predictor = HairClassifierPredictor(model_path=model_save_path)
    test_image = "E:/B9/face/style_dataset/filtered_faces/test/realface (195).jpg"
    predicted_class, confidence = predictor.predict_from_image(test_image)
    print("预测类型：",predicted_class, "置信度：", confidence)  

if __name__ == "__main__":
    main()
