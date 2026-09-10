using System.Collections;
using System.Collections.Generic;
using UnityEngine;





public class LLMToolManager
{
    
    private List<BaseLLMTool> tools = new List<BaseLLMTool>();
    
    public LLMToolManager(){
        tools.Add(new GoToTool());
        tools.Add(new GoToAndPickTool());
        tools.Add(new GoToAndAutoAttackTool());
        tools.Add(new FollowPlayerTool());
        tools.Add(new SwitchToAttackStateTool());
        tools.Add(new IdleTool());
        tools.Add(new SpeakTool());
    }
    
    public string GetSceneInfo()
    {
        string sceneInfo = "";
        
        Vector3 playerPos = GameManager.Instance.playerController.transform.position;
        sceneInfo += "角色位置：x=" + playerPos.x.ToString("F2") + " y=" + playerPos.y.ToString("F2") + " z=" + playerPos.z.ToString("F2") + "\n";
        
        for(int i = 0; i < GameManager.Instance.npcControllers.Length; i++){
            NpcController npc = GameManager.Instance.npcControllers[i];
            Vector3 npcPos = npc.transform.position;
            sceneInfo += "NPC[" + i + "]位置：x=" + npcPos.x.ToString("F2") + " y=" + npcPos.y.ToString("F2") + " z=" + npcPos.z.ToString("F2") + "\n";
        }
        foreach(Monster monster in GameManager.Instance.monsterManager.monsters.Values){
            Vector3 monsterPos = monster.transform.position;
            sceneInfo += "妖怪[" + monster.id + "]位置：x=" + monsterPos.x.ToString("F2") + " y=" + monsterPos.y.ToString("F2") + " z=" + monsterPos.z.ToString("F2") + "\n";
        }
        
        Item[] items = GameObject.FindObjectsOfType<Item>();
        foreach(Item item in items){
            Vector3 itemPos = item.transform.position;
            sceneInfo += "物品[" + item.itemName + "]位置：x=" + itemPos.x.ToString("F2") + " y=" + itemPos.y.ToString("F2") + " z=" + itemPos.z.ToString("F2") + "\n";
        }
        //Debug.Log("sceneInfo: " + sceneInfo);

        return sceneInfo;
    }
    
    
    public string GetToolDescString(){
        string toolDescString = "[";
        for(int i = 0; i < tools.Count; i++){
            toolDescString += tools[i].GetDescription();
            if(i < tools.Count - 1){
                toolDescString += ",";
            }
        }
        toolDescString += "]";
        return toolDescString;
    }
    
    public void RunTool(int index, string toolName, string arguments){
        
        BaseLLMTool tool = tools.Find(tool => tool.GetName() == toolName);
        if(tool == null){
            Debug.LogError("Tool not found: " + toolName);
            return;
        }
        
        tool.Run(index, arguments);
    }
}
