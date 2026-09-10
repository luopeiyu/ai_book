using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

    /// <summary>
    /// UI管理器 - 管理所有UI元素，特别是对话框系统
    /// </summary>
public class UIManager : MonoBehaviour
{
    public Button sendButton;                       // 发送按钮
    public TMP_InputField chatInputField;           // 聊天输入框（TMP版）
    public Transform[] npcDialogs = new Transform[2];                 
    private TextMeshProUGUI[] npcTexts = new TextMeshProUGUI[2];

    private float[] startTimes = new float[2];

    // 私有变量
    private List<Queue<string>> messageQueues = new List<Queue<string>>(){
        new Queue<string>(),
        new Queue<string>()
    };
    
    //
    private float MESSAGE_DISPLAY_DURATION = 3.0f;
    void Start()
    {
        npcTexts[0] = npcDialogs[0].GetComponentInChildren<TextMeshProUGUI>();
        npcTexts[1] = npcDialogs[1].GetComponentInChildren<TextMeshProUGUI>();

        npcDialogs[0].gameObject.SetActive(false);
        npcDialogs[1].gameObject.SetActive(false);
        sendButton.onClick.AddListener(OnSendButtonClick);
        

        // 监听输入框获得焦点和失去焦点事件
        chatInputField.onSelect.AddListener((string text) => {
            GameManager.Instance.SetPlayerControllable(false);
        });
        chatInputField.onDeselect.AddListener((string text) => {
            GameManager.Instance.SetPlayerControllable(true);
        });

        // 监听输入框回车键（确定键）发送
        chatInputField.onSubmit.AddListener((string text) => {
            OnSendButtonClick();
        });
    }



    void Update()
    {
        for(int i = 0; i < npcDialogs.Length; i++){
            UpdateDialog(i);
        }
    }
    
    void UpdateDialog(int index)
    {
        if(Time.time - startTimes[index] > MESSAGE_DISPLAY_DURATION){
            if (messageQueues[index].Count > 0)
            {
                npcTexts[index].text = messageQueues[index].Dequeue();
                startTimes[index] = Time.time;
                npcDialogs[index].gameObject.SetActive(true);
            }
            else
            {
                npcDialogs[index].gameObject.SetActive(false);
            }
        }
        else{
            Vector3 npcCanvasPos = GameManager.Instance.GetNPCCanvasPosition(index);
            npcDialogs[index].transform.position = npcCanvasPos;
        }
    }


    public void NPCSpeak(int index, string message)
    {
        messageQueues[index].Enqueue(message);
    }
    

    public void OnSendButtonClick()
    {
        /*
        string message = chatInputField.text;
        string npcMessage = message + "吗？";
        NPC1Speak(npcMessage);
        */

        /*
        GameObject cube1 = GameObject.Find("Cube (1)");
        Vector3 targetPosition = cube1.transform.position;
        MoveAction moveAction = new MoveAction(targetPosition);
        GameManager.Instance.npcController1.AddAction(moveAction);

        SpeakAction speakAction = new SpeakAction("我移动到了");
        GameManager.Instance.npcController1.AddAction(speakAction);

        */

        /*
        SpeakAction speakAction = new SpeakAction("准备行动");
        GameManager.Instance.npcController2.AddAction(speakAction);
        
        GameObject item = GameObject.Find("item1_sword");
        Vector3 targetPosition = item.transform.position;
        MoveAction moveAction = new MoveAction(targetPosition);
        GameManager.Instance.npcController2.AddAction(moveAction);

        PickAction pickAction = new PickAction();
        GameManager.Instance.npcController2.AddAction(pickAction);
        */
        
        /*
        if(chatInputField.text == "1"){
            //GameManager.Instance.npcController1.toFollow = true;
            GameManager.Instance.npcController1.toAutoAttack = true;
        }
        else{
            GameObject item = GameObject.Find("item1_sword");
            Vector3 targetPosition = item.transform.position;
            MoveAction moveAction = new MoveAction(targetPosition);
            GameManager.Instance.npcController1.AddAction(moveAction);

            PickAction pickAction = new PickAction();
            GameManager.Instance.npcController1.AddAction(pickAction);
        }
        */
        if(GameManager.Instance.llmManager.isProcessing){
            return;
        }
        
        GameManager.Instance.llmManager.ProcessPlayerInput(chatInputField.text);
        
        chatInputField.text = "";
    }
}   