using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UI : MonoBehaviour
{
    public Model model;
    
    // 头部尺寸
    public float headWidth;
    public float headHeight;
    
    // 鼻子特征
    public float noseWidth;
    public float noseLength;
    
    // 眼部特征
    public float eyeLength;
    public float eyeWidth;
    public float eyeGap;
    
    // 嘴部特征
    public float mouthSize;
    
    // 头发类型
    public int hairType;
    
    // 上一次的值
    private float lastHeadWidth;
    private float lastHeadHeight;
    private float lastNoseWidth;
    private float lastNoseLength;
    private float lastEyeLength;
    private float lastEyeWidth;
    private float lastEyeGap;
    private float lastMouthSize;
    private int lastHairType;

    //生成数据集组件
    public GenDataset genDataset;
    // Start is called before the first frame update
    void Start()
    {
        model = this.GetComponent<Model>();
        genDataset = this.GetComponent<GenDataset>();
    }

    void OnGUI()
    {
        float screenWidth = Screen.width;
        float screenHeight = Screen.height;

        // 创建一个界面区域
        GUILayout.BeginArea(new Rect(20, 20, 300, 600));
        GUILayout.Label("捏脸控制器", GUI.skin.box);

        // 头部尺寸控制
        GUILayout.Space(5);
        GUILayout.Label("头部尺寸", GUI.skin.box);
        
        GUILayout.BeginHorizontal();
        GUILayout.Label("头部宽度: " + headWidth.ToString("F1"), GUILayout.Width(120));
        headWidth = GUILayout.HorizontalSlider(headWidth, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label("头部高度: " + headHeight.ToString("F1"), GUILayout.Width(120));
        headHeight = GUILayout.HorizontalSlider(headHeight, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        // 鼻子特征控制
        GUILayout.Space(5);
        GUILayout.Label("鼻子特征", GUI.skin.box);
        
        GUILayout.BeginHorizontal();
        GUILayout.Label("鼻子宽度: " + noseWidth.ToString("F1"), GUILayout.Width(120));
        noseWidth = GUILayout.HorizontalSlider(noseWidth, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label("鼻子长度: " + noseLength.ToString("F1"), GUILayout.Width(120));
        noseLength = GUILayout.HorizontalSlider(noseLength, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        // 眼部特征控制
        GUILayout.Space(5);
        GUILayout.Label("眼部特征", GUI.skin.box);
        
        GUILayout.BeginHorizontal();
        GUILayout.Label("眼睛长度: " + eyeLength.ToString("F1"), GUILayout.Width(120));
        eyeLength = GUILayout.HorizontalSlider(eyeLength, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label("眼睛宽度: " + eyeWidth.ToString("F1"), GUILayout.Width(120));
        eyeWidth = GUILayout.HorizontalSlider(eyeWidth, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        GUILayout.BeginHorizontal();
        GUILayout.Label("眼间距: " + eyeGap.ToString("F1"), GUILayout.Width(120));
        eyeGap = GUILayout.HorizontalSlider(eyeGap, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        // 嘴部特征控制
        GUILayout.Space(5);
        GUILayout.Label("嘴部特征", GUI.skin.box);
        
        GUILayout.BeginHorizontal();
        GUILayout.Label("嘴巴大小: " + mouthSize.ToString("F1"), GUILayout.Width(120));
        mouthSize = GUILayout.HorizontalSlider(mouthSize, -100, 100, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        // 头发类型选择
        GUILayout.Space(10);
        GUILayout.Label("头发类型", GUI.skin.box);

        GUILayout.BeginHorizontal();
        GUILayout.Label("头发类型: " + hairType.ToString(), GUILayout.Width(120));
        hairType = (int)GUILayout.HorizontalSlider(hairType, 0, 4, GUILayout.Width(150));
        GUILayout.EndHorizontal();

        // 检查是否有任何值发生变化
        if (HasValuesChanged())
        {
            // 创建Data对象并设置数据
            Data data = new Data();
            data.headWidth = (int)headWidth;
            data.headHeight = (int)headHeight;
            data.noseWidth = (int)noseWidth;
            data.noseLength = (int)noseLength;
            data.eyeLength = (int)eyeLength;
            data.eyeWidth = (int)eyeWidth;
            data.eyeGap = (int)eyeGap;
            data.mouthSize = (int)mouthSize;
            data.hairType = hairType;
                
            // 调用model的UpdateFromData方法
            model.UpdateFromData(data);
            
            // 更新上次的值
            UpdateLastValues();
        }

        // 显示面部特征点·
        model.showFacialLandmarks = GUILayout.Toggle(model.showFacialLandmarks, "显示面部特征点");

        // 生成数据集
        if (GUILayout.Button("生成数据集(200)个"))
        {
            genDataset.GenerateDataset(200);
        }

        GUILayout.EndArea();
    }

    private bool HasValuesChanged()
    {
        return headWidth != lastHeadWidth || 
               headHeight != lastHeadHeight ||
               noseWidth != lastNoseWidth ||
               noseLength != lastNoseLength ||
               eyeLength != lastEyeLength ||
               eyeWidth != lastEyeWidth ||
               eyeGap != lastEyeGap ||
               mouthSize != lastMouthSize ||
               hairType != lastHairType;
    }

    private void UpdateLastValues()
    {
        lastHeadWidth = headWidth;
        lastHeadHeight = headHeight;
        lastNoseWidth = noseWidth;
        lastNoseLength = noseLength;
        lastEyeLength = eyeLength;
        lastEyeWidth = eyeWidth;
        lastEyeGap = eyeGap;
        lastMouthSize = mouthSize;
        lastHairType = hairType;
    }
}