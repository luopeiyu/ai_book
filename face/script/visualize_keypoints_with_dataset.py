import cv2
import json
import numpy as np
from matplotlib import pyplot as plt

def visualize_keypoints(image_path, json_path):
    """
    可视化图片上的特征点
    
    Args:
        image_path (str): 输入图片路径
        json_path (str): JSON文件路径
    """
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片: {image_path}")
        return
    
    # 转换为RGB格式
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    landmarks = data['landmarks']
    
    # 定义需要用蓝色标注的对称点序号
    symmetric_points = [0, 1, 3, 4, 5, 6, 9]
    
    # 绘制特征点
    for i, landmark in enumerate(landmarks):
        x = int(landmark['x'])
        y = int(landmark['y'])
        
        # 根据序号选择颜色
        cv2.circle(image_rgb, (x, y), 3, (255, 0, 0), -1)
        if i in symmetric_points:
            # 计算x轴对称点的坐标
            symmetric_x = image_rgb.shape[1] - x  # 图片宽度减去x坐标
            cv2.circle(image_rgb, (symmetric_x, y), 3, (0, 0, 255), -1) # 用蓝色圆圈标注x轴对称点

        
        # 标注序号
        cv2.putText(image_rgb, str(i), (x + 10, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 显示图片
    plt.figure(figsize=(10, 8))
    plt.imshow(image_rgb)
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    # 使用示例
    image_path = "E:/B9/face/unity_sim/Assets/Dataset/sample_0001.png"
    json_path = "E:/B9/face/unity_sim/Assets/Dataset/sample_0001.json"
    
    visualize_keypoints(image_path, json_path)
