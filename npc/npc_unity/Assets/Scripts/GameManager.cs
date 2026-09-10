using UnityEngine;
using UnityEngine.UI;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    // 管理器
    public UIManager uiManager;
    public LLMManager3 llmManager;
    public MonsterManager monsterManager;
    public PlayerController playerController;
    public NpcController[] npcControllers;
    public LLMToolManager llmToolManager;
    void Awake()
    {
        // 单例
        Instance = this;

        // 初始化所有管理器
        uiManager = transform.GetComponent<UIManager>();
        llmManager = transform.gameObject.AddComponent<LLMManager3>();
        llmToolManager = new LLMToolManager();
        playerController = transform.GetComponent<PlayerController>();
        monsterManager = transform.GetComponent<MonsterManager>();
        //npc controller直接赋值

    }


    public void SetPlayerControllable(bool isControllable)
    {
        playerController.SetControlEnabled(isControllable);
    }

    public Vector3 GetNPCCanvasPosition(int index)
    {
        Camera camera = playerController.playerCamera;
        return camera.WorldToScreenPoint(npcControllers[index].npcTransform.position + new Vector3(0,2,0));
    }



}
