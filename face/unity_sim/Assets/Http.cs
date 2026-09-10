using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Text;
using System.Threading;
using UnityEngine;

//请求示例 curl "http://localhost:8080/face?headWidth=50&headHeight=-30&noseWidth=20"

public class Http : MonoBehaviour
{
    [Header("HTTP服务器设置")]
    public int port = 8080;
    public Model model;

    private HttpListener httpListener;
    private Thread httpListenerThread;
    private bool isRunning = false;

    // 请求队列系统
    private Queue<RequestData> requestQueue = new Queue<RequestData>();
    private readonly object queueLock = new object();

    // 请求数据结构
    private class RequestData
    {
        public Data faceData;
        public HttpListenerResponse response;
        public bool isProcessed = false;
        public string result = null;
    }

    void Start()
    {
        model = FindObjectOfType<Model>();
        StartHttpServer();
    }

    void Update()
    {
        ProcessRequestQueue();
    }

    void OnDestroy()
    {
        StopHttpServer();
    }

    private void StartHttpServer()
    {
        httpListener = new HttpListener();
        httpListener.Prefixes.Add($"http://localhost:{port}/");
        httpListener.Start();

        isRunning = true;
        httpListenerThread = new Thread(HandleHttpRequests);
        httpListenerThread.Start();

        Debug.Log($"HTTP服务器已启动，端口: {port}");
    }

    private void StopHttpServer()
    {
        isRunning = false;
        httpListener?.Stop();
        httpListenerThread?.Abort();
    }

    private void HandleHttpRequests()
    {
        while (isRunning)
        {
            try
            {
                HttpListenerContext context = httpListener.GetContext();
                ProcessRequest(context);
            }
            catch { }
        }
    }

    private void ProcessRequest(HttpListenerContext context)
    {
        HttpListenerRequest request = context.Request;
        HttpListenerResponse response = context.Response;

        // 设置CORS头
        response.Headers.Add("Access-Control-Allow-Origin", "*");
        response.Headers.Add("Access-Control-Allow-Methods", "GET");

        if (request.HttpMethod == "GET" && request.Url.AbsolutePath == "/face")
        {
            HandleFaceRequest(request, response);
        }
        else
        {
            response.StatusCode = 404;
            response.Close();
        }
    }

    private void HandleFaceRequest(HttpListenerRequest request, HttpListenerResponse response)
    {
        // 解析参数
        Data faceData = ParseFaceParameters(request.QueryString);

        // 创建请求数据并添加到队列
        RequestData requestData = new RequestData
        {
            faceData = faceData,
            response = response
        };

        lock (queueLock)
        {
            requestQueue.Enqueue(requestData);
        }

        // 等待处理完成
        while (!requestData.isProcessed)
        {
            Thread.Sleep(10);
        }

        // 发送响应
        response.ContentType = "application/json";
        response.StatusCode = 200;
        byte[] buffer = Encoding.UTF8.GetBytes(requestData.result);
        response.ContentLength64 = buffer.Length;
        response.OutputStream.Write(buffer, 0, buffer.Length);
        response.Close();
    }

    private void ProcessRequestQueue()
    {
        RequestData currentRequest = null;

        lock (queueLock)
        {
            if (requestQueue.Count > 0)
            {
                currentRequest = requestQueue.Dequeue();
            }
        }

        if (currentRequest != null)
        {
            StartCoroutine(ProcessRequestInMainThread(currentRequest));
        }
    }

    private IEnumerator ProcessRequestInMainThread(RequestData requestData)
    {
        // 更新模型
        model.UpdateFromData(requestData.faceData);

        // 等待一帧
        yield return new WaitForEndOfFrame();

        // 获取关键点
        requestData.result = model.GetFacialLandmarks2DJson();
        requestData.isProcessed = true;
    }

    private Data ParseFaceParameters(System.Collections.Specialized.NameValueCollection queryString)
    {
        Data data = new Data();

        if (int.TryParse(queryString["headWidth"], out int headWidth))
            data.headWidth = Mathf.Clamp(headWidth, -100, 100);

        if (int.TryParse(queryString["headHeight"], out int headHeight))
            data.headHeight = Mathf.Clamp(headHeight, -100, 100);

        if (int.TryParse(queryString["noseWidth"], out int noseWidth))
            data.noseWidth = Mathf.Clamp(noseWidth, -100, 100);

        if (int.TryParse(queryString["noseLength"], out int noseLength))
            data.noseLength = Mathf.Clamp(noseLength, -100, 100);

        if (int.TryParse(queryString["eyeLength"], out int eyeLength))
            data.eyeLength = Mathf.Clamp(eyeLength, -100, 100);

        if (int.TryParse(queryString["eyeWidth"], out int eyeWidth))
            data.eyeWidth = Mathf.Clamp(eyeWidth, -100, 100);

        if (int.TryParse(queryString["eyeGap"], out int eyeGap))
            data.eyeGap = Mathf.Clamp(eyeGap, -100, 100);

        if (int.TryParse(queryString["mouthSize"], out int mouthSize))
            data.mouthSize = Mathf.Clamp(mouthSize, -100, 100);

        if (int.TryParse(queryString["hairType"], out int hairType))
            data.hairType = Mathf.Clamp(hairType, 0, 4);

        return data;
    }
}
