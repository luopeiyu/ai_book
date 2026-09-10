using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;


public enum IntentType{
    Chat,       // 闲聊对话
    Action      // 动作指令
}

public class IntentResult{
    public RoleTargetType targetType;
    public IntentType intentType;
}


public class LLMIntentDetector{
    private LLMClient llmClient = new LLMClient();
    private string INTENT_DETECTION_PROMPT = @"请分析玩家的输入，判断两个信息：

1. 目标对象（谁）：游戏中有两个NPC：林婉儿和赵铁牛
- NPC1：如果是在跟林婉儿说话（包含林婉儿、婉儿、女生、姑娘等称呼，或温柔相关的内容）
- NPC2：如果是在跟赵铁牛说话（包含赵铁牛、铁牛、大叔、大哥等称呼，或直接粗暴的内容）  
- Both：如果是在跟两个人说话（包含大家、你们、所有人等称呼）
- None：如果没有明确指向任何NPC（普通闲聊或不确定的内容）

2. 意图类型（做什么）：
- Chat：闲聊对话（问候、聊天、询问等）
- Action：动作指令（移动、攻击、拾取、跟随等具体行为）

请严格按照以下格式回复：
目标：[NPC1/NPC2/Both/None]
意图：[Chat/Action]

玩家输入：";


    private IntentResult DetectByResponse(string response)
    {
        IntentResult result = new IntentResult();
        if(response.Contains("Action"))
            result.intentType = IntentType.Action;
        else if(response.Contains("Chat"))
            result.intentType = IntentType.Chat;
        else
            result.intentType = IntentType.Chat;
            
            
        if(response.Contains("NPC1"))
            result.targetType = RoleTargetType.NPC1;
        else if(response.Contains("NPC2"))
            result.targetType = RoleTargetType.NPC2;
        else if(response.Contains("Both"))
            result.targetType = RoleTargetType.Both;
        else
            result.targetType = RoleTargetType.None;
            
        return result;
    }


    public IEnumerator DetectIntent(string userInput, Action<bool,IntentResult> callback){
        string prompt = INTENT_DETECTION_PROMPT + userInput;
        yield return llmClient.SendChat("", prompt, null, (success, response) => {
            if(success){
                IntentResult result = DetectByResponse(response);
                callback(true, result);
            }
            else{
                IntentResult result = new IntentResult();
                result.targetType = RoleTargetType.None;
                result.intentType = IntentType.Chat;
                callback(false, result);
            }
        });
    }

}