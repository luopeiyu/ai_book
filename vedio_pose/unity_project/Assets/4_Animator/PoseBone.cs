using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BasePoseBone
{
    public HumanBodyBones boneType;
    public Transform bone;

    public Quaternion correctionRotation = Quaternion.identity;

    public virtual Quaternion CaculateRotation(PoseFrame poseFrame){
        return Quaternion.identity;
    }



    public Quaternion LookRotationYForward(Vector3 forward, Vector3 upwards)
    {
        Quaternion standardRotation = Quaternion.LookRotation(forward, upwards);
        Quaternion axisAdjustment1 = Quaternion.AngleAxis(90f, Vector3.left);
        Quaternion axisAdjustment2 = Quaternion.AngleAxis(180f, Vector3.forward);
        return standardRotation * axisAdjustment1 * axisAdjustment2;
    }



}


public class PoseBone_RightUpperArm : BasePoseBone
{
    public PoseBone_RightUpperArm(Animator animator)
    {
        boneType = HumanBodyBones.RightUpperArm;
        bone = animator.GetBoneTransform(boneType);
        correctionRotation = CaculateCorrection(animator);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_SHOULDER);
        Vector3 lowerArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_WRIST, PoseLandmark.RIGHT_ELBOW);

        Vector3 upwards = -Vector3.Cross(upperArmforward, lowerArmforward);

        
        return LookRotationYForward(upperArmforward, upwards) * correctionRotation;
    }
    
    public Quaternion CaculateCorrection(Animator animator)
    {
        //rightUpperArmReference
        Transform rightUpperArm = animator.GetBoneTransform(HumanBodyBones.RightUpperArm);
        Transform rightLowerArm = animator.GetBoneTransform(HumanBodyBones.RightLowerArm);
        Vector3 forward = (rightLowerArm.position - rightUpperArm.position);
        Transform hips = animator.GetBoneTransform(HumanBodyBones.Hips);
        Transform spine = animator.GetBoneTransform(HumanBodyBones.Spine);
        Vector3 upwards = (spine.position - hips.position);
        Quaternion reference = LookRotationYForward(forward, upwards);
        // 计算最终的调整矩阵
        correctionRotation = Quaternion.Inverse(reference) * rightUpperArm.rotation;
        return correctionRotation;
    }
}

public class PoseBone_RightLowerArm : BasePoseBone
{
    public PoseBone_RightLowerArm(Animator animator)
    {
        boneType = HumanBodyBones.RightLowerArm;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_SHOULDER);
        Vector3 lowerArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_WRIST, PoseLandmark.RIGHT_ELBOW);

        Vector3 upwards = -Vector3.Cross(upperArmforward, lowerArmforward);
        return LookRotationYForward(lowerArmforward, upwards);
    }
}


public class PoseBone_LeftUpperArm : BasePoseBone
{
    public PoseBone_LeftUpperArm(Animator animator)
    {
        boneType = HumanBodyBones.LeftUpperArm;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_SHOULDER);
        Vector3 lowerArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_WRIST, PoseLandmark.LEFT_ELBOW);

        Vector3 upwards = Vector3.Cross(upperArmforward, lowerArmforward);


        return LookRotationYForward(upperArmforward, upwards);
    }
}

public class PoseBone_LeftLowerArm : BasePoseBone
{
    public PoseBone_LeftLowerArm(Animator animator)
    {
        boneType = HumanBodyBones.LeftLowerArm;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_SHOULDER);
        Vector3 lowerArmforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_WRIST, PoseLandmark.LEFT_ELBOW);

        Vector3 upwards = Vector3.Cross(upperArmforward, lowerArmforward);
        return LookRotationYForward(lowerArmforward, upwards);
    }
}

public class PoseBone_RightUpperLeg : BasePoseBone
{
    public PoseBone_RightUpperLeg(Animator animator)
    {
        boneType = HumanBodyBones.RightUpperLeg;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_HIP);
        Vector3 lowerLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_ANKLE, PoseLandmark.RIGHT_KNEE);

        Vector3 crossDirection = -Vector3.Cross(upperLegforward, lowerLegforward);
        Vector3 upwards = Quaternion.AngleAxis(-90, upperLegforward) * crossDirection; 
        return LookRotationYForward(upperLegforward, upwards);
    }
}

public class PoseBone_RightLowerLeg : BasePoseBone
{
    public PoseBone_RightLowerLeg(Animator animator)
    {
        boneType = HumanBodyBones.RightLowerLeg;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_HIP);
        Vector3 lowerLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.RIGHT_ANKLE, PoseLandmark.RIGHT_KNEE);


        Vector3 crossDirection = -Vector3.Cross(upperLegforward, lowerLegforward);
        Vector3 upwards = Quaternion.AngleAxis(-90, lowerLegforward) * crossDirection;
        return LookRotationYForward(lowerLegforward, upwards);
    }
}

public class PoseBone_LeftUpperLeg : BasePoseBone
{
    public PoseBone_LeftUpperLeg(Animator animator)
    {
        boneType = HumanBodyBones.LeftUpperLeg;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_HIP);
        Vector3 lowerLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_ANKLE, PoseLandmark.LEFT_KNEE);

        Vector3 crossDirection = Vector3.Cross(upperLegforward, lowerLegforward);
        Vector3 upwards = Quaternion.AngleAxis(90, upperLegforward) * crossDirection;
        return LookRotationYForward(upperLegforward, upwards);
    }
}

public class PoseBone_LeftLowerLeg : BasePoseBone
{
    public PoseBone_LeftLowerLeg(Animator animator)
    {
        boneType = HumanBodyBones.LeftLowerLeg;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 upperLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_HIP);
        Vector3 lowerLegforward = MediaPipePoseReader.GetDirection(poseFrame, PoseLandmark.LEFT_ANKLE, PoseLandmark.LEFT_KNEE);

        Vector3 crossDirection = Vector3.Cross(upperLegforward, lowerLegforward);
        Vector3 upwards = Quaternion.AngleAxis(90, lowerLegforward) * crossDirection;
        return LookRotationYForward(lowerLegforward, upwards);
    }
}



public class PoseBone_Hips : BasePoseBone
{
    public PoseBone_Hips(Animator animator)
    {
        boneType = HumanBodyBones.Hips;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {

        Vector3 leftShoulder = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_SHOULDER);
        Vector3 rightShoulder = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_SHOULDER);
        Vector3 leftHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_HIP);
        Vector3 rightHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_HIP);
        
        Vector3 midShoulder = (leftShoulder + rightShoulder) / 2;
        Vector3 midHip = (leftHip + rightHip) / 2;
        Vector3 forward = midShoulder - midHip;


        Vector3 upwards = Vector3.Cross(leftShoulder - midHip, midHip - rightShoulder);
        return LookRotationYForward(forward, upwards);
    }
}

public class PoseBone_Spine : BasePoseBone
{
    public PoseBone_Spine(Animator animator)
    {
        boneType = HumanBodyBones.Spine;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 leftShoulder = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_SHOULDER);
        Vector3 rightShoulder = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_SHOULDER);
        Vector3 leftHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_HIP);
        Vector3 rightHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_HIP);

        Vector3 midShoulder = (leftShoulder + rightShoulder) / 2;
        Vector3 midHip = (leftHip + rightHip) / 2;
        Vector3 forward = midShoulder - midHip;


        Vector3 upwards = Vector3.Cross(leftShoulder - midHip, midHip - rightShoulder);
        return LookRotationYForward(forward, upwards);
    }
}

public class PoseBone_Head : BasePoseBone
{
    public PoseBone_Head(Animator animator)
    {
        boneType = HumanBodyBones.Head;
        bone = animator.GetBoneTransform(boneType);
    }
    public override Quaternion CaculateRotation(PoseFrame poseFrame)
    {
        Vector3 leftEar = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_EAR);
        Vector3 rightEar = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_EAR);
        Vector3 leftShoulder = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_SHOULDER);
        Vector3 rightShoulder = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_SHOULDER);
        
        Vector3 midShoulder = (leftShoulder + rightShoulder) / 2;
        
        // 保持向上的forward轴与躯干一致
        Vector3 leftHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.LEFT_HIP);
        Vector3 rightHip = MediaPipePoseReader.GetPosition(poseFrame, PoseLandmark.RIGHT_HIP);
        Vector3 midHip = (leftHip + rightHip) / 2;
        Vector3 forward = midShoulder - midHip;
        
        // 使用耳朵位置计算左右旋转的right向量
        Vector3 rightDirection = rightEar - leftEar;
        Vector3 upwards = Vector3.Cross(rightDirection, forward);
        
        return LookRotationYForward(forward, upwards);
    }
}