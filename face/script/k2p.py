import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from normalize_facial_keypoints import FacialKeypointNormalizer
import time
from simulator import Simulator
class KeypointsToParamsDataset(Dataset):
    """关键点到参数的数据集类"""
    
    def __init__(self, data_folder, split='train'):
        self.data_folder = Path(data_folder) / split
        self.normalizer = FacialKeypointNormalizer()
        self.param_names = ['headWidth', 'headHeight', 'noseWidth', 'noseLength', 'eyeLength', 'eyeWidth', 'mouthSize']
        self.data = []
        self.load_data()
    
    def load_data(self):
        json_files = list(self.data_folder.glob('*.json'))
        print(f"找到 {len(json_files)} 个JSON文件")
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            landmarks = data.get('landmarks', [])
            keypoints = np.array([[point['x'], point['y']] for point in landmarks])
            normalized_keypoints = self.normalizer.normalize_keypoints(keypoints)
            
            params_data = data.get('data', {})
            params = [params_data.get(name, 0) / 100.0 for name in self.param_names] #归一化到-1到1
            
            self.data.append({
                'keypoints': normalized_keypoints.flatten(),
                'params': np.array(params, dtype=np.float32)
            })
        
        print(f"成功加载 {len(self.data)} 个样本")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = self.data[idx]
        return torch.FloatTensor(sample['keypoints']), torch.FloatTensor(sample['params'])

class KeypointsToParamsNet(nn.Module):
    """关键点到参数的神经网络模型"""
    
    def __init__(self):
        super().__init__()
        # 简化网络结构，减少层数和参数
        self.network = nn.Sequential(
            nn.Linear(22, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 7),
        )
    
    def forward(self, x):
        return self.network(x) 

class KeypointsToParamsTrainer:
    """训练器类"""
    
    def __init__(self, data_folder, model_save_path='models/k2p_model.pth'):
        self.model_save_path = model_save_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 加载数据
        self.train_dataset = KeypointsToParamsDataset(data_folder, 'train')
        self.test_dataset = KeypointsToParamsDataset(data_folder, 'test')
        
        self.train_loader = DataLoader(self.train_dataset, batch_size=32, shuffle=True)
        self.test_loader = DataLoader(self.test_dataset, batch_size=32, shuffle=False)
        
        # 创建模型
        self.model = KeypointsToParamsNet().to(self.device)
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        self.train_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        
        print(f"训练设备: {self.device}")
        print(f"训练样本: {len(self.train_dataset)}, 测试样本: {len(self.test_dataset)}")
    
    def train_epoch(self):
        self.model.train()
        total_loss = 0.0
        
        for keypoints, params in self.train_loader:
            keypoints, params = keypoints.to(self.device), params.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(keypoints)
            loss = self.criterion(outputs, params)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(self.train_loader)
    
    def validate(self):
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for keypoints, params in self.test_loader:
                keypoints, params = keypoints.to(self.device), params.to(self.device)
                outputs = self.model(keypoints)
                loss = self.criterion(outputs, params)
                total_loss += loss.item()
        
        return total_loss / len(self.test_loader)
    
    def train(self, epochs=100):
        print(f"开始训练，共 {epochs} 个epoch")
        
        for epoch in range(epochs):
            train_loss = self.train_epoch()
            val_loss = self.validate()
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.save_model()
                print(f"Epoch {epoch+1}: Train={train_loss:.6f}, Val={val_loss:.6f} (Best)")
            elif (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}: Train={train_loss:.6f}, Val={val_loss:.6f}")
        
        print(f"训练完成！最佳验证损失: {self.best_val_loss:.6f}")
    
    def save_model(self):
        torch.save(self.model.state_dict(), self.model_save_path)
    
    def plot_training_history(self):
        plt.figure(figsize=(10, 4))
        plt.plot(self.train_losses, label='Training Loss')
        plt.plot(self.val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training History')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def evaluate_model(self):
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for keypoints, params in self.test_loader:
                keypoints = keypoints.to(self.device)
                outputs = self.model(keypoints)
                all_predictions.append(outputs.cpu().numpy())
                all_targets.append(params.numpy())
        
        predictions = np.vstack(all_predictions)
        targets = np.vstack(all_targets)
        
        mse = mean_squared_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        mae = np.mean(np.abs(targets - predictions))
        
        print(f"\n模型评估结果:")
        print(f"MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")
        
        print(f"\n各参数详细分析:")
        for i, param_name in enumerate(self.train_dataset.param_names):
            param_mae = np.mean(np.abs(targets[:, i] - predictions[:, i]))
            param_r2 = r2_score(targets[:, i], predictions[:, i])
            print(f"{param_name:12}: MAE={param_mae:6.2f}, R²={param_r2:6.3f}")

class KeypointsToParamsPredictor:
    """预测器类"""
    
    def __init__(self, model_path='models/k2p_model.pth'):
        self.param_names = ['headWidth', 'headHeight', 'noseWidth', 'noseLength', 'eyeLength', 'eyeWidth', 'mouthSize']
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.normalizer = FacialKeypointNormalizer()
        self.load_model(model_path)
    
    def load_model(self, model_path):
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model = KeypointsToParamsNet().to(self.device)
        self.model.load_state_dict(checkpoint)
        self.model.eval()
        print(f"模型已加载")
    
    def predict_from_landmarks(self, landmarks_list):
        """从关键点预测参数"""
        keypoints = np.array([[point['x'], point['y']] for point in landmarks_list])
        normalized_keypoints = self.normalizer.normalize_keypoints(keypoints)
        keypoints_tensor = torch.FloatTensor(normalized_keypoints.flatten()).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            predictions = self.model(keypoints_tensor).cpu().numpy()[0]
        return {name: int(round(pred*100)) for name, pred in zip(self.param_names, predictions)}
    
def main():
    # 设置路径
    data_folder = "E:/B9/face/Dataset/"
    model_save_path = "models/k2p_model.pth"
    
    print("=== 训练模型 ===")
    #trainer = KeypointsToParamsTrainer(data_folder, model_save_path)
    #trainer.train(epochs=400)
    #trainer.plot_training_history()
    #trainer.evaluate_model()
    

    
    print("\n=== 测试预测 ===")
    predictor = KeypointsToParamsPredictor(model_save_path)
    
    # 测试预测
    with open("E:/B9/face/Dataset/test/sample_0181.json", 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    test_keypoints = test_data.get('landmarks', [])
    test_params = [test_data.get('data', {}).get(name, 0) for name in predictor.param_names]
    predicted_params = predictor.predict_from_landmarks(test_keypoints)
    
    print(f"真实参数: {dict(zip(predictor.param_names, test_params))}")
    print(f"预测参数: {predicted_params}")

    #看图像结果
    simulator = Simulator()
    simulator.get_landmarks(predicted_params)

if __name__ == "__main__":
    main()
