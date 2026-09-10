using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class GenDataset : MonoBehaviour
{
    [Header("数据集生成设置")]
    public Camera screenshotCamera;
    public string saveDirectory = "Dataset";
    public int imageWidth = 512;
    public int imageHeight = 512;
    public Model model;
    
    private bool isGenerating = false;
    
    // Start is called before the first frame update
    void Start()
    {
        // 如果没有指定相机，使用主相机
        if (screenshotCamera == null)
        {
            screenshotCamera = Camera.main;
        }
        
        // 如果没有指定模型，尝试找到模型组件
        if (model == null)
        {
            model = FindObjectOfType<Model>();
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    
    /// <summary>
    /// 生成指定数量的数据集
    /// </summary>
    public void GenerateDataset(int count)
    {
        if (!isGenerating)
        {
            StartCoroutine(GenerateDatasetCoroutine(count));
        }
        else
        {
            Debug.LogWarning("数据集生成正在进行中，请等待完成");
        }
    }
    

    
    private IEnumerator GenerateDatasetCoroutine(int count)
    {
        isGenerating = true;

        // 创建保存目录
        string fullSaveDirectory = Path.Combine(Application.dataPath, saveDirectory);
        if (!Directory.Exists(fullSaveDirectory))
        {
            Directory.CreateDirectory(fullSaveDirectory);
        }

        Debug.Log($"开始生成 {count} 个数据集样本，保存到: {fullSaveDirectory}");

        for (int i = 0; i < count; i++)
        {
            // 生成随机数据
            Data randomData = Data.RandomGenData();

            // 应用数据到模型
            if (model != null)
            {
                model.UpdateFromData(randomData);
            }

            // 等待一帧确保模型更新完成
            yield return new WaitForEndOfFrame();

            // 获取面部特征点
            string landmarksJson = model.GetFacialLandmarks2DJson();

            // 生成文件名
            string fileName = $"sample_{i:D4}";

            // 保存JSON数据
            string jsonPath = Path.Combine(fullSaveDirectory, fileName + ".json");

            // 使用辅助方法构建JSON字符串
            string dataJson = randomData.ToJson();
            string jsonContent = "{\n" +
                "  \"data\": " + dataJson + ",\n" +
                "  \"landmarks\": " + landmarksJson + "\n" +
                "}";    

            File.WriteAllText(jsonPath, jsonContent);

            // 截图并保存
            string imagePath = Path.Combine(fullSaveDirectory, fileName + ".png");
            yield return StartCoroutine(CaptureScreenshot(imagePath));

            // 显示进度
            if (i % 10 == 0 || i == count - 1)
            {
                Debug.Log($"数据集生成进度: {i + 1}/{count} ({(float)(i + 1) / count * 100:F1}%)");
            }

            // 每10个样本暂停一小段时间，避免过度占用资源
            if (i % 10 == 0 && i > 0)
            {
                yield return new WaitForSeconds(0.1f);
            }
        }

        isGenerating = false;
        Debug.Log($"数据集生成完成！共生成 {count} 个样本，保存在: {fullSaveDirectory}");
    }
    
    private IEnumerator CaptureScreenshot(string filePath)
    {
        // 等待渲染完成
        yield return new WaitForEndOfFrame();
        
        // 创建RenderTexture
        RenderTexture renderTexture = new RenderTexture(imageWidth, imageHeight, 24);
        RenderTexture previousTarget = screenshotCamera.targetTexture;
        
        // 设置相机渲染目标
        screenshotCamera.targetTexture = renderTexture;
        screenshotCamera.Render();
        
        // 读取像素数据
        RenderTexture.active = renderTexture;
        Texture2D screenshot = new Texture2D(imageWidth, imageHeight, TextureFormat.RGB24, false);
        screenshot.ReadPixels(new Rect(0, 0, imageWidth, imageHeight), 0, 0);
        screenshot.Apply();
        
        // 恢复相机设置
        screenshotCamera.targetTexture = previousTarget;
        RenderTexture.active = null;
        
        // 保存图片
        byte[] data = screenshot.EncodeToPNG();
        File.WriteAllBytes(filePath, data);
        
        // 清理资源
        DestroyImmediate(screenshot);
        DestroyImmediate(renderTexture);
    }
    
    /// <summary>
    /// 获取当前是否正在生成数据集
    /// </summary>
    public bool IsGenerating()
    {
        return isGenerating;
    }
    
    /// <summary>
    /// 停止数据集生成
    /// </summary>
    public void StopGeneration()
    {
        StopAllCoroutines();
        isGenerating = false;
        Debug.Log("数据集生成已停止");
    }
}
