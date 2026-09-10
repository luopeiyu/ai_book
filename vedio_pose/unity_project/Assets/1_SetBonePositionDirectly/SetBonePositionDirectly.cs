using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SetBonePositionDirectly : MonoBehaviour
{
    Animator animator;
    PoseData poseData;
    public bool isAutoPlay = false;
    public int currentFrame = 0;
    public int lastFrame = -1;
    public float frameRate = 5f;
    private float lastFrameTime = 0f;
    
    public Vector3 scale = new Vector3(1, 1, 1);
    
    void Start()
    {
        animator = GetComponent<Animator>();
        // 读取姿态数据
        poseData = MediaPipePoseReader.ReadPoseData("E:/b9/vedio_pose/script/vedio1_pose_data.json");

        // 设置初始帧
        PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, 0);
        SetBonePositionsDirectly(poseFrame);
        lastFrame = currentFrame;
    }

    void Update()
    {
        if (isAutoPlay)
        {
            // 控制播放速度
            if (Time.time - lastFrameTime >= 1f / frameRate)
            {
                currentFrame++;
                if (currentFrame >= poseData.frames.Count)
                {
                    currentFrame = 0;
                }
                
                PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, currentFrame);
                SetBonePositionsDirectly(poseFrame);
                lastFrameTime = Time.time;
                lastFrame = currentFrame;
            }
        }
        else if (lastFrame != currentFrame)
        {
            PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, currentFrame);
            SetBonePositionsDirectly(poseFrame);
            lastFrame = currentFrame;
        }
        

    }
    
    void SetBonePositionsDirectly(PoseFrame poseFrame)
    {
        // 直接设置各个骨骼的位置 - 这是错误的做法！
        
        // 躯干部分
        SetBonePosition(HumanBodyBones.Hips, GetAveragePosition(poseFrame, PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP));
        SetBonePosition(HumanBodyBones.Spine, GetAveragePosition(poseFrame, PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER));
        SetBonePosition(HumanBodyBones.Neck, GetAveragePosition(poseFrame, PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER));
        SetBonePosition(HumanBodyBones.Head, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.NOSE));
        
        // 左臂
        SetBonePosition(HumanBodyBones.LeftShoulder, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_SHOULDER));
        SetBonePosition(HumanBodyBones.LeftUpperArm, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_SHOULDER));
        SetBonePosition(HumanBodyBones.LeftLowerArm, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_ELBOW));
        SetBonePosition(HumanBodyBones.LeftHand, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_WRIST));
        
        // 右臂
        SetBonePosition(HumanBodyBones.RightShoulder, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_SHOULDER));
        SetBonePosition(HumanBodyBones.RightUpperArm, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_SHOULDER));
        SetBonePosition(HumanBodyBones.RightLowerArm, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_ELBOW));
        SetBonePosition(HumanBodyBones.RightHand, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_WRIST));
        
        // 左腿
        SetBonePosition(HumanBodyBones.LeftUpperLeg, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_HIP));
        SetBonePosition(HumanBodyBones.LeftLowerLeg, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_KNEE));
        SetBonePosition(HumanBodyBones.LeftFoot, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_ANKLE));
        
        // 右腿
        SetBonePosition(HumanBodyBones.RightUpperLeg, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_HIP));
        SetBonePosition(HumanBodyBones.RightLowerLeg, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_KNEE));
        SetBonePosition(HumanBodyBones.RightFoot, MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_ANKLE));
        
    }
    
    void SetBonePosition(HumanBodyBones boneType, Vector3 position)
    {
        Transform bone = animator.GetBoneTransform(boneType);
        bone.position = new Vector3(position.x * scale.x, position.y * scale.y, position.z * scale.z);
    }
    
    Vector3 GetAveragePosition(PoseFrame poseFrame, PoseLandmark landmark1, PoseLandmark landmark2)
    {
        Vector3 pos1 = MediaPipePoseReader.GetPosition(poseFrame, landmark1);
        Vector3 pos2 = MediaPipePoseReader.GetPosition(poseFrame, landmark2);
        return (pos1 + pos2) / 2f;
    }
}
