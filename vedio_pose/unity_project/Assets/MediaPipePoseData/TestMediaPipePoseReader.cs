using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestMediaPipePoseReader : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        PoseData poseData = MediaPipePoseReader.ReadPoseData("E:/b9/vedio_pose/script/vedio1_pose_data.json");
        Debug.Log(poseData.frames.Count);
        PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, 0);
        Debug.Log(poseFrame.landmarks.Count);
        PoseLandmarkData poseLandmarkData = MediaPipePoseReader.GetLandmarkData(poseFrame, 0);
        Debug.Log(poseLandmarkData.x);
        Debug.Log(poseLandmarkData.y);
        Debug.Log(poseLandmarkData.z);
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
