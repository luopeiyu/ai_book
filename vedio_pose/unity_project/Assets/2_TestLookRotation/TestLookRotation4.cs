using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestLookRotation4 : MonoBehaviour
{
    public Transform target_forward;
    public Transform target_origin;
    
    // Start is called before the first frame update
    void Start()
    {
        Transform parent = transform.parent;

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
        Quaternion rotation = LookRotationYForward(target_forward.position - target_origin.position, Vector3.up);
        transform.rotation = rotation;
    }
}
