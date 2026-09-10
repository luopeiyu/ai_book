using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MonsterManager : MonoBehaviour
{
    public Dictionary<int, Monster> monsters = new Dictionary<int, Monster>();
    public List<float> dieTime = new List<float>();
    public GameObject monsterPrefab;
    
    public GameObject spawnPoints;
    public List<GameObject> spawnPointsList = new List<GameObject>();
    
    public float respawnTime = 15f;
    // Start is called before the first frame update
    void Start()
    {
        
        spawnPoints = GameObject.Find("spawnPoints");
        foreach (Transform child in spawnPoints.transform)
        {
            spawnPointsList.Add(child.gameObject);
            dieTime.Add(-5000);
        }

    }


    public void RespawnMonster()
    {
        for(int i = 0; i < spawnPointsList.Count; i++)
        {
            if (Time.time - dieTime[i] > respawnTime)
            {
                SpawnMonster(i);
            }
        }
    }
    
    
    public void SpawnMonster(int id)
    {
        Vector3 position = spawnPointsList[id].transform.position;
        Quaternion rotation = spawnPointsList[id].transform.rotation;
        // 修正角度
        Vector3 euler = rotation.eulerAngles;
        euler.x = 90f;
        rotation = Quaternion.Euler(euler);
        
        GameObject monsterObject = Instantiate(monsterPrefab, position, rotation);
        Monster monster = monsterObject.AddComponent<Monster>();
        monster.id = id;
        dieTime[id] = float.MaxValue;
        monsters.Add(id, monster);
    }

    public void MonsterDie(int id)
    {
        dieTime[id] = Time.time;
        Destroy(monsters[id].gameObject);
        monsters.Remove(id);
    }

    // Update is called once per frame
    void Update()
    {
        RespawnMonster();
    }
}
