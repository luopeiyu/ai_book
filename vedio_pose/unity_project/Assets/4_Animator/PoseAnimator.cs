using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PoseAnimator : MonoBehaviour
{
    Animator animator;
    List<BasePoseBone> poseBones = new List<BasePoseBone>();
    PoseData poseData;
    public bool isAutoPlay = false;
    public int currentFrame = 0;
    public int lastFrame = -1;
    public float frameRate = 5f; // 控制播放帧率
    private float lastFrameTime = 0f;

    public bool isSmooth = false;
    private Vector3 initHipPosition;
    // Start is called before the first frame update
    void Start()
    {
        animator = GetComponent<Animator>();

        poseBones.Add(new PoseBone_Hips(animator));//躯干，注意顺序，一定要先父后子
        poseBones.Add(new PoseBone_Spine(animator));
        poseBones.Add(new PoseBone_Head(animator));
        
        poseBones.Add(new PoseBone_RightUpperArm(animator));//手
        poseBones.Add(new PoseBone_RightLowerArm(animator));
        poseBones.Add(new PoseBone_LeftUpperArm(animator));
        poseBones.Add(new PoseBone_LeftLowerArm(animator));
        
        poseBones.Add(new PoseBone_RightUpperLeg(animator));//腿
        poseBones.Add(new PoseBone_RightLowerLeg(animator));
        poseBones.Add(new PoseBone_LeftUpperLeg(animator));
        poseBones.Add(new PoseBone_LeftLowerLeg(animator));


        initHipPosition = poseBones[0].bone.position;

        //测试
        poseData = MediaPipePoseReader.ReadPoseData("E:/b9/vedio_pose/script/vedio1_pose_data.json");
        PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, currentFrame);
        PlayFrame(poseFrame);
        lastFrame = currentFrame;
    }

    // Update is called once per frame

    
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
                
                if (isSmooth)
                {
                    PlayFrameSmooth(poseFrame, 0.3f);
                }
                else
                {
                    PlayFrame(poseFrame);
                }
                lastFrameTime = Time.time;
                lastFrame = currentFrame;
                
                AdjustHipPosition(poseFrame);

            }
        }
        else if (lastFrame != currentFrame)
        {
            PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, currentFrame);
            if (isSmooth)
            {
                PlayFrameSmooth(poseFrame, 0.3f);
            }
            else
            {
                PlayFrame(poseFrame);
            }
            lastFrame = currentFrame;
        }
        else if (Input.GetKeyDown(KeyCode.Space))
        {
            PoseFrame poseFrame = MediaPipePoseReader.GetPoseFrame(poseData, currentFrame);
            if (isSmooth)
            {
                PlayFrameSmooth(poseFrame, 0.3f);
            }
            else
            {
                PlayFrame(poseFrame);
            }
            lastFrame = currentFrame;
        }

        
    }
    
    public void PlayFrame(PoseFrame poseFrame)
    {
        foreach (BasePoseBone poseBone in poseBones)
        {
            Quaternion rotation = poseBone.CaculateRotation(poseFrame);
            poseBone.bone.rotation = rotation;
        }
    }

    public void PlayFrameSmooth(PoseFrame poseFrame, float smoothingFactor)
    {
        foreach (BasePoseBone poseBone in poseBones)
        {
            Quaternion rotation = poseBone.CaculateRotation(poseFrame);
            // 使用Slerp进行平滑插值，smoothingFactor控制平滑程度
            poseBone.bone.rotation = Quaternion.Slerp(poseBone.bone.rotation, rotation, smoothingFactor);
        }
    }
    


    
    public void AdjustHipPosition(PoseFrame poseFrame)
    {
        Vector3 leftHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_HIP);
        Vector3 rightHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_HIP);
        Vector3 hipPosition = (leftHip + rightHip) / 2;
        
        PoseFrame firstFrame = MediaPipePoseReader.GetPoseFrame(poseData, 0);
        Vector3 firstFrameLeftHip = MediaPipePoseReader.GetPosition(firstFrame, PoseLandmark.LEFT_HIP);
        Vector3 firstFrameRightHip = MediaPipePoseReader.GetPosition(firstFrame, PoseLandmark.RIGHT_HIP);
        Vector3 firstFrameHipPosition = (firstFrameLeftHip + firstFrameRightHip) / 2;
        
        Vector3 hipOffset = hipPosition - firstFrameHipPosition;
        
        poseBones[0].bone.position = initHipPosition + hipOffset;
    }
}
