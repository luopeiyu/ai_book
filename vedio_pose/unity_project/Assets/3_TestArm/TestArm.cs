using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestArm : MonoBehaviour
{
    public Transform target1;
    public Transform target2;
    public Transform target3;
    
    Animator animator;
    Transform upperArm;
    Transform lowerArm;
    Transform hand;
    // Start is called before the first frame update
    void Start()
    {
        animator = GetComponent<Animator>();
        upperArm = animator.GetBoneTransform(HumanBodyBones.RightUpperArm);
        lowerArm = animator.GetBoneTransform(HumanBodyBones.RightLowerArm);
        hand = animator.GetBoneTransform(HumanBodyBones.RightHand);
    }


    public static Quaternion LookRotationYForward(Vector3 forward, Vector3 upwards)
    {
        Quaternion standardRotation = Quaternion.LookRotation(forward, upwards);
        Quaternion axisAdjustment1 = Quaternion.AngleAxis(90f, Vector3.left);
        Quaternion axisAdjustment2 = Quaternion.AngleAxis(180f, Vector3.forward);
        return standardRotation * axisAdjustment1 * axisAdjustment2;
    }
    // Update is called once per frame
    void Update()
    {
        
        Vector3 up = Vector3.up; //animator.GetBoneTransform(HumanBodyBones.UpperChest).up;

        upperArm.rotation = LookRotationYForward(target2.position - target1.position, up);
        lowerArm.rotation = LookRotationYForward(target3.position - target2.position, up);
    }
}
