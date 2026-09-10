import cv2
import mediapipe as mp
import json
import os
from typing import List, Dict, Any
import numpy as np


# MediaPipe姿态关键点的名称列表
#
#         "NOSE", "LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER",
#         "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER",
#         "LEFT_EAR", "RIGHT_EAR", "MOUTH_LEFT", "MOUTH_RIGHT",
#         "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW", "RIGHT_ELBOW",
#         "LEFT_WRIST", "RIGHT_WRIST", "LEFT_PINKY", "RIGHT_PINKY",
#         "LEFT_INDEX", "RIGHT_INDEX", "LEFT_THUMB", "RIGHT_THUMB",
#         "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE",
#         "LEFT_ANKLE", "RIGHT_ANKLE", "LEFT_HEEL", "RIGHT_HEEL",
#         "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"



class VideoPoseExtractor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def extract_pose_from_video(self, video_path: str) -> Dict[str, Any]:

        cap = cv2.VideoCapture(video_path)
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"处理视频: {video_path}")
        print(f"FPS: {fps}, 总帧数: {frame_count}")
        
        
        results = []

        frame_index = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # 转换BGR到RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 检测姿态
            pose_results = self.pose.process(rgb_frame)

            # 打出pose_results的完整结构
            frame_data= []
            
            if pose_results.pose_landmarks:
                # 提取关键点数据
                for landmark in pose_results.pose_landmarks.landmark:
                    frame_data.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    })
            
            results.append(frame_data)
            frame_index += 1
            
        cap.release()
        return results
    





def main():
    video_path = "E:\\b9\\vedio_pose\\resource\\vedio1.mp4"
    output_path = "E:\\b9\\vedio_pose\\script\\vedio1_pose_data.json"
    
    extractor = VideoPoseExtractor()
    pose_data = extractor.extract_pose_from_video(video_path)
    print(pose_data)
    # 保存数据到JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pose_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
