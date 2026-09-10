using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TestLookRotation2: MonoBehaviour
{
    public Transform target;
    public Transform origin;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        Quaternion rotation = Quaternion.LookRotation(target.position - origin.position);
        transform.rotation = rotation;
    }
}
