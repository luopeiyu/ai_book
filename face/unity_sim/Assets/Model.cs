using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Model : MonoBehaviour
{
    // 引用 SkinnedMeshRenderer 组件
    public GameObject faceObject;
    private SkinnedMeshRenderer skinnedMeshRenderer;
    
    // 头部尺寸索引（正负分开）
    private int headWidthWideIndex;
    private int headWidthNarrowIndex;
    private int headHeightWideIndex;
    private int headHeightNarrowIndex;
    
    // 鼻子特征索引
    private int noseWidthWideIndex;
    private int noseWidthNarrowIndex;
    private int noseLengthWideIndex;
    private int noseLengthNarrowIndex;
    
    // 眼部特征索引
    private int eyeLengthWideIndex;
    private int eyeLengthNarrowIndex;
    private int eyeWidthWideIndex;
    private int eyeWidthNarrowIndex;
    private int eyeGapWideIndex;
    private int eyeGapNarrowIndex;
    
    // 嘴部特征索引
    private int mouthSizeWideIndex;
    private int mouthSizeNarrowIndex;
    
    // 引用头发游戏对象
    public GameObject[] hairObjects;

    //头发的自适应变换
    public HairTransformData[] hairTransformDatas = new HairTransformData[] {
        new HairTransformData(0.6f, 1.15f, 0.65f, 1.32f, 0f, 0f),
        new HairTransformData(0.6f, 1.15f, 0.65f, 1.32f, 0f, 0f),
        new HairTransformData(0.6f, 1.15f, 0.65f, 1.32f, 0f, 0f),
        new HairTransformData(0.7f, 1.35f, 0.65f, 1.32f, 0f, 0f),
        new HairTransformData(0.7f, 1.28f, 0.65f, 1.32f, 0f, 0f)
    };

    // 面部特征点
    public int[] facialLandmarks = new int[] {
        79,1476,1454,
        1786,1836,1825,1855,
        1389,1426,
        2056,
        1445
    };


    // 是否显示面部特征点
    public bool showFacialLandmarks = false;




    public void Start()
    {
        // 获取 SkinnedMeshRenderer 组件
        faceObject = this.gameObject.transform.Find("face_8_dim").gameObject;
        skinnedMeshRenderer = faceObject.GetComponent<SkinnedMeshRenderer>();

        // 获取所有混合形状索引
        InitializeBlendShapeIndices();

        // 获取头发游戏对象
        GameObject hairObject1 = this.gameObject.transform.Find("hair1").gameObject;
        GameObject hairObject2 = this.gameObject.transform.Find("hair2").gameObject;
        GameObject hairObject3 = this.gameObject.transform.Find("hair3").gameObject;
        GameObject hairObject4 = this.gameObject.transform.Find("hair4").gameObject;
        GameObject hairObject5 = this.gameObject.transform.Find("hair5").gameObject;
        this.hairObjects = new GameObject[] { hairObject1, hairObject2, hairObject3, hairObject4, hairObject5 };

        // 初始化头发游戏对象
        foreach (GameObject hairObject in hairObjects)
        {
            hairObject.SetActive(false);
        }
        hairObjects[0].SetActive(true);

        
    }

    private void InitializeBlendShapeIndices()
    {
        // 头部尺寸
        headWidthWideIndex = GetBlendShapeIndex("Head Width_Wide");
        headWidthNarrowIndex = GetBlendShapeIndex("Head Width_Narrow");
        headHeightWideIndex = GetBlendShapeIndex("Head Height_Wide");
        headHeightNarrowIndex = GetBlendShapeIndex("Head Height_Narrow");
        
        // 鼻子特征
        noseWidthWideIndex = GetBlendShapeIndex("Nose Width_Wide");
        noseWidthNarrowIndex = GetBlendShapeIndex("Nose Width_Narrow");
        noseLengthWideIndex = GetBlendShapeIndex("Nose Length_Wide");
        noseLengthNarrowIndex = GetBlendShapeIndex("Nose Length_Narrow");
        
        // 眼部特征
        eyeLengthWideIndex = GetBlendShapeIndex("Eye Length_Wide");
        eyeLengthNarrowIndex = GetBlendShapeIndex("Eye Length_Narrow");
        eyeWidthWideIndex = GetBlendShapeIndex("Eye Width_Wide");
        eyeWidthNarrowIndex = GetBlendShapeIndex("Eye Width_Narrow");
        eyeGapWideIndex = GetBlendShapeIndex("Eye Gap_Wide");
        eyeGapNarrowIndex = GetBlendShapeIndex("Eye Gap_Narrow");
        
        // 嘴部特征
        mouthSizeWideIndex = GetBlendShapeIndex("Mouth Size_Wide");
        mouthSizeNarrowIndex = GetBlendShapeIndex("Mouth Size_Narrow");
    }

    private int GetBlendShapeIndex(string shapeName)
    {
        int index = skinnedMeshRenderer.sharedMesh.GetBlendShapeIndex(shapeName);
        if (index == -1)
        {
            Debug.LogWarning($"找不到名为 '{shapeName}' 的混合形状");
        }
        return index;
    }

    private void SetBlendShapeValue(int wideIndex, int narrowIndex, int value)
    {
        if (value >= 0)
        {
            if (wideIndex != -1) skinnedMeshRenderer.SetBlendShapeWeight(wideIndex, value);
            if (narrowIndex != -1) skinnedMeshRenderer.SetBlendShapeWeight(narrowIndex, 0);
        }
        else
        {
            if (wideIndex != -1) skinnedMeshRenderer.SetBlendShapeWeight(wideIndex, 0);
            if (narrowIndex != -1) skinnedMeshRenderer.SetBlendShapeWeight(narrowIndex, -value);
        }
    }

    public void UpdateFromData(Data data)
    {
        //做一些变换使数据更合理
        data.headWidth = (int)(data.headWidth * 0.8f);
        data.headHeight = (int)(data.headHeight * 0.7f);
        data.noseWidth = (int)(data.noseWidth * 0.7f);
        data.noseLength = (int)(data.noseLength * 0.9f);
        data.eyeLength = (int)(data.eyeLength * 0.7f);
        data.eyeWidth = (int)(data.eyeWidth * 0.8f);
        data.eyeGap = (int)(data.eyeGap * 0.7f);
        data.mouthSize = (int)(data.mouthSize * 0.8f);
        
        // 更新所有面部BlendShape参数
        SetBlendShapeValue(headWidthWideIndex, headWidthNarrowIndex, data.headWidth);
        SetBlendShapeValue(headHeightWideIndex, headHeightNarrowIndex, data.headHeight);
        SetBlendShapeValue(noseWidthWideIndex, noseWidthNarrowIndex, data.noseWidth);
        SetBlendShapeValue(noseLengthWideIndex, noseLengthNarrowIndex, data.noseLength);
        SetBlendShapeValue(eyeLengthWideIndex, eyeLengthNarrowIndex, data.eyeLength);
        SetBlendShapeValue(eyeWidthWideIndex, eyeWidthNarrowIndex, data.eyeWidth);
        SetBlendShapeValue(eyeGapWideIndex, eyeGapNarrowIndex, data.eyeGap);
        SetBlendShapeValue(mouthSizeWideIndex, mouthSizeNarrowIndex, data.mouthSize);
        
        // 更新头发游戏对象
        foreach (GameObject o in hairObjects)
        {
            o.SetActive(false);
        }
        hairObjects[data.hairType].SetActive(true);
        // 更新头发游戏对象的缩放和位置（基于头部尺寸）
        HairTransformData hairData = hairTransformDatas[data.hairType];
        GameObject hairObject = hairObjects[data.hairType];
        float localScaleX = 1;
        float localScaleY = 1;
        float localPositionY = 0;
        
        if (data.headWidth < 0)
        {
            localScaleX = 1 + (hairData.headWidthMinScale - 1) * data.headWidth / -100;
        }
        else
        {
            localScaleX = 1 + (hairData.headWidthMaxScale - 1) * data.headWidth / 100;
        }
        
        if (data.headHeight < 0)
        {
            localScaleY = 1 + (hairData.headHeightMinScale - 1) * data.headHeight / -100;
            localPositionY = hairData.headHeightMinPosition * data.headHeight / -100;
        }
        else
        {
            localScaleY = 1 + (hairData.headHeightMaxScale - 1) * data.headHeight / 100;
            localPositionY = hairData.headHeightMaxPosition * data.headHeight / 100;
        }
        
        hairObject.transform.localScale = new Vector3(localScaleX, localScaleY, 1);
        hairObject.transform.localPosition = new Vector3(0, localPositionY, 0);
    }

    // Update is called once per frame

    public Vector3[] GetFacialLandmarks()
    {
        Vector3[] landmarks = new Vector3[facialLandmarks.Length];
        Mesh bakedMesh = new Mesh();
        skinnedMeshRenderer.BakeMesh(bakedMesh);
        for (int i = 0; i < facialLandmarks.Length; i++)
        {
            int vertexIndex = facialLandmarks[i];
            Vector3 vertexLocalPos = bakedMesh.vertices[vertexIndex];
            Vector3 vertexWorldPos = faceObject.transform.TransformPoint(vertexLocalPos);
            landmarks[i] = vertexWorldPos;
        }
        Destroy(bakedMesh);
        return landmarks;
    }


    public Vector2[] GetFacialLandmarks2D()
    {
        Vector3[] landmarks = GetFacialLandmarks();
        float noraml_image_width = 512;
        float noraml_image_height = 512;
        // 转换为2D屏幕坐标
        Vector2[] landmarks2D = new Vector2[landmarks.Length];
        for (int i = 0; i < landmarks.Length; i++)
        {
            Vector3 screenPoint = Camera.main.WorldToScreenPoint(landmarks[i]);
            // Unity的屏幕坐标原点在左下角，转换为左上角坐标系
            float normalizedX = screenPoint.x / Screen.width;
            float normalizedY = (Screen.height - screenPoint.y) / Screen.height;
            landmarks2D[i] = new Vector2(Mathf.RoundToInt(normalizedX * noraml_image_width), Mathf.RoundToInt(normalizedY * noraml_image_height));
        }
        
        return landmarks2D;
    }

    public string GetFacialLandmarks2DJson()
    {
        Vector2[] landmarks2D = GetFacialLandmarks2D();
        string jsonContent = "[\n";
        for (int k = 0; k < landmarks2D.Length; k++)
        {
            jsonContent += $"    {{\"x\": {Mathf.RoundToInt(landmarks2D[k].x)}, \"y\": {Mathf.RoundToInt(landmarks2D[k].y)}}}";
            if (k < landmarks2D.Length - 1)
            {
                jsonContent += ",";
            }
            jsonContent += "\n";
        }
        jsonContent += "]";
        return jsonContent;
    }


    public void DisplayFacialLandmarks()
    {
        
        Vector3[] landmarks = GetFacialLandmarks();
        for (int i = 0; i < landmarks.Length; i++)
        {
            Gizmos.color = Color.red;
            Gizmos.DrawSphere(landmarks[i], 0.005f);
        }
    }
    
    void OnDrawGizmos()
    {
        if (Application.isPlaying && showFacialLandmarks)
        {
            DisplayFacialLandmarks();
        }
    }
    
    void Update()
    {

    }
}
