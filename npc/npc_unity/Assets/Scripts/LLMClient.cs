using UnityEngine;
using UnityEngine.Networking;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.Text;
using System.Collections.Generic;
using System;
using System.Collections;

// LLM API数据结构
[System.Serializable]
public class Function
{
    public string name;
    public string arguments;
}

[System.Serializable]
public class ToolCall
{
    public string type;
    public Function function;
}

[System.Serializable]
public class LLMMessage
{
    public string role;
    public string content;
    [JsonProperty("tool_calls")]
    public ToolCall[] tool_calls;  
}

[System.Serializable]
public class LLMRequest
{
    public string model;
    public LLMMessage[] messages;
    public object tools;
}

[System.Serializable]
public class LLMChoice
{
    public LLMMessage message;
    public string finish_reason;
}

[System.Serializable]
public class LLMResponse
{
    public LLMChoice[] choices;
}




class LLMClient
{
    public string baseUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions";
    public string apiKey = "sk-123456";  // 需要替换为实际的API Key
    
    
    public IEnumerator SendRequest(LLMRequest request, Action<bool,LLMResponse> callback) {
        string jsonData = JsonConvert.SerializeObject(request);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        
        using (UnityWebRequest www = new UnityWebRequest(baseUrl, "POST")){
            www.uploadHandler = new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");
            www.SetRequestHeader("Authorization", $"Bearer {apiKey}");
            
            yield return www.SendWebRequest();
            if (www.result == UnityWebRequest.Result.Success)
            {
                string responseText = www.downloadHandler.text;
                Debug.Log($"API响应: {responseText}");
                
                LLMResponse response = JsonConvert.DeserializeObject<LLMResponse>(responseText);
                callback(true, response);
            }
            else
            {
                Debug.LogError($"API调用失败: {www.error}");
                callback(false, null);
            }
        }
        
    }
    
    public IEnumerator SendChat(string systemPrompt, string userInput, List<LLMMessage> memory = null, Action<bool, string> callback=null) {
        List<LLMMessage> messages = new List<LLMMessage>();
        //system prompt
        if (systemPrompt != "")
        {
            messages.Add(new LLMMessage { role = "system", content = systemPrompt });
        }
        //memory
        if (memory != null)
        {
            messages.AddRange(memory);
        }
        //user input
        messages.Add(new LLMMessage { role = "user", content = userInput });

        //request
        LLMRequest request = new LLMRequest
        {
            model = "qwen-turbo",
            messages = messages.ToArray()
        };
        
        yield return SendRequest(request, (success, response) => {
            if(success){
                callback(true, response.choices[0].message.content);
            }
            else{
                callback(false, "");
            }
        });
    }
    
    public IEnumerator SendFunctionCall(string systemPrompt, string userInput,string toolsJsonString, Action<bool,LLMMessage> callback){
        List<LLMMessage> messages = new List<LLMMessage>();
        //system prompt
        if (systemPrompt != "")
        {
            messages.Add(new LLMMessage { role = "system", content = systemPrompt });
        }
        //user input
        messages.Add(new LLMMessage { role = "user", content = userInput });
        //request
        LLMRequest request = new LLMRequest
        {
            model = "qwen-turbo",
            messages = messages.ToArray(),
            tools = JsonConvert.DeserializeObject(toolsJsonString)
        };

        yield return SendRequest(request, (success, response) => {
            if(success){
                callback(true, response.choices[0].message);
            }
            else{
                callback(false, null);
            }
        });
    }

}




