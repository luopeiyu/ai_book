import torch
import torch.nn as nn
from k2p import KeypointsToParamsNet
from hair_classify import HairClassifierNet

def count_parameters(model):
    """计算模型的参数量"""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total_params, trainable_params

def get_model_info(model, model_name, input_shape):
    """获取模型的详细信息"""
    print(f"\n=== {model_name} 模型信息 ===")
    
    # 计算参数量
    total_params, trainable_params = count_parameters(model)
    print(f"总参数量: {total_params:,}")
    print(f"可训练参数量: {trainable_params:,}")
    print(f"参数量 (MB): {total_params * 4 / (1024 * 1024):.2f}")  # 假设float32，每个参数4字节
    
    # 获取输入输出维度信息
    model.eval()
    with torch.no_grad():
        # 创建测试输入
        test_input = torch.randn(1, *input_shape)
        print(f"输入维度: {test_input.shape}")
        
        # 前向传播获取输出
        output = model(test_input)
        print(f"输出维度: {output.shape}")
        
        # 详细的网络结构信息
        print(f"\n网络结构:")
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # 叶子节点
                params = sum(p.numel() for p in module.parameters())
                if params > 0:
                    print(f"  {name}: {module} - 参数量: {params:,}")

def analyze_k2p_model():
    """分析关键点到参数的模型"""
    print("正在分析 KeypointsToParamsNet 模型...")
    
    # 创建模型
    model = KeypointsToParamsNet()
    
    # KeypointsToParamsNet的输入是22维的关键点数据（11个点，每个点x,y坐标）
    # 输出是7维的参数（headWidth, headHeight, noseWidth, noseLength, eyeLength, eyeWidth, mouthSize）
    input_shape = (22,)  # 22维输入
    
    get_model_info(model, "KeypointsToParamsNet", input_shape)
    
    print(f"\n模型功能说明:")
    print(f"  - 输入: 11个人脸关键点的归一化坐标 (x,y) = 22维向量")
    print(f"  - 输出: 7个捏脸参数 (headWidth, headHeight, noseWidth, noseLength, eyeLength, eyeWidth, mouthSize)")
    print(f"  - 任务类型: 回归任务")
    print(f"  - 损失函数: MSE (均方误差)")

def analyze_hair_classifier_model():
    """分析发型分类模型"""
    print("正在分析 HairClassifierNet 模型...")
    
    # 创建模型
    model = HairClassifierNet()
    
    # HairClassifierNet的输入是32x32的灰度图像
    # 输出是5个发型类别的概率
    input_shape = (1, 32, 32)  # 1通道，32x32图像
    
    get_model_info(model, "HairClassifierNet", input_shape)
    
    print(f"\n模型功能说明:")
    print(f"  - 输入: 32x32像素的灰度图像")
    print(f"  - 输出: 5个发型类别的概率分布")
    print(f"  - 任务类型: 分类任务")
    print(f"  - 损失函数: CrossEntropyLoss (交叉熵)")

def compare_models():
    """对比两个模型"""
    print("\n" + "="*60)
    print("模型对比分析")
    print("="*60)
    
    # 创建两个模型
    k2p_model = KeypointsToParamsNet()
    hair_model = HairClassifierNet()
    
    # 计算参数量
    k2p_total, k2p_trainable = count_parameters(k2p_model)
    hair_total, hair_trainable = count_parameters(hair_model)
    
    print(f"参数量对比:")
    print(f"  KeypointsToParamsNet: {k2p_total:,} 参数")
    print(f"  HairClassifierNet:    {hair_total:,} 参数")
    print(f"  参数量比例: {hair_total/k2p_total:.1f}:1 (发型分类器 : 关键点回归器)")
    
    print(f"\n模型复杂度分析:")
    print(f"  KeypointsToParamsNet:")
    print(f"    - 网络类型: 简单的全连接网络")
    print(f"    - 层数: 3层")
    print(f"    - 参数量: {k2p_total:,} ({k2p_total * 4 / (1024 * 1024):.2f} MB)")
    print(f"    - 计算复杂度: 低")
    
    print(f"  HairClassifierNet:")
    print(f"    - 网络类型: 卷积神经网络")
    print(f"    - 层数: 多层(卷积+池化+全连接)")
    print(f"    - 参数量: {hair_total:,} ({hair_total * 4 / (1024 * 1024):.2f} MB)")
    print(f"    - 计算复杂度: 中等")
    
    print(f"\n应用场景对比:")
    print(f"  KeypointsToParamsNet:")
    print(f"    - 处理结构化数据(关键点坐标)")
    print(f"    - 实时性要求高")
    print(f"    - 输出连续数值")
    
    print(f"  HairClassifierNet:")
    print(f"    - 处理图像数据")
    print(f"    - 需要特征提取能力")
    print(f"    - 输出离散类别")

def main():
    """主函数"""
    print("AI游戏开发 - 模型参数分析工具")
    print("="*60)
    
    try:
        # 分析关键点到参数的模型
        analyze_k2p_model()
        
        print("\n" + "-"*60)
        
        # 分析发型分类模型
        analyze_hair_classifier_model()
        
        # 对比两个模型
        compare_models()
        
        print(f"\n总结:")
        print(f"  两个模型在AI照片捏脸系统中承担不同的角色:")
        print(f"  - KeypointsToParamsNet: 负责从人脸关键点预测捏脸参数，是核心的参数映射模块")
        print(f"  - HairClassifierNet: 负责从照片中识别发型类型，是辅助的分类模块")
        print(f"  - 两者结合使用，实现完整的AI照片捏脸功能")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        print("请确保 k2p.py 和 hair_classify.py 文件在同一目录下")

if __name__ == "__main__":
    main()
