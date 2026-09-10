using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

public class VertexMatcher : EditorWindow
{
    private SkinnedMeshRenderer targetRenderer;
    private Vector2 scrollPos;
    private bool isSelecting = false;
    private List<VertexInfo> selectedVertices = new List<VertexInfo>();
    private bool showAllVertices = false;
    private float vertexDisplaySize = 0.01f;
    private Color vertexColor = Color.cyan;
    private Color selectedVertexColor = Color.red;
    
    [System.Serializable]
    public class VertexInfo
    {
        public int index;
        public Vector3 localPosition;
        public Vector3 worldPosition;
        public string timestamp;
        
        public VertexInfo(int idx, Vector3 localPos, Vector3 worldPos)
        {
            index = idx;
            localPosition = localPos;
            worldPosition = worldPos;
            timestamp = System.DateTime.Now.ToString("HH:mm:ss");
        }
    }
    
    [MenuItem("Tools/顶点选择器")]
    static void Init()
    {
        VertexMatcher window = (VertexMatcher)EditorWindow.GetWindow(typeof(VertexMatcher));
        window.titleContent = new GUIContent("顶点选择器");
        window.Show();
    }
    
    void OnGUI()
    {
        EditorGUILayout.LabelField("顶点选择工具", EditorStyles.boldLabel);
        
        // 选择SkinnedMeshRenderer
        targetRenderer = (SkinnedMeshRenderer)EditorGUILayout.ObjectField("目标渲染器", targetRenderer, typeof(SkinnedMeshRenderer), true);
        
        if (targetRenderer == null)
        {
            EditorGUILayout.HelpBox("请选择一个SkinnedMeshRenderer", MessageType.Info);
            return;
        }
        
        EditorGUILayout.Space();
        
        // 控制按钮
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button(isSelecting ? "停止选择" : "开始选择"))
        {
            isSelecting = !isSelecting;
            if (isSelecting)
            {
                Debug.Log("开始选择模式 - 在Scene视图中点击顶点");
            }
            else
            {
                Debug.Log("停止选择模式");
            }
            SceneView.RepaintAll();
        }
        
        if (GUILayout.Button("清空选择"))
        {
            selectedVertices.Clear();
            Debug.Log("已清空所有选择的顶点");
        }
        
        if (GUILayout.Button("显示所有顶点"))
        {
            showAllVertices = !showAllVertices;
            SceneView.RepaintAll();
        }
        EditorGUILayout.EndHorizontal();
        
        // 显示设置
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("显示设置", EditorStyles.boldLabel);
        vertexDisplaySize = EditorGUILayout.Slider("顶点显示大小", vertexDisplaySize, 0.0005f, 0.005f);
        vertexColor = EditorGUILayout.ColorField("顶点颜色", vertexColor);
        selectedVertexColor = EditorGUILayout.ColorField("选中顶点颜色", selectedVertexColor);
        
        // 网格信息
        if (targetRenderer.sharedMesh != null)
        {
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("网格信息", EditorStyles.boldLabel);
            EditorGUILayout.LabelField($"顶点总数: {targetRenderer.sharedMesh.vertexCount}");
            EditorGUILayout.LabelField($"已选择: {selectedVertices.Count} 个顶点");
        }
        
        // 选择状态提示
        if (isSelecting)
        {
            EditorGUILayout.HelpBox("选择模式已激活！在Scene视图中点击顶点来选择", MessageType.Info);
        }
        
        // 显示选择的顶点列表
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("选择的顶点", EditorStyles.boldLabel);
        
        if (selectedVertices.Count > 0)
        {
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("复制所有编号"))
            {
                CopyAllIndices();
            }
            if (GUILayout.Button("导出到文件"))
            {
                ExportToFile();
            }
            EditorGUILayout.EndHorizontal();
        }
        
        scrollPos = EditorGUILayout.BeginScrollView(scrollPos, GUILayout.Height(200));
        
        for (int i = selectedVertices.Count - 1; i >= 0; i--) // 倒序显示，最新的在上面
        {
            var vertex = selectedVertices[i];
            EditorGUILayout.BeginHorizontal();
            
            EditorGUILayout.LabelField($"[{vertex.timestamp}] 顶点 {vertex.index}", GUILayout.Width(150));
            EditorGUILayout.LabelField($"本地: {vertex.localPosition.ToString("F3")}", GUILayout.Width(200));
            EditorGUILayout.LabelField($"世界: {vertex.worldPosition.ToString("F3")}", GUILayout.Width(200));
            
            if (GUILayout.Button("复制", GUILayout.Width(40)))
            {
                EditorGUIUtility.systemCopyBuffer = vertex.index.ToString();
                Debug.Log($"已复制顶点编号: {vertex.index}");
            }
            
            if (GUILayout.Button("定位", GUILayout.Width(40)))
            {
                FocusOnVertex(vertex.worldPosition);
            }
            
            if (GUILayout.Button("删除", GUILayout.Width(40)))
            {
                selectedVertices.RemoveAt(i);
            }
            
            EditorGUILayout.EndHorizontal();
        }
        
        EditorGUILayout.EndScrollView();
    }
    
    void OnEnable()
    {
        SceneView.duringSceneGui += OnSceneGUI;
    }
    
    void OnDisable()
    {
        SceneView.duringSceneGui -= OnSceneGUI;
    }
    
    void OnSceneGUI(SceneView sceneView)
    {
        if (targetRenderer == null) return;
        
        if (showAllVertices)
        {
            DrawAllVertices();
        }
        
        DrawSelectedVertices();
        
        if (isSelecting)
        {
            HandleVertexSelection();
        }
    }
    
    private void DrawAllVertices()
    {
        if (targetRenderer.sharedMesh == null) return;
        
        Mesh mesh = targetRenderer.sharedMesh;
        Vector3[] vertices = mesh.vertices;
        
        Handles.color = vertexColor;
        for (int i = 0; i < vertices.Length; i++)
        {
            Vector3 worldPos = targetRenderer.transform.TransformPoint(vertices[i]);
            
            // 距离裁剪，避免显示过远的顶点
            float distanceToCamera = Vector3.Distance(worldPos, SceneView.lastActiveSceneView.camera.transform.position);
            if (distanceToCamera > 10f) continue;
            
            Handles.DrawSolidDisc(worldPos, SceneView.lastActiveSceneView.camera.transform.forward, vertexDisplaySize);
            
            // 近距离显示编号
            if (distanceToCamera < 3f)
            {
                Handles.Label(worldPos, i.ToString(), EditorStyles.miniLabel);
            }
        }
    }
    
    private void DrawSelectedVertices()
    {
        Handles.color = selectedVertexColor;
        foreach (var vertex in selectedVertices)
        {
            Handles.DrawSolidDisc(vertex.worldPosition, SceneView.lastActiveSceneView.camera.transform.forward, vertexDisplaySize * 1.5f);
            Handles.Label(vertex.worldPosition, vertex.index.ToString(), EditorStyles.whiteLargeLabel);
        }
    }
    
    private void HandleVertexSelection()
    {
        Event e = Event.current;
        
        if (e.type == EventType.MouseDown && e.button == 0 && !e.alt)
        {
            Ray ray = HandleUtility.GUIPointToWorldRay(e.mousePosition);
            int vertexIndex = FindClosestVertex(ray);
            
            if (vertexIndex >= 0)
            {
                SelectVertex(vertexIndex);
                e.Use();
            }
        }
    }
    
    private int FindClosestVertex(Ray ray)
    {
        if (targetRenderer.sharedMesh == null) return -1;
        
        Mesh mesh = targetRenderer.sharedMesh;
        Vector3[] vertices = mesh.vertices;
        
        int closestIndex = -1;
        float closestDistanceToRay = float.MaxValue;
        float closestDistanceToOrigin = float.MaxValue;
        float maxSelectionDistance = 0.1f; // 选择阈值
        
        for (int i = 0; i < vertices.Length; i++)
        {
            Vector3 worldPos = targetRenderer.transform.TransformPoint(vertices[i]);
            float distanceToRay = Vector3.Cross(ray.direction, worldPos - ray.origin).magnitude;
            
            if (distanceToRay < maxSelectionDistance)
            {
                float distanceToOrigin = Vector3.Distance(worldPos, ray.origin);
                
                // 优先选择离射线原点更近的顶点
                if (distanceToRay < closestDistanceToRay || 
                    (Mathf.Approximately(distanceToRay, closestDistanceToRay) && distanceToOrigin < closestDistanceToOrigin))
                {
                    closestDistanceToRay = distanceToRay;
                    closestDistanceToOrigin = distanceToOrigin;
                    closestIndex = i;
                }
            }
        }
        
        return closestIndex;
    }
    
    private void SelectVertex(int vertexIndex)
    {
        if (targetRenderer.sharedMesh == null) return;
        
        Mesh mesh = targetRenderer.sharedMesh;
        Vector3[] vertices = mesh.vertices;
        
        if (vertexIndex < 0 || vertexIndex >= vertices.Length) return;
        
        Vector3 localPos = vertices[vertexIndex];
        Vector3 worldPos = targetRenderer.transform.TransformPoint(localPos);
        
        // 检查是否已经选择过这个顶点
        bool alreadySelected = selectedVertices.Exists(v => v.index == vertexIndex);
        
        if (!alreadySelected)
        {
            VertexInfo newVertex = new VertexInfo(vertexIndex, localPos, worldPos);
            selectedVertices.Add(newVertex);
            
            Debug.Log($"选择顶点 {vertexIndex}: 本地坐标 {localPos}, 世界坐标 {worldPos}");
        }
        else
        {
            Debug.Log($"顶点 {vertexIndex} 已经被选择过了");
        }
        
        Repaint();
    }
    
    private void FocusOnVertex(Vector3 worldPosition)
    {
        SceneView.lastActiveSceneView.pivot = worldPosition;
        SceneView.lastActiveSceneView.Repaint();
    }
    
    private void CopyAllIndices()
    {
        if (selectedVertices.Count == 0) return;
        
        string indices = string.Join(", ", selectedVertices.ConvertAll(v => v.index.ToString()));
        EditorGUIUtility.systemCopyBuffer = indices;
        Debug.Log($"已复制所有顶点编号: {indices}");
    }
    
    private void ExportToFile()
    {
        if (selectedVertices.Count == 0) return;
        
        string path = EditorUtility.SaveFilePanel("导出顶点数据", Application.dataPath, "selected_vertices", "txt");
        if (!string.IsNullOrEmpty(path))
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.AppendLine($"选择的顶点数据 - {System.DateTime.Now}");
            sb.AppendLine($"目标对象: {targetRenderer.gameObject.name}");
            sb.AppendLine($"网格: {targetRenderer.sharedMesh.name}");
            sb.AppendLine("=====================================");
            
            foreach (var vertex in selectedVertices)
            {
                sb.AppendLine($"顶点 {vertex.index}: 本地坐标 {vertex.localPosition}, 世界坐标 {vertex.worldPosition}, 选择时间 {vertex.timestamp}");
            }
            
            sb.AppendLine("=====================================");
            sb.AppendLine($"顶点编号列表: {string.Join(", ", selectedVertices.ConvertAll(v => v.index.ToString()))}");
            
            System.IO.File.WriteAllText(path, sb.ToString());
            Debug.Log($"顶点数据已导出到: {path}");
        }
    }
} 