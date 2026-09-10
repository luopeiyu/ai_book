using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;

public enum RoleTargetType
{
    None,   // 没有呼叫任何NPC
    NPC1,   // 呼叫NPC1
    NPC2,    // 呼叫NPC2
    Both,    // 呼叫NPC1和NPC2
}


public class LLMTargetDetector{
    private LLMClient llmClient = new LLMClient();
    private string TARGET_DETECTION_PROMPT = @"请分析玩家的输入，判断他在跟谁说话。游戏中有两个NPC：林婉儿和赵铁牛。
请只回复以下其中一个选项：
- NPC1：如果是在跟林婉儿说话（包含林婉儿、婉儿、女生、姑娘等称呼，或温柔相关的内容）
- NPC2：如果是在跟赵铁牛说话（包含赵铁牛、铁牛、大叔、大哥等称呼，或直接粗暴的内容）  
- Both：如果是在跟两个人说话（包含大家、你们、所有人等称呼）
- None：如果没有明确指向任何NPC（普通闲聊或不确定的内容）

玩家输入：";

    private RoleTargetType DetectByResponse(string response){
        if(response.Contains("NPC1"))
            return RoleTargetType.NPC1;
        else if(response.Contains("NPC2"))
            return RoleTargetType.NPC2;
        else if(response.Contains("Both"))
            return RoleTargetType.Both;
        else
            return RoleTargetType.None;
    }

    public IEnumerator DetectTarget(string userInput, Action<bool,RoleTargetType> callback){
        string prompt = TARGET_DETECTION_PROMPT + userInput;
        yield return llmClient.SendChat("", prompt, null, (success, response) => {
            if(success){
                RoleTargetType targetType = DetectByResponse(response);
                callback(true, targetType);
            }else{
                callback(false, RoleTargetType.None);
            }
        });
    }
}