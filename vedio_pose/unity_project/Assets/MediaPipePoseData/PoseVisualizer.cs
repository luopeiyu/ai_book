using System.Collections.Generic;
using UnityEngine;

public class PoseVisualizer : MonoBehaviour
{
    public Vector3 scale = new Vector3(5, 5, 5);
    public Vector3 offset = Vector3.zero;
    public int frameIndex = 0;
    public PoseData poseData;
    void Start()
    {
        poseData = MediaPipePoseReader.ReadPoseData("E:/b9/vedio_pose/script/vedio1_pose_data.json");
    }
    
    // MediaPipe骨骼连接定义，为了简洁，直接用数字
    private readonly int[,] boneConnections = new int[,]
    {
        // 身体主干
        {11, 12}, // 肩膀
        {11, 23}, {12, 24}, // 肩膀到臀部
        {23, 24}, // 臀部
        
        // 左臂
        {11, 13}, {13, 15}, // 左臂
        
        // 右臂
        {12, 14}, {14, 16}, // 右臂
        
        // 左腿
        {23, 25}, {25, 27}, // 左腿
        
        // 右腿
        {24, 26}, {26, 28}, // 右腿
        
        // 眼睛
        {1, 2}, {2,3},
        {4, 5}, {5, 6} ,
    };
    

    void DrawFrame(PoseFrame poseFrame)
    {
        for (int i = 0; i < boneConnections.GetLength(0); i++)
        {
            int startIndex = boneConnections[i, 0];
            int endIndex = boneConnections[i, 1];
            Vector3 startPosition = MediaPipePoseReader.GetPosition(poseFrame, (PoseLandmark)startIndex);
            Vector3 endPosition = MediaPipePoseReader.GetPosition(poseFrame, (PoseLandmark)endIndex);
            Vector3 transformedStartPosition = new Vector3(
                startPosition.x * scale.x + offset.x,
                startPosition.y * scale.y + offset.y,
                startPosition.z * scale.z + offset.z
            );
            Vector3 transformedEndPosition = new Vector3(
                endPosition.x * scale.x + offset.x,
                endPosition.y * scale.y + offset.y,
                endPosition.z * scale.z + offset.z
            );
            
            Gizmos.DrawLine(transformedStartPosition, transformedEndPosition);
        }
    }

    void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        if (poseData == null)
        {
            return;
        }
        
        PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, frameIndex);

        DrawFrame(poseFrame);
    }
        

} 