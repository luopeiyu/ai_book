import cv2
import numpy as np
from matplotlib import pyplot as plt
from extract_facial_keypoints import FacialKeypointExtractor,show_keypoints


class FacialKeypointNormalizer:
    def __init__(self):
        """
        初始化人脸特征点归一化器
        """
        # 根据你的数据：第3、5点是眼睛相关点
        self.left_eye_index = 3   # 对应68点的36
        self.nose_tip_index = 7   # 对应68点的28，作为面部中心
    
    def normalize_keypoints(self, keypoints):
        """
        基于两眼间距进行归一化
        
        Args:
            keypoints: 11个特征点坐标 [[x1,y1], [x2,y2], ...]
        
        Returns:
            normalized_keypoints: 归一化后的特征点
        """
        
        # 计算
        left_eye_x = keypoints[self.left_eye_index][0]
        left_eye_y = keypoints[self.left_eye_index][1]
        
        center = keypoints[self.nose_tip_index]
        center_x = center[0]
        center_y = center[1]
        
        # 计算两眼间距
        eye_distance = (center_x - left_eye_x)*2
        
        # 标准化参数
        standard_eye_distance = 1  # 标准两眼间距
        scale_factor = standard_eye_distance / eye_distance
        
        # 执行归一化：以眼部中心为中心进行缩放
        normalized_keypoints = (keypoints - center) * scale_factor
        
        return normalized_keypoints

def visualize_normalization(normalized_keypoints):
   
    # 创建单个图
    plt.figure(figsize=(5, 5))
    
    # 绘制归一化后的特征点
    plt.scatter(normalized_keypoints[:, 0], normalized_keypoints[:, 1], c='red', s=50)
    
    # 设置坐标轴范围为-3到3
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)
    plt.gca().invert_yaxis()  # y轴从上到下
    
    plt.legend()
    plt.axis('equal')  # 保持坐标轴比例一致
    plt.grid(True, alpha=0.1)
    plt.show()
    
    



def main():
    """
    测试归一化功能
    """
    # 从extract_facial_keypoints.py导入提取器
    import sys
    sys.path.append('.')
    from extract_facial_keypoints import FacialKeypointExtractor
    
    # 提取特征点
    extractor = FacialKeypointExtractor()
    image_path = "E:/B9/face/1.png"
    keypoints = extractor.extract_keypoints(image_path)
    
    # 归一化
    normalizer = FacialKeypointNormalizer()
    normalized_keypoints = normalizer.normalize_keypoints(keypoints)
    
    print(normalized_keypoints)
    print("基于两眼间距的特征点归一化")
    
    #show_keypoints(image_path,keypoints)
    visualize_normalization(normalized_keypoints)

if __name__ == "__main__":
    main()
