import cv2
import mediapipe as mp
import json
import os
import numpy as np


class PoseRenderer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # 初始化姿态检测器
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,  # 设置为True，因为我们处理单帧图像
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def render_pose_from_video(self, video_path: str, output_dir: str = "output_frames", interval_seconds: int = 3):
        """
        从视频中每隔指定秒数提取一帧，检测姿态并可视化关键点
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出图片的目录
            interval_seconds: 提取间隔（秒）
        """
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        cap = cv2.VideoCapture(video_path)
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        print(f"处理视频: {video_path}")
        print(f"FPS: {fps}, 总帧数: {frame_count}, 时长: {duration:.2f}秒")
        
        # 计算每隔多少帧提取一次
        frame_interval = int(fps * interval_seconds)
        
        frame_index = 0
        extracted_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每隔指定帧数处理一次
            if frame_index % frame_interval == 0:
                current_time = frame_index / fps
                print(f"处理第 {frame_index} 帧 (时间: {current_time:.1f}秒)")
                
                # 转换BGR到RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 检测姿态
                pose_results = self.pose.process(rgb_frame)
                
                # 在原始帧上绘制关键点
                annotated_frame = frame.copy()
                
                if pose_results.pose_landmarks:
                    # 绘制姿态关键点和连接线
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        pose_results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    
                    # 添加文本信息
                    text = f"Frame: {frame_index}, Time: {current_time:.1f}s"
                    cv2.putText(annotated_frame, text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # 添加关键点数量信息
                    landmarks_count = len(pose_results.pose_landmarks.landmark)
                    count_text = f"Landmarks: {landmarks_count}"
                    cv2.putText(annotated_frame, count_text, (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    # 如果没有检测到姿态，添加提示文本
                    no_pose_text = "No pose detected"
                    cv2.putText(annotated_frame, no_pose_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # 保存带注释的帧
                output_filename = f"pose_frame_{extracted_count:04d}_time_{current_time:.1f}s.jpg"
                output_path = os.path.join(output_dir, output_filename)
                cv2.imwrite(output_path, annotated_frame)
                
                print(f"保存图片: {output_path}")
                extracted_count += 1
            
            frame_index += 1
        
        cap.release()
        print(f"处理完成！共提取了 {extracted_count} 帧图片")
        return extracted_count
    
    def render_pose_with_detailed_info(self, video_path: str, output_dir: str = "detailed_output", interval_seconds: int = 10):
        """
        带详细信息的姿态渲染，包括关键点坐标和可见度
        """
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_interval = int(fps * interval_seconds)
        frame_index = 0
        extracted_count = 0
        
        # MediaPipe关键点名称
        landmark_names = [
            "NOSE", "LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER",
            "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER",
            "LEFT_EAR", "RIGHT_EAR", "MOUTH_LEFT", "MOUTH_RIGHT",
            "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW", "RIGHT_ELBOW",
            "LEFT_WRIST", "RIGHT_WRIST", "LEFT_PINKY", "RIGHT_PINKY",
            "LEFT_INDEX", "RIGHT_INDEX", "LEFT_THUMB", "RIGHT_THUMB",
            "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE",
            "LEFT_ANKLE", "RIGHT_ANKLE", "LEFT_HEEL", "RIGHT_HEEL",
            "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"
        ]
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_index % frame_interval == 0:
                current_time = frame_index / fps
                
                # 转换BGR到RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 检测姿态
                pose_results = self.pose.process(rgb_frame)
                
                if pose_results.pose_landmarks:
                    # 创建一个更大的画布来显示详细信息
                    height, width = frame.shape[:2]
                    extended_frame = np.zeros((height, width, 3), dtype=np.uint8) # width +400
                    extended_frame[:, :width] = frame
                    
                    # 绘制姿态关键点
                    self.mp_drawing.draw_landmarks(
                        extended_frame,
                        pose_results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    
                    # 在右侧区域显示关键点详细信息
                    text_x = width + 10
                    text_y = 30
                    line_height = 20
                    
                    # 标题
                    cv2.putText(extended_frame, f"Frame: {frame_index}", (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    text_y += line_height
                    
                    cv2.putText(extended_frame, f"Time: {current_time:.1f}s", (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    text_y += line_height * 2
                    
                    # 显示部分关键点的坐标信息（主要关节点）
                    key_landmarks = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]  # 主要关节点索引
                    
                    for i, landmark_idx in enumerate(key_landmarks):
                        if landmark_idx < len(pose_results.pose_landmarks.landmark):
                            landmark = pose_results.pose_landmarks.landmark[landmark_idx]
                            name = landmark_names[landmark_idx]
                            
                            # 显示关键点信息
                            info_text = f"{name[:12]}: ({landmark.x:.3f}, {landmark.y:.3f})"
                            cv2.putText(extended_frame, info_text, (text_x, text_y), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                            text_y += 15
                            
                            # 显示可见度
                            vis_text = f"Visibility: {landmark.visibility:.3f}"
                            cv2.putText(extended_frame, vis_text, (text_x, text_y), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                            text_y += 20
                    
                    # 保存扩展的帧
                    output_filename = f"detailed_pose_frame_{extracted_count:04d}.jpg"
                    output_path = os.path.join(output_dir, output_filename)
                    cv2.imwrite(output_path, extended_frame)
                    
                    print(f"保存详细图片: {output_path}")
                    extracted_count += 1
            
            frame_index += 1
        
        cap.release()
        print(f"详细处理完成！共提取了 {extracted_count} 帧图片")


def main():
    video_path = "E:\\b9\\vedio_pose\\resource\\vedio1.mp4"
    
    renderer = PoseRenderer()
    
    print("开始基础姿态渲染...")
    # 基础渲染，每10秒提取一帧
    count1 = renderer.render_pose_from_video(video_path, "output_frames", interval_seconds=1)
    
    print("\n开始详细姿态渲染...")
    # 详细渲染，包含坐标信息
    renderer.render_pose_with_detailed_info(video_path, "detailed_output", interval_seconds=1)
    
    print(f"\n渲染完成！请查看输出目录中的图片文件")


if __name__ == "__main__":
    main()
