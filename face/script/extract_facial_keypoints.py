import cv2
import mediapipe as mp
import numpy as np

class FacialKeypointExtractor:
    def __init__(self):
        """
        初始化人脸特征点提取器
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5
        )
        
        # MediaPipe 468 → dlib 68
        
        self.face_68_landmarks =[162,234,93,58,172,136,149,148,152,377,378,365,397,288,323,454,389,71,63,105,66,107,336,
                  296,334,293,301,168,197,5,4,75,97,2,326,305,33,160,158,133,153,144,362,385,387,263,373,
                  380,61,39,37,0,267,269,291,405,314,17,84,181,78,82,13,312,308,317,14,87]
                
        
        # 需要画出的68点索引
        self.target_points = [0, 4, 8, 36, 38, 39, 41, 28, 33, 48, 66]
    
    def extract_keypoints(self, image_path):
        """
        提取人脸特征点并画出指定点
        """
        # 读取图片
        image = cv2.imread(image_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 处理图片
        results = self.face_mesh.process(rgb_image)
        face_landmarks = results.multi_face_landmarks[0]
        
        # 获取图像尺寸
        height, width = image.shape[:2]
        
        # 提取11个特征点坐标(可优化直接提取11点对应的坐标)
        keypoints_11 = []
        
        for idx_68 in self.target_points:
            landmark_idx = self.face_68_landmarks[idx_68]
            landmark = face_landmarks.landmark[landmark_idx]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            keypoints_11.append([x, y])
                
        return np.array(keypoints_11)
        



def show_keypoints(input_path, keypoints):
    image = cv2.imread(input_path)
    for point_idx in keypoints:
        x, y = point_idx
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
    cv2.imshow("keypoints",image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def main():
    extractor = FacialKeypointExtractor()
    input_path = "E:/B9/face/test_face/1.png"
    
    keypoints = extractor.extract_keypoints(input_path)
    
    print(keypoints)
    
    show_keypoints(input_path, keypoints)

if __name__ == "__main__":
    main()
