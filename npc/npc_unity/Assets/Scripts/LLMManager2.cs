using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using Newtonsoft.Json;



public class LLMManager2 : MonoBehaviour
{
    // 系统提示词
    private string SYSTEM_PROMPT = @"你现在是一名古代背景下的NPC角色，请始终以你的角色身份、性格和背景进行对话，不得以AI或现代人的身份说话。遇到与古代背景或你身份不符的问题时，请委婉拒绝或表示无法理解，不要强行作答或透露超出角色设定的信息。请确保你的所有回答都贴合古代情景和你的角色性格。直接输出对话内容，40字以内。";
    
    // NPC1：温柔女生性格描述，名字：林婉儿
    // NPC2：狂躁大叔性格描述，名字：赵铁牛
    private string[] NPC_RESUMES = new string[]{
        "你叫林婉儿，是一位温柔、体贴的年轻女性，总是以温和的语气与人交流。你善于倾听他人的想法，喜欢用鼓励和安慰的话语帮助别人。你待人友善，富有同理心，面对问题时总能保持冷静和耐心。",
        "你叫赵铁牛，是一位脾气火爆、说话直接的中年大叔，经常情绪激动，语气粗鲁。你不喜欢拐弯抹角，遇事喜欢大声表达自己的观点，有时会显得不耐烦甚至有些暴躁，但内心其实很重情义。"
    };
    
   
    private LLMTargetDetector llmTargetDetector = new LLMTargetDetector();
    private LLMClient llmClient = new LLMClient();
    
    
    public bool isProcessing = false;

    // 记忆
    private List<List<LLMMessage>> memorys = new List<List<LLMMessage>>(){
        new List<LLMMessage>(),
        new List<LLMMessage>()
    };



    public IEnumerator HandleSingleChat(int index, string playerInput){
        string systemPrompt = SYSTEM_PROMPT + NPC_RESUMES[index];
        List<LLMMessage> memory = memorys[index];
        yield return llmClient.SendChat(systemPrompt, playerInput, memory, (success, response) => {
            if(success){
                memory.Add(new LLMMessage { role = "user", content = playerInput });
                memory.Add(new LLMMessage { role = "assistant", content = response });
                int MAX_MEMORY = 10;
                if (memory.Count > MAX_MEMORY) // 删除旧的
                {
                    int removeCount = memory.Count - MAX_MEMORY;
                    memory.RemoveRange(0, removeCount);
                }
                
                SpeakAction speakAction = new SpeakAction(response);
                GameManager.Instance.npcControllers[index].AddAction(speakAction);
                isProcessing = false;
            }
            else{
                Debug.LogError("HandleSingleChat");
                isProcessing = false;
            }
        });
    }


    public void ProcessChatRequest(RoleTargetType targetType, string playerInput){
        switch (targetType)
        {
            case RoleTargetType.NPC1:
                StartCoroutine(HandleSingleChat(0, playerInput));
                break;
            case RoleTargetType.NPC2:
                StartCoroutine(HandleSingleChat(1, playerInput));
                break;
            case RoleTargetType.Both:
                StartCoroutine(HandleSingleChat(0, playerInput));
                StartCoroutine(HandleSingleChat(1, playerInput));
                break;
            case RoleTargetType.None:
                StartCoroutine(HandleSingleChat(0, playerInput));
                break;
        }
    }


    public IEnumerator LLMProcess(string playerInput) {
        //先判断意图
        yield return llmTargetDetector.DetectTarget(playerInput, (success, targetType) => {
            ProcessChatRequest(targetType, playerInput);
        });
    }

    public void ProcessPlayerInput(string playerInput)
    {
        if (isProcessing)
        {
            return;
        }

        isProcessing = true;

        StartCoroutine(LLMProcess(playerInput));
    }

}









