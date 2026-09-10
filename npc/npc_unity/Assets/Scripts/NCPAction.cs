using UnityEngine;
using UnityEngine.AI;

public class BaseAction {
    public bool isComplete = false;
    public NpcController npcController;
    public virtual void OnStart(){
        Debug.Log("BaseAction OnStart");
    }
    
    public virtual void OnUpdate(){
        Debug.Log("BaseAction OnUpdate");
    }
    
    public virtual void OnComplete(){
        Debug.Log("BaseAction OnEnd");
    }
}

public class SpeakAction : BaseAction{
    public string message;
    public float startTime;
    public float duration = 3.0f;
    public SpeakAction(string message){
        this.message = message;
        startTime = Time.time;
    }
    public override void OnStart(){
        
        for(int i = 0; i < GameManager.Instance.npcControllers.Length; i++){
            if(npcController == GameManager.Instance.npcControllers[i]){
                GameManager.Instance.uiManager.NPCSpeak(i, message);
                break;
            }
        }
    }
    
    public override void OnUpdate(){
        if(Time.time - startTime > duration){
            isComplete = true;
        }
    }
}

public class MoveAction : BaseAction {
    private Vector3 targetPosition;
    private NavMeshAgent agent;
    public MoveAction(Vector3 targetPosition)
    {
        this.targetPosition = targetPosition;
    }

    public override void OnStart()
    {
        agent = npcController.agent;
        agent.isStopped = false;
        agent.SetDestination(targetPosition);
        npcController.animator.SetBool("isMoving", true);
    }

    public override void OnUpdate()
    {
        // 判断是否到达目的地
        if (!agent.pathPending && agent.remainingDistance <= agent.stoppingDistance)
        {
            if (!agent.hasPath || agent.velocity.sqrMagnitude == 0f)
            {
                isComplete = true;
            }
        }
    }

    public override void OnComplete()
    {
        agent.isStopped = true;
        npcController.animator.SetBool("isMoving", false);
    }
}


public class PickAction : BaseAction 
{

    public override void OnStart()
    {
        Item[] items = GameObject.FindObjectsOfType<Item>();
        bool hasPicked = false;
        foreach (Item item in items)
        {
            if (item.IsInPickupRange(npcController.transform.position))
            {
                item.PickUp(npcController);
                hasPicked = true;
                SpeakAction speakAction = new SpeakAction("我拾取了" + item.itemName);
                npcController.AddAction(speakAction);
                Debug.Log("我拾取了" + item.itemName);
                break;
            }
        }
        
        if(!hasPicked)
        {
            SpeakAction speakAction = new SpeakAction("我没有拾取到物品");
            npcController.AddAction(speakAction);
            Debug.Log("我没有拾取到物品");
        }
        
        isComplete = true;
    }
}

public class FollowAction : BaseAction
{
    public override void OnStart()
    {
        npcController.toFollow = true;
        isComplete = true;
    }
}
   
public class IdelAction : BaseAction
{
    public override void OnStart()
    {
        npcController.toFollow = false;
        npcController.toAutoAttack = false;
        isComplete = true;
    }
}

public class AutoAttackAction : BaseAction
{
    public override void OnStart()
    {
        npcController.toFollow = false;
        npcController.toAutoAttack = true;
        isComplete = true;
    }
}


