using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestGetLocalRotation : MonoBehaviour
{
    public Transform target_forward;
    public Transform target_origin;
    public Transform parent;
    
    // Start is called before the first frame update
    void Start()
    {
        parent = transform.parent;
    }

    // Update is called once per frame
    void Update()
    {
        Quaternion rotation = Quaternion.LookRotation(target_forward.position - target_origin.position);
        //方法1：计算相对父节点的旋转
        //Quaternion localRotation = Quaternion.Inverse(parent.rotation) * rotation;
        //transform.localRotation = localRotation;
        //Debug.Log($"localRotation: {localRotation}");
        
        //方法2：先设置触发计算再获取
        transform.rotation = rotation;
        Debug.Log($"transform.localRotation: {transform.localRotation}");
    }
}
