using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Monster : MonoBehaviour
{
    public int id;
    public int maxHealth = 100;
    public int health = 100;
    public Transform canvasTransform;
    public Image healthBarImage;
    // Start is called before the first frame update
    void Start()
    {
        canvasTransform = transform.Find("Canvas");
        healthBarImage = canvasTransform.Find("HpImage").GetComponent<Image>();
        health = maxHealth;
        UpdateHealthBar();
    }


    public void UpdateHealthBar()
    {
        healthBarImage.fillAmount = (float)health / maxHealth;
    }
    // Update is called once per frame
    void Update()
    {
        FaceCamera();
    }
    
    public void TakeDamage(int damage)
    {
        health -= damage;
        UpdateHealthBar();
        if(health <= 0)
        {
            GameManager.Instance.monsterManager.MonsterDie(id);
        }
    }

    void FaceCamera()
    {

        // 让血条面向相机
        Vector3 directionToCamera = Camera.main.transform.position - canvasTransform.position;
        healthBarImage.transform.rotation = Quaternion.LookRotation(-directionToCamera);
    }
}
