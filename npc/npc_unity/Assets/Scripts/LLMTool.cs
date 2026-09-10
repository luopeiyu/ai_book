using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

public class BaseLLMTool
{
    public virtual string GetName()
    {
        return "BaseLLMTool";
    }

    public virtual string GetDescription()
    {
        return "BaseLLMTool Description";
    }

    public virtual void Run(int index, string arguments)
    {
        Debug.Log("BaseLLMTool Run");
    }
}


    
public class GoToTool : BaseLLMTool
{
    public override string GetName()
    {
        return "GoTo";
    }

    public override string GetDescription()
    {
        return @"{
            ""type"": ""function"",
            ""function"": {
                ""name"": ""GoTo"",
                ""description"": ""让NPC走到指定坐标位置"",
                ""parameters"": {
                    ""type"": ""object"",
                    ""properties"": {
                        ""x"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的X坐标""
                        },
                        ""y"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的Y坐标""
                        },
                        ""z"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的Z坐标""
                        }
                    },
                    ""required"": [""x"", ""y"", ""z""]
                }
            }
        }";
    }

    public override void Run(int index, string arguments)
    {
        Vector3 targetPosition = new Vector3(0, 0, 0);
        try
        {
            var argumentsDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(arguments);
            float x = Convert.ToSingle(argumentsDict["x"]);
            float y = Convert.ToSingle(argumentsDict["y"]);
            float z = Convert.ToSingle(argumentsDict["z"]);
            targetPosition = new Vector3(x, y, z);
        }
        catch (Exception e)
        {
            Debug.Log($"GoToTool: 解析失败: {e.Message}");
            return;
        }

        NpcController npc = GameManager.Instance.npcControllers[index];
        npc.ClearActionQueue();
        npc.AddAction(new SpeakAction("出发"));
        npc.AddAction(new MoveAction(targetPosition));
    }
}

public class GoToAndPickTool : BaseLLMTool
{
    public override string GetName()
    {
        return "GoToAndPick";
    }

    public override string GetDescription()
    {
        return @"{
            ""type"": ""function"",
            ""function"": {
                ""name"": ""GoToAndPick"",
                ""description"": ""让NPC走到指定坐标并拾取物品"",
                ""parameters"": {
                    ""type"": ""object"",
                    ""properties"": {
                        ""x"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的X坐标""
                        },
                        ""y"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的Y坐标""
                        },
                        ""z"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的Z坐标""
                        }
                    },
                    ""required"": [""x"", ""y"", ""z""]
                }
            }
        }";
    }

    public override void Run(int index, string arguments)
    {
        Vector3 targetPosition = new Vector3(0, 0, 0);
        try
        {
            var argumentsDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(arguments);
            float x = Convert.ToSingle(argumentsDict["x"]);
            float y = Convert.ToSingle(argumentsDict["y"]);
            float z = Convert.ToSingle(argumentsDict["z"]);
            targetPosition = new Vector3(x, y, z);
        }
        catch (Exception e)
        {
            Debug.Log($"GoToAndPickTool: 解析失败: {e.Message}");
            return;
        }

        NpcController npc = GameManager.Instance.npcControllers[index];
        npc.ClearActionQueue();
        npc.AddAction(new SpeakAction("去拾取物品"));
        npc.AddAction(new MoveAction(targetPosition));
        npc.AddAction(new PickAction());
    }
}

public class GoToAndAutoAttackTool : BaseLLMTool
{
    public override string GetName()
    {
        return "GoToAndAutoAttack";
    }

    public override string GetDescription()
    {
        return @"{
            ""type"": ""function"",
            ""function"": {
                ""name"": ""GoToAndAutoAttack"",
                ""description"": ""让NPC走到指定坐标并开始攻击"",
                ""parameters"": {
                    ""type"": ""object"",
                    ""properties"": {
                        ""x"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的X坐标""
                        },
                        ""y"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的Y坐标""
                        },
                        ""z"": {
                            ""type"": ""number"",
                            ""description"": ""目标位置的Z坐标""
                        }
                    },
                    ""required"": [""x"", ""y"", ""z""]
                }
            }
        }";
    }

    public override void Run(int index, string arguments)
    {
        Vector3 targetPosition = new Vector3(0, 0, 0);
        try
        {
            var argumentsDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(arguments);
            float x = Convert.ToSingle(argumentsDict["x"]);
            float y = Convert.ToSingle(argumentsDict["y"]);
            float z = Convert.ToSingle(argumentsDict["z"]);
            targetPosition = new Vector3(x, y, z);
        }
        catch (Exception e)
        {
            Debug.Log($"GoToAndAutoAttackTool: 解析失败: {e.Message}");
            return;
        }

        NpcController npc = GameManager.Instance.npcControllers[index];
        npc.ClearActionQueue();
        npc.AddAction(new SpeakAction("去攻击"));
        npc.AddAction(new MoveAction(targetPosition));
        npc.AddAction(new AutoAttackAction());
    }
}

public class FollowPlayerTool : BaseLLMTool
{
    public override string GetName()
    {
        return "FollowPlayer";
    }

    public override string GetDescription()
    {
        return @"{
            ""type"": ""function"",
            ""function"": {
                ""name"": ""FollowPlayer"",
                ""description"": ""让NPC跟随玩家移动"",
                ""parameters"": {
                    ""type"": ""object"",
                    ""properties"": {},
                    ""required"": []
                }
            }
        }";
    }

    public override void Run(int index, string arguments)
    {
        NpcController npc = GameManager.Instance.npcControllers[index];
        npc.ClearActionQueue();
        npc.AddAction(new SpeakAction("我跟着你走"));
        npc.AddAction(new FollowAction());
    }
}

public class SwitchToAttackStateTool : BaseLLMTool
{
    public override string GetName()
    {
        return "SwitchToAttackState";
    }

    public override string GetDescription()
    {
        return @"{
            ""type"": ""function"",
            ""function"": {
                ""name"": ""SwitchToAttackState"",
                ""description"": ""让NPC切换到攻击状态"",
                ""parameters"": {
                    ""type"": ""object"",
                    ""properties"": {},
                    ""required"": []
                }
            }
        }";
    }

    public override void Run(int index, string arguments)
    {
        NpcController npc = GameManager.Instance.npcControllers[index];
        npc.ClearActionQueue();
        npc.AddAction(new SpeakAction("让我看看周围有哪些妖怪"));
        npc.AddAction(new AutoAttackAction());
    }
}

public class IdleTool : BaseLLMTool
{
    public override string GetName()
    {
        return "Idle";
    }

    public override string GetDescription()
    {
        return @"{
            ""type"": ""function"",
            ""function"": {
                ""name"": ""Idle"",
                ""description"": ""让NPC停止当前动作，原地待机"",
                ""parameters"": {
                    ""type"": ""object"",
                    ""properties"": {},
                    ""required"": []
                }
            }
        }";
    }

    public override void Run(int index, string arguments)
    {
        NpcController npc = GameManager.Instance.npcControllers[index];
        npc.ClearActionQueue();
        npc.AddAction(new SpeakAction("我休息一下"));
        npc.AddAction(new IdelAction());
    }
}

public class SpeakTool : BaseLLMTool
{
    public override string GetName()
    {
        return "Speak";
    }

    public override string GetDescription()
    {
        return @"{
            ""type"": ""function"",
            ""function"": {
                ""name"": ""Speak"",
                ""description"": ""让NPC说出指定的话语"",
                ""parameters"": {
                    ""type"": ""object"",
                    ""properties"": {
                        ""message"": {
                            ""type"": ""string"",
                            ""description"": ""NPC要说的话""
                        }
                    },
                    ""required"": [""message""]
                }
            }
        }";
    }

    public override void Run(int index, string arguments)
    {
        string message = "";
        try
        {
            var argumentsDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(arguments);
            message = argumentsDict["message"].ToString();
        }
        catch (Exception e)
        {
            Debug.Log($"SpeakTool: 解析失败: {e.Message}");
            return;
        }

        NpcController npc = GameManager.Instance.npcControllers[index];
        npc.ClearActionQueue();
        npc.AddAction(new SpeakAction(message));
    }
}