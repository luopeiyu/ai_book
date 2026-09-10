using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerController : MonoBehaviour
{

    public float moveSpeed = 5.0f;              // 移动速度
    public float gravity = 9.8f;               // 重力强度
    public float rotationSpeed = 10.0f;         // 角色旋转速度
    

    public Camera playerCamera;                 // 玩家相机
    public float cameraDistance = 5.0f;         // 相机距离
    public float cameraHeight = 2.0f;           // 相机高度
    public float mouseSensitivity = 2.0f;       // 鼠标灵敏度
    public float upDownRange = 80.0f;           // 上下视角限制角度
    public LayerMask cameraCollisionLayers = -1; // 相机碰撞检测层
    

    public float attackRange = 0.3f;            // 攻击范围
    public float attackCooldown = 2f;         // 攻击冷却时间
    public LayerMask enemyLayers = -1;          // 敌人层级
    

    public CharacterController characterController; // 角色控制器组件
    public Animator animator;                   // 动画控制器
    
    // 私有变量
    private Vector3 velocity;                   // 当前速度
    private bool isGrounded;                    // 是否在地面
    private float horizontalRotation = 0;       // 水平旋转角度
    private float verticalRotation = 0;         // 垂直旋转角度
    private float lastAttackTime = 0;           // 上次攻击时间
    private Vector3 cameraOffset;               // 相机偏移
    private bool controlEnabled = true;         // 是否允许控制
    
    public Transform playerTransform;
    private bool isAttacking = false;
    
    
    void Start()
    {
        
        playerTransform = characterController.transform;
        animator = playerTransform.GetComponent<Animator>();
        playerCamera = Camera.main;
        enemyLayers = LayerMask.GetMask("Monster");
        // 初始化相机位置
        InitializeCamera();
    }

    void Update()
    {
        // 只有在允许控制时才处理输入
        if (controlEnabled)
        {
            // 处理鼠标视角控制
            HandleMouseLook();
            
            // 处理角色移动
            HandleMovement();
            
            // 处理攻击
            HandleAttack();
        }
    }
    
    void LateUpdate()
    {
        // 更新相机位置
        UpdateCameraPosition();
    }
    
    /// <summary>
    /// 初始化相机位置
    /// </summary>
    void InitializeCamera()
    {
        if (playerCamera != null)
        {
            horizontalRotation = playerTransform.eulerAngles.y;
            verticalRotation = 20f; // 默认向下看的角度
            UpdateCameraPosition();
        }
    }
    
    /// <summary>
    /// 处理鼠标视角控制
    /// </summary>
    void HandleMouseLook()
    {
        if (playerCamera == null) return;
        
        if (!controlEnabled) return;
        
        // 只有按下鼠标右键才能操作视角
        if (!Input.GetMouseButton(1))
        {
            return;
        }
        
        // 获取鼠标输入
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;
        
        // 水平旋转（左右环绕角色）
        horizontalRotation += mouseX;
        
        // 垂直旋转（上下调整视角）
        verticalRotation -= mouseY;
        verticalRotation = Mathf.Clamp(verticalRotation, -upDownRange, upDownRange);
    }
    
    /// <summary>
    /// 更新相机位置
    /// </summary>
    void UpdateCameraPosition()
    {
        if (playerCamera == null) return;
        
        // 计算相机的目标位置
        Vector3 direction = new Vector3(0, 0, -cameraDistance);
        Quaternion rotation = Quaternion.Euler(verticalRotation, horizontalRotation, 0);
        Vector3 targetPosition = playerTransform.position + Vector3.up * cameraHeight + rotation * direction;
        
        // 检查相机碰撞
        Vector3 actualPosition = CheckCameraCollision(targetPosition);
        
        // 设置相机位置和旋转
        playerCamera.transform.position = actualPosition;
        playerCamera.transform.LookAt(playerTransform.position + Vector3.up * cameraHeight);
    }
    
    /// <summary>
    /// 检查相机碰撞
    /// </summary>
    Vector3 CheckCameraCollision(Vector3 targetPosition)
    {
        Vector3 playerPos = playerTransform.position + Vector3.up * cameraHeight;
        Vector3 direction = (targetPosition - playerPos).normalized;
        float distance = Vector3.Distance(playerPos, targetPosition);
        
        RaycastHit hit;
        if (Physics.Raycast(playerPos, direction, out hit, distance, cameraCollisionLayers))
        {
            return hit.point - direction * 0.1f; // 稍微向前偏移避免穿墙
        }
        
        return targetPosition;
    }
    
    /// <summary>
    /// 处理角色移动
    /// </summary>
    void HandleMovement()
    {
        // 检测是否在地面
        isGrounded = characterController.isGrounded;
        
        // 在攻击时不允许移动
        if (isAttacking)
        {
            return;
        }
        
        // 如果在地面且有向下的速度，重置垂直速度
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f; // 轻微向下的力，确保始终与地面接触
        }
        
        // 获取输入
        float horizontal = Input.GetAxis("Horizontal"); // A/D 或 左/右箭头
        float vertical = Input.GetAxis("Vertical");     // W/S 或 上/下箭头
        
        // 计算移动方向（相对于相机朝向）
        Vector3 cameraForward = playerCamera.transform.forward;
        Vector3 cameraRight = playerCamera.transform.right;
        
        // 忽略Y轴的影响
        cameraForward.y = 0f;
        cameraRight.y = 0f;
        cameraForward.Normalize();
        cameraRight.Normalize();
        
        Vector3 moveDirection = cameraForward * vertical + cameraRight * horizontal;
        
        // 如果有移动输入，让角色面向移动方向
        if (moveDirection.magnitude > 0.1f)
        {
            Quaternion targetRotation = Quaternion.LookRotation(moveDirection);
            playerTransform.rotation = Quaternion.Slerp(playerTransform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
            
            // 设置动画参数
            if (animator != null)
            {
                animator.SetBool("isMoving", true);
            }
        }
        else
        {
            // 设置动画参数
            if (animator != null)
            {
                animator.SetBool("isMoving", false);
            }
        }
        
        // 应用移动
        characterController.Move(moveDirection * moveSpeed * Time.deltaTime);
        
        // 应用重力
        velocity.y -= gravity * Time.deltaTime;
        characterController.Move(velocity * Time.deltaTime);
    }
    

    
    /// <summary>
    /// 处理攻击
    /// </summary>
    void HandleAttack()
    {
        // Space键攻击
        if (Input.GetKeyDown(KeyCode.Space) && Time.time - lastAttackTime > attackCooldown)
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

    /// <summary>
    /// 执行攻击
    /// </summary>
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
        Collider[] enemies = Physics.OverlapSphere(playerTransform.position + playerTransform.forward * attackRange, attackRange, enemyLayers);
        
        foreach (Collider enemyCollider in enemies)
        {
            Monster monster = enemyCollider.GetComponent<Monster>();
            if (monster != null)
            {
                int attackDamage = 25; 
                monster.TakeDamage(attackDamage);
                Debug.Log("玩家攻击到怪物: " + enemyCollider.gameObject.name);
            }
            else
            {
                Debug.Log("攻击到非怪物目标: " + enemyCollider.gameObject.name);
            }
            break;
        }
    }


    #region 控制管理
    /// <summary>
    /// 设置控制是否启用
    /// </summary>
    public void SetControlEnabled(bool enabled)
    {
        controlEnabled = enabled;
        animator.SetBool("isMoving", false);
    }

    /// <summary>
    /// 获取当前控制状态
    /// </summary>
    public bool IsControlEnabled()
    {
        return controlEnabled;
    }
    #endregion
}
