using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using Newtonsoft.Json;
using System.Threading.Tasks;



public class LLMManager1 : MonoBehaviour
{
    private LLMClient llmClient = new LLMClient();
    public bool isProcessing = false;
    public  void ProcessPlayerInput(string playerInput)
    {
        LLMRequest request = new LLMRequest{
            model = "qwen-turbo",
            messages = new LLMMessage[] {
                 new LLMMessage { role = "user", content = playerInput } 
            }
        };

        StartCoroutine(llmClient.SendRequest(request, (success, resp) => {
            if(success){
                string content = resp.choices[0].message.content;
                SpeakAction action = new SpeakAction(content);
                NpcController npc = GameManager.Instance.npcControllers[0];
                npc.AddAction(action);
            }
        }));
    }
}








