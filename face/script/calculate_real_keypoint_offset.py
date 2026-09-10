import json
import numpy as np
from pathlib import Path
import cv2
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pickle
import os
from normalize_facial_keypoints import FacialKeypointNormalizer
from extract_facial_keypoints import FacialKeypointExtractor

class KeypointOffsetStatistics:
    def __init__(self):
        """
        计算真实人脸和动漫人脸关键点之间的偏移量和缩放关系
        """
        self.real_keypoints = []
        self.anime_keypoints = []
        self.offset_stats = []
    
    def extract_keypoints_from_json(self, json_path):
        """从JSON文件中提取关键点"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        landmarks = data.get('landmarks', [])
        if not landmarks:
            return None
        normalizer = FacialKeypointNormalizer()
        # 转换为numpy数组
        keypoints = np.array([[point['x'], point['y']] for point in landmarks])
        keypoints = normalizer.normalize_keypoints(keypoints)
        return keypoints
    
   
    def load_real_face_keypoints(self, real_faces_folder):
        """加载真实人脸的关键点数据"""
        real_path = Path(real_faces_folder)
        
        # 获取所有图片文件
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(list(real_path.glob(ext)))
        
        print(f"找到 {len(image_files)} 个真实人脸图片文件")
        
        # 创建关键点提取器
        extractor = FacialKeypointExtractor()
        normalizer = FacialKeypointNormalizer()
        for image_file in image_files:
            keypoints = extractor.extract_keypoints(str(image_file))
            
            keypoints = normalizer.normalize_keypoints(keypoints)
            self.real_keypoints.append(keypoints)
        
        print(f"成功加载 {len(self.real_keypoints)} 个真实人脸关键点")
    
    def load_anime_face_keypoints(self, anime_folder):
        """加载动漫人脸的关键点数据"""
        anime_path = Path(anime_folder)
        
        # 获取所有JSON文件
        json_files = list(anime_path.glob('*.json'))
        
        print(f"找到 {len(json_files)} 个动漫人脸描述文件")
        
        for json_file in json_files:
            keypoints = self.extract_keypoints_from_json(json_file)
            self.anime_keypoints.append(keypoints)
        
        print(f"成功加载 {len(self.anime_keypoints)} 个动漫人脸关键点")
    
    def calculate_point_statistics(self):
        """计算每个关键点的统计信息"""
        if not self.real_keypoints or not self.anime_keypoints:
            print("请先加载关键点数据")
            return
        
        # 转换为numpy数组
        real_points = np.array(self.real_keypoints)  # shape: (n_samples, n_points, 2)
        anime_points = np.array(self.anime_keypoints)
        
        n_points = real_points.shape[1]
        
        print(f"计算 {n_points} 个关键点的统计信息...")
        
        # 为每个关键点计算统计信息
        for point_idx in range(n_points):
            # 获取该点在所有样本中的坐标
            real_point_coords = real_points[:, point_idx, :]  # shape: (n_samples, 2)
            anime_point_coords = anime_points[:, point_idx, :]
            
            # 计算真实人脸和动漫人脸的统计信息
            real_center, real_std = self._calculate_point_center_and_std(real_point_coords)
            anime_center, anime_std = self._calculate_point_center_and_std(anime_point_coords)
            
            # 计算缩放因子
            scale_x, scale_y = self._calculate_scale_factors(real_std, anime_std)
            
            # 保存统计信息
            self.offset_stats.append({
                "real_center_x": real_center[0],
                "real_center_y": real_center[1],
                "anime_center_x": anime_center[0],
                "anime_center_y": anime_center[1],
                "scale_x": scale_x,
                "scale_y": scale_y,
            })
        
        #print(self.offset_stats)    
        print("统计信息计算完成")        
        
        return self.offset_stats
    
    def _remove_outliers_using_iqr(self, coords):
        """使用IQR方法剔除离奇点"""
        # 分别处理x和y坐标
        x_coords = coords[:, 0]
        y_coords = coords[:, 1]
        
        # 计算四分位数
        x_q1, x_q3 = np.percentile(x_coords, [25, 75])
        y_q1, y_q3 = np.percentile(y_coords, [25, 75])
        
        # 计算IQR
        x_iqr = x_q3 - x_q1
        y_iqr = y_q3 - y_q1
        
        # 定义离奇点边界
        x_lower = x_q1 - 1.5 * x_iqr
        x_upper = x_q3 + 1.5 * x_iqr
        y_lower = y_q1 - 1.5 * y_iqr
        y_upper = y_q3 + 1.5 * y_iqr
        
        # 筛选正常点
        valid_mask = (
            (x_coords >= x_lower) & (x_coords <= x_upper) &
            (y_coords >= y_lower) & (y_coords <= y_upper)
        )
        
        if np.sum(valid_mask) == 0:
            # 如果所有点都被认为是离奇点，则使用原始数据
            return coords
        else:
            return coords[valid_mask]
    
    def _calculate_point_center_and_std(self, point_coords):
        """计算关键点的中心位置和标准差"""
        # 剔除离奇点
        valid_coords = self._remove_outliers_using_iqr(point_coords)
        #print(f"剔除了 {len(point_coords) - len(valid_coords)} 个离奇点")
        # 计算统计信息
        center = np.mean(valid_coords, axis=0)
        std = np.std(valid_coords, axis=0)
        
        return center, std
    
    def _calculate_scale_factors(self, real_std, anime_std):
        """计算缩放因子"""
        # 使用标准差比例作为缩放因子，这比使用范围更稳定
        # 如果标准差为0，使用1作为默认缩放比例
        scale_x = anime_std[0] / real_std[0] if real_std[0] != 0 else 1.0
        scale_y = anime_std[1] / real_std[1] if real_std[1] != 0 else 1.0
        
        return scale_x, scale_y
    
    def visualize_offset_stats(self):
        """可视化偏移量统计信息"""
        if not self.offset_stats:
            print("请先计算偏移量统计信息")
            return
        
        # 用红点画anime各点的中心，用蓝点画real各点的中心，用箭头将对应蓝点指向红点
        plt.figure(figsize=(10, 10))
        
        # 绘制所有关键点
        for i in range(len(self.real_keypoints)):
            if i == 0:
                plt.scatter(self.real_keypoints[i][:, 0], self.real_keypoints[i][:, 1], color='blue', label='real', alpha=0.3)
            else:
                plt.scatter(self.real_keypoints[i][:, 0], self.real_keypoints[i][:, 1], color='blue', alpha=0.3)
        for i in range(len(self.anime_keypoints)):
            if i == 0:
                plt.scatter(self.anime_keypoints[i][:, 0], self.anime_keypoints[i][:, 1], color='red', label='anime', alpha=0.3)
            else:
                plt.scatter(self.anime_keypoints[i][:, 0], self.anime_keypoints[i][:, 1], color='red', alpha=0.3)
        
        # 绘制中心点和箭头
        for point_idx in range(len(self.offset_stats)):
            stats = self.offset_stats[point_idx]
            real_center = [stats['real_center_x'], stats['real_center_y']]
            anime_center = [stats['anime_center_x'], stats['anime_center_y']]
            
            # 绘制中心点
            plt.scatter(real_center[0], real_center[1], color='darkblue', s=100, marker='o')
            plt.scatter(anime_center[0], anime_center[1], color='darkred', s=100, marker='o')
            
            # 绘制箭头
            plt.arrow(real_center[0], real_center[1], 
                     anime_center[0] - real_center[0], 
                     anime_center[1] - real_center[1], 
                     color='green', head_width=0.02, head_length=0.02, fc='green', ec='green')
        
        plt.legend()
        plt.title('offset')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.gca().invert_yaxis()
        plt.grid(True, alpha=0.3)
        plt.show()
    

THE_OFFSET_STATS = [
    {'real_center_x': -0.7333500120471739, 'real_center_y': -0.28938934008542727, 'anime_center_x': -0.5405488302673283, 'anime_center_y': 0.05490061870493798, 'scale_x': 0.6064642517564064, 'scale_y': 0.36222144549731033},
    {'real_center_x': -0.5813279317619745, 'real_center_y': 0.6543830640350083, 'anime_center_x': -0.4524016433900894, 'anime_center_y': 0.36869598976537743, 'scale_x': 0.8499087990939319, 'scale_y': 0.9196836354691034},
    {'real_center_x': -0.0035682635066632937, 'real_center_y': 1.0353506333099367, 'anime_center_x': 0.0, 'anime_center_y': 0.7939097397463192, 'scale_x': 0.0, 'scale_y': 1.857642465778299},
    {'real_center_x': -0.5, 'real_center_y': -0.14970004963316716, 'anime_center_x': -0.5, 'anime_center_y': 0.018563717674759603, 'scale_x': 1.0, 'scale_y': 0.5761141205367994},
    {'real_center_x': -0.30737095636162076, 'real_center_y': -0.19729784837106917, 'anime_center_x': -0.32892947904138753, 'anime_center_y': -0.0639271825870348, 'scale_x': 4.171722418563079, 'scale_y': 1.0067507413763777},
    {'real_center_x': -0.19125523783601409, 'real_center_y': -0.11917677198600021, 'anime_center_x': -0.1937525310055903, 'anime_center_y': 0.06667275091951014, 'scale_x': 5.347274078316568, 'scale_y': 0.8666364296385198},
    {'real_center_x': -0.40327231677971925, 'real_center_y': -0.10473829895591301, 'anime_center_x': -0.4307511979685195, 'anime_center_y': 0.1358344488516776, 'scale_x': 1.943523112505884, 'scale_y': 1.2081114756345936},
    {'real_center_x': 0.0, 'real_center_y': 0.0, 'anime_center_x': 0.0, 'anime_center_y': 0.0, 'scale_x': 1.0, 'scale_y': 1.0},
    {'real_center_x': 0.0, 'real_center_y': 0.3701181635134175, 'anime_center_x': 0.0, 'anime_center_y': 0.22839138439922474, 'scale_x': 1.0, 'scale_y': 2.565625131049781},
    {'real_center_x': -0.30324032207998847, 'real_center_y': 0.5422945242898052, 'anime_center_x': -0.15219478691748808, 'anime_center_y': 0.503035102035332, 'scale_x': 1.0560599320605106, 'scale_y': 1.435096972196563},
    {'real_center_x': 0.0020966057459751684, 'real_center_y': 0.6303129600109214, 'anime_center_x': 0.0, 'anime_center_y': 0.5414662282865703, 'scale_x': 0.0, 'scale_y': 1.79576720523088}
]


    
def transform_real_to_anime(real_keypoints,offset_stats=THE_OFFSET_STATS):
    """
    将真实人脸关键点转换为动漫风格
    """
    transformed = real_keypoints.copy()
    for point_idx in range(len(real_keypoints)):
        stats = offset_stats[point_idx]
        transform_x = (real_keypoints[point_idx][0] - stats['real_center_x']) * stats['scale_x'] + stats['anime_center_x']
        transform_y = (real_keypoints[point_idx][1] - stats['real_center_y']) * stats['scale_y'] + stats['anime_center_y']
        transformed[point_idx] = [transform_x,transform_y]
    return transformed

        


def main():
    # 设置路径
    real_faces_folder = "E:/B9/face/style_dataset/filtered_faces/train"
    anime_folder = "E:/B9/face/Dataset"

    test_real_img = "E:/B9/face/style_dataset/filtered_faces/test/realface (195).jpg"
    
    # 统计
    calculator = KeypointOffsetStatistics()
    calculator.load_real_face_keypoints(real_faces_folder)
    calculator.load_anime_face_keypoints(anime_folder)
    offset_stats = calculator.calculate_point_statistics()
    calculator.visualize_offset_stats()
    
    print("offset_stats: ",offset_stats) 
    
    # 测试
    extractor = FacialKeypointExtractor()
    normalizer = FacialKeypointNormalizer()
    real_keypoints = extractor.extract_keypoints(test_real_img)
    real_keypoints = normalizer.normalize_keypoints(real_keypoints)
    transformed_keypoints = transform_real_to_anime(real_keypoints,offset_stats)
    print(transformed_keypoints)
    from normalize_facial_keypoints import visualize_normalization
    visualize_normalization(transformed_keypoints)
    
    


if __name__ == "__main__":
    main()
