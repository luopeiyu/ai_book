using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Newtonsoft.Json;

public class MediaPipePoseReader
{
    public static PoseData ReadPoseData(string filePath)
    {
        string jsonContent = File.ReadAllText(filePath);
        PoseData poseData = new PoseData();
        poseData.frames = new List<PoseFrame>();
        // 使用Newtonsoft.Json直接解析二维数组
        List<List<PoseLandmarkData>> frames = JsonConvert.DeserializeObject<List<List<PoseLandmarkData>>>(jsonContent);
        
        // 将二维数组转换为PoseFrame列表
        foreach (List<PoseLandmarkData> frame in frames)
        {
            PoseFrame poseFrame = new PoseFrame();
            poseFrame.landmarks = new List<PoseLandmarkData>();
            foreach (PoseLandmarkData landmark in frame)
            {
                //landmark数据变换：MediaPipe使用左手坐标系，Unity使用左手坐标系，但Y轴方向相反
                landmark.x = landmark.x -0.5f;
                landmark.y = 1-landmark.y;
                landmark.z = landmark.z/2; //MediaPipe: Z向内为正，Unity: Z向前为正，需要反转Z，再做一次镜像保持不变
                poseFrame.landmarks.Add(landmark);
            }
            
            poseData.frames.Add(poseFrame);
        }
        
        // 创建PoseData并设置转换后的帧数据

        return poseData;
    }
    
    public static PoseFrame GetPoseFrame(PoseData poseData, int frameIndex)
    {
        if (frameIndex < 0 || frameIndex >= poseData.frames.Count)
        {
            return null;
        }
        return poseData.frames[frameIndex];
    }
    
    public static PoseLandmarkData GetLandmarkData(PoseFrame frame, int landmarkIndex)
    {
        if (landmarkIndex < 0 || landmarkIndex >= frame.landmarks.Count)
        {
            return null;
        }
        return frame.landmarks[landmarkIndex];
    }
    
    public static int GetTotalFrames(PoseData poseData)
    {
        return poseData.frames.Count;
    }
    
    public static Vector3 GetPosition(PoseFrame frame, PoseLandmark landmark)
    {
        PoseLandmarkData landmarkData = GetLandmarkData(frame, (int)landmark);  
        return new Vector3(landmarkData.x, landmarkData.y, landmarkData.z);
    }

    public static Vector3 GetDirection(PoseFrame frame, PoseLandmark target, PoseLandmark origin) 
    {
        Vector3 targetPosition = GetPosition(frame, target);
        Vector3 originPosition = GetPosition(frame, origin);
        return targetPosition - originPosition;
    }

}
