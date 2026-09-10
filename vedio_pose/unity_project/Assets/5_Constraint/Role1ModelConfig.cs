using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Role1ModelConfig : ModelConfig
{
    public Role1ModelConfig()
    {
        // 右上臂限制（肩关节）- 相对于躯干
        rightUpperArmConstraints.minRotation = new Vector3(-10, -180, -10);  // X:前后摆动, Y:左右摆动, Z:内外旋转
        rightUpperArmConstraints.maxRotation = new Vector3(10, 180, 10);
        
        // 右下臂限制（肘关节）- 相对于上臂，主要是弯曲动作
        // rightLowerArmConstraints.minRotation = new Vector3(0, 0, -30);
        rightLowerArmConstraints.maxRotation = new Vector3(0, 0, 30);
        
        // 左上臂限制（肩关节）- 相对于躯干
        leftUpperArmConstraints.minRotation = new Vector3(-10, -180, -10);
        leftUpperArmConstraints.maxRotation = new Vector3(10, 180, 10);
        
        // 左下臂限制（肘关节）- 相对于上臂
        // leftLowerArmConstraints.minRotation = new Vector3(0, 0, -30);
        // leftLowerArmConstraints.maxRotation = new Vector3(0, 0, 30);
        
        // 腿部也添加一些合理的限制
        //rightUpperLegConstraints.minRotation = new Vector3(-30, -30, -20);
        //rightUpperLegConstraints.maxRotation = new Vector3(100, 30, 60);
        
        //leftUpperLegConstraints.minRotation = new Vector3(-30, -30, -60);
        //leftUpperLegConstraints.maxRotation = new Vector3(100, 30, 20);
        
        //rightLowerLegConstraints.minRotation = new Vector3(0, -10, -10);
        //rightLowerLegConstraints.maxRotation = new Vector3(130, 10, 10);
        
        //leftLowerLegConstraints.minRotation = new Vector3(0, -10, -10);
        //leftLowerLegConstraints.maxRotation = new Vector3(130, 10, 10);
    }
}
