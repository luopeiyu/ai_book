using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class Item : MonoBehaviour
{

    public string itemName = "未知物品";

    public float pickupRange = 1.5f;         // 拾取范围

    public void PickUp(NpcController picker)
    {

        Debug.Log($"拾取了 {itemName}");
        Destroy(gameObject);
    }
    

    public bool IsInPickupRange(Vector3 position)
    {
        return Vector3.Distance(transform.position, position) <= pickupRange;
    }
    
}
