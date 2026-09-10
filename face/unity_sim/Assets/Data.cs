using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Data
{
    // 头部尺寸
    public int headWidth;    // Head_Width_Wide / Head_Width_Narrow
    public int headHeight;   // Head_Height_Wide / Head_Height_Narrow

    // 鼻子特征
    public int noseWidth;    // Nose_Width_Wide / Nose_Width_Narrow
    public int noseLength;   // Nose_Length_Wide / Nose_Length_Narrow

    // 眼部特征
    public int eyeLength;    // Eye_Length_Wide / Eye_Length_Narrow
    public int eyeWidth;     // Eye_Width_Wide / Eye_Width_Narrow
    public int eyeGap;       // Eye_Gap_Wide / Eye_Gap_Narrow

    // 嘴部特征
    public int mouthSize;    // Mouth_Size_Wide / Mouth_Size_Narrow

    // 头发类型
    public int hairType;

    // 构造函数
    public Data()
    {
        headWidth = 0;
        headHeight = 0;
        noseWidth = 0;
        noseLength = 0;
        eyeLength = 0;
        eyeWidth = 0;
        eyeGap = 0;
        mouthSize = 0;
        hairType = 0;
    }

    // 将对象转换为JSON字符串
    public string ToJson()
    {
        return JsonUtility.ToJson(this, true);
    }

    // 从JSON字符串创建Data对象
    public static Data FromJson(string json)
    {
        try
        {
            return JsonUtility.FromJson<Data>(json);
        }
        catch (System.Exception e)
        {
            Debug.LogError("解析JSON失败: " + e.Message);
            return new Data(); // 返回默认值
        }
    }
    
    public static Data RandomGenData()
    {
        Data data = new Data();
        //data.headWidth = Random.Range(-100, 100);
        data.headHeight = Random.Range(-100, 100);
        data.noseWidth = 0;//Random.Range(-100, 100);
        data.noseLength = Random.Range(-100, 100);
        data.eyeLength = Random.Range(-100, 100);
        data.eyeWidth = Random.Range(-100, 100);
        data.eyeGap = 0; //Random.Range(-100, 100);
        data.mouthSize = Random.Range(-100, 100);
        data.hairType = Random.Range(0, 5);
        
        
        return data;
    }
}
