using System.Collections;
using System.Collections.Generic;
using UnityEngine;



public class ModelConfig
{
    //身体
    public BoneConstraints hipsConstraints = new BoneConstraints();
    public BoneConstraints spineConstraints = new BoneConstraints();
    public BoneConstraints headConstraints = new BoneConstraints();

    //手臂
    public BoneConstraints rightUpperArmConstraints = new BoneConstraints();
    public BoneConstraints rightLowerArmConstraints = new BoneConstraints();
    public BoneConstraints leftUpperArmConstraints = new BoneConstraints();
    public BoneConstraints leftLowerArmConstraints = new BoneConstraints();

    //腿部
    public BoneConstraints rightUpperLegConstraints = new BoneConstraints();
    public BoneConstraints rightLowerLegConstraints = new BoneConstraints();
    public BoneConstraints leftUpperLegConstraints = new BoneConstraints();
    public BoneConstraints leftLowerLegConstraints = new BoneConstraints();


    // 获取特定骨骼的约束
    public BoneConstraints GetBoneConstraints(HumanBodyBones boneType)
    {
        switch (boneType)
        {
            case HumanBodyBones.Hips: return hipsConstraints;
            case HumanBodyBones.Spine: return spineConstraints;
            case HumanBodyBones.Head: return headConstraints;
            case HumanBodyBones.RightUpperArm: return rightUpperArmConstraints;
            case HumanBodyBones.RightLowerArm: return rightLowerArmConstraints;
            case HumanBodyBones.LeftUpperArm: return leftUpperArmConstraints;
            case HumanBodyBones.LeftLowerArm: return leftLowerArmConstraints;
            case HumanBodyBones.RightUpperLeg: return rightUpperLegConstraints;
            case HumanBodyBones.RightLowerLeg: return rightLowerLegConstraints;
            case HumanBodyBones.LeftUpperLeg: return leftUpperLegConstraints;
            case HumanBodyBones.LeftLowerLeg: return leftLowerLegConstraints;
            default: return new BoneConstraints();
        }
    }
}
