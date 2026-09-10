using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

enum NPCState{
    Idle,
    Follow,
    AutoAttack,
    Tasking
}

public class NpcController : MonoBehaviour
{
    public Transform npcTransform;
    public Queue<BaseAction> actionQueue = new Queue<BaseAction>();
    public NavMeshAgent agent;
    public Animator animator;
    BaseAction currentAction;

    public float attackRange = 0.3f;            // 攻击范围
    public float attackCooldown = 2f;         // 攻击冷却时间
    public LayerMask enemyLayers = -1;          // 敌人层级
    private float lastAttackTime = 0;           // 上次攻击时间
    private bool isAttacking = false;           // 是否正在攻击


    NPCState currentState = NPCState.Idle;
    public bool toFollow = false;
    public bool toAutoAttack = false;
    
    private float followUpdateTimer = 0f;
    private float findMonsterTimer = 0f;
    
    
    private Monster targetMonster = null;
    void Start(){
        agent = npcTransform.GetComponent<NavMeshAgent>();
        animator = npcTransform.GetComponent<Animator>();
        enemyLayers = LayerMask.GetMask("Monster");
    }
    void Update(){
        
        
        //AI状态机
        switch(currentState){
            case NPCState.Idle:
                UpdateIdleState();
                break;
            case NPCState.Follow:
                UpdateFollowState();    
                break;
            case NPCState.AutoAttack:
                UpdateAutoAttackState();
                break;
            case NPCState.Tasking:
                UpdateTaskingState();
                break;
        }


        //状态处理
        if (isAttacking && Time.time - lastAttackTime > attackCooldown)
        {
            isAttacking = false;
        }
    }
    
    
    void UpdateIdleState(){

        if (actionQueue.Count > 0)
        {
            currentState = NPCState.Tasking;
            return;
        }
        if (toFollow)
        {
            currentState = NPCState.Follow;
            return;
        }
        
        if (toAutoAttack)
        {
            currentState = NPCState.AutoAttack;
            return;
        }
        


        

    }
    
    
    void UpdateTaskingState(){
        if (currentAction != null)
        {
            currentAction.OnUpdate();
            if (currentAction.isComplete)
            {
                currentAction.OnComplete();
                currentAction = null;
            }
        }
        else
        {
            if (actionQueue.Count > 0)
            {
                currentAction = actionQueue.Dequeue();
                currentAction.OnStart();
            }
            else
            {
                currentState = NPCState.Idle;
            }
        }
    }
    
    void FollowPlayerUpdate(){
        float followDistance = 2.0f; // 跟随距离
        float stopDistance = 2.5f;   // 到达玩家附近的停止距离

        // 计算NPC与玩家的距离
        Transform playerTransform = GameManager.Instance.playerController.playerTransform;
        float distanceToPlayer = Vector3.Distance(npcTransform.position, playerTransform.position);

        // 只有距离大于停止距离时才移动
        if (distanceToPlayer > stopDistance)
        {
            MoveTo(playerTransform, followDistance);
            animator.SetBool("isMoving", true);
        }
        else
        {
            // 距离足够近，停止移动
            if (!agent.isStopped)
            {
                agent.isStopped = true;
            }
            animator.SetBool("isMoving", false);
        }
    }
    
    
    void UpdateFollowState(){
        // 如果有任务就退出
        if (actionQueue.Count > 0)
        {
            currentState = NPCState.Idle;
            return;
        }
        // 如果toFollow变量为false则退出
        if (!toFollow)
        {
            currentState = NPCState.Idle;
            return;
        }

        FollowPlayerUpdate();

        
    }


    void MoveTo(Transform targetObject, float followDistance)
    {
        // 每隔一段时间重新设置一次目标点，避免频繁寻路
        if (followUpdateTimer <= 0f)
        {
            agent.isStopped = false;
           
            Vector3 directionToPlayer = (npcTransform.position - targetObject.position).normalized;
            Vector3 targetPosition = targetObject.position + directionToPlayer * followDistance;

            agent.SetDestination(targetPosition);
            followUpdateTimer = 0.3f; 
        }
        else
        {
            followUpdateTimer -= Time.deltaTime;
        }
    }
    
    
    Monster CheckMonsterInRange(){
        float range = 6.0f;
        Collider[] enemies = Physics.OverlapSphere(npcTransform.position, range, enemyLayers);
        foreach (Collider enemyCollider in enemies)
        {
            Monster monster = enemyCollider.GetComponent<Monster>();
            if(monster != null){
                return monster;
            }
        }
        return null;
    }
    
    
    void MoveToAndAttack(Monster targetMonster)
    {
        float distance = Vector3.Distance(npcTransform.position, targetMonster.transform.position);
        if (distance > 1.5)
        {
            // 没到攻击距离，继续移动
            MoveTo(targetMonster.transform, 1);
            animator.SetBool("isMoving", true);
        }
        else
        {
            // 到达攻击距离，停止移动并攻击
            if (!agent.isStopped)
            {
                agent.isStopped = true;
            }
            animator.SetBool("isMoving", false);

            // 攻击冷却判断
            if (Time.time - lastAttackTime > attackCooldown && !isAttacking)
            {
                StartCoroutine(PerformAttack());
                lastAttackTime = Time.time;
                isAttacking = true;
            }
        }
    }

    void UpdateAutoAttackState(){
            
        if(actionQueue.Count > 0){
            currentState = NPCState.Idle;
            return;
        }
            
        if(!toAutoAttack){
            currentState = NPCState.Idle;
            return;
        }

        if (toFollow)
        {
            currentState = NPCState.Idle;
            return;
        }

        //有目标就去攻击
        if (targetMonster != null) {
            MoveToAndAttack(targetMonster);
            return;
        }
        
        //没目标就找目标
        if(targetMonster == null){
            // 每隔1秒找一次怪物
            findMonsterTimer -= Time.deltaTime;
            if (findMonsterTimer <= 0f) {
                targetMonster = CheckMonsterInRange();
                findMonsterTimer = 1f;
            }
        }
        
    }
    

    public void AddAction(BaseAction action){
        if(action.npcController == null){
            action.npcController = this;
        }
        actionQueue.Enqueue(action);
    }

    void HandleAttack()
    {
        // Space键攻击
        if (Time.time - lastAttackTime > attackCooldown)
        {
            StartCoroutine(PerformAttack());
            lastAttackTime = Time.time;
            isAttacking = true;
        }

        if (isAttacking && Time.time - lastAttackTime > attackCooldown)
        {
            isAttacking = false;
        }
    }

    IEnumerator PerformAttack()
    {
        // 触发攻击动画
        if (animator != null)
        {
            animator.SetTrigger("Attack");
        }


        float attackTriggerDelay = 0.5f; // 攻击动画开始后0.3秒触发伤害
        yield return new WaitForSeconds(attackTriggerDelay);

        // 检测攻击范围内的敌人
        Collider[] enemies = Physics.OverlapSphere(npcTransform.position + npcTransform.forward * attackRange, attackRange, enemyLayers);

        foreach (Collider enemyCollider in enemies)
        {
            Monster monster = enemyCollider.GetComponent<Monster>();
            if (monster != null)
            {
                
                //面向怪物
                npcTransform.LookAt(enemyCollider.transform);
                
                int attackDamage = 25;
                monster.TakeDamage(attackDamage);
                Debug.Log("NPC玩家攻击到怪物: " + enemyCollider.gameObject.name);
            }
            else
            {
                Debug.Log("NPC攻击到非怪物目标: " + enemyCollider.gameObject.name);
            }
            break;
        }
    }
    
    
    public void ClearActionQueue(){
        actionQueue.Clear();
    }
}   
