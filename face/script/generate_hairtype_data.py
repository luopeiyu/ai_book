import torch
import torch.nn.functional as F
from PIL import Image
import clip
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm

class HairTypeClassifier:
    def __init__(self, hairtype_folder):
        """
        初始化头发类型分类器
        
        Args:
            hairtype_folder: 包含头发类型参考图片的文件夹路径
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        # 加载CLIP模型
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device, download_root="models")
        
        # 加载头发类型参考图片
        self.hairtype_folder = Path(hairtype_folder)
        self.load_hairtype_references()
    
    def convert_to_grayscale_rgb(self, image):
        """将图片转为灰度，但保持RGB格式"""
        gray = image.convert('L')
        rgb_gray = Image.merge('RGB', (gray, gray, gray))
        return rgb_gray
    
    def crop_hairtype_region(self, image):
        """
        裁剪hairtype图片的头发区域
        根据3D模型特点，裁剪上半部分的头发区域
        """
        width, height = image.size
        
        # 3D模型的头发主要在上半部分
        # 裁剪区域
        width_crop = int(width * 0.65)
        height_crop = int(height * 0.65)
        height_offset = -int(height * 0.1)
        
        left = width / 2 - width_crop / 2
        right = left + width_crop
        top = height / 2 - height_crop / 2 + height_offset
        bottom = top + height_crop
        
        cropped = image.crop((left, top, right, bottom))
        return cropped
    
    def crop_real_face_region(self, image):
        cropped = image
        return cropped
    
    def load_hairtype_references(self):
        """加载头发类型参考图片并提取特征"""
        self.hairtype_features = {}
        
        png_files = list(self.hairtype_folder.glob('*.png'))
        print(f"找到 {len(png_files)} 个头发类型参考图片:")
        
        for png_file in png_files:
            hairtype_id = png_file.stem
            
            # 加载图片
            image = Image.open(png_file).convert('RGB')
            
            # 裁剪头发区域
            cropped_image = self.crop_hairtype_region(image)
            
            # 转为灰度
            gray_image = self.convert_to_grayscale_rgb(cropped_image)
            
            # 预处理并提取特征
            image_input = self.preprocess(gray_image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model.encode_image(image_input)
                features = F.normalize(features, dim=-1)
            
            self.hairtype_features[hairtype_id] = features
            print(f"  - 类型 {hairtype_id}: {png_file.name} (已裁剪头发区域并转为灰度)")
        
        print(f"成功加载 {len(self.hairtype_features)} 个头发类型")
    
    def classify_hair_type(self, image_path):
        """对单张图片进行头发类型分类"""
        try:
            # 加载图片
            image = Image.open(image_path).convert('RGB')
            
            # 裁剪头发区域
            cropped_image = self.crop_real_face_region(image)
            
            # 转为灰度
            gray_image = self.convert_to_grayscale_rgb(cropped_image)
            
            # 预处理并提取特征
            image_input = self.preprocess(gray_image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features = F.normalize(image_features, dim=-1)
            
            # 计算与所有头发类型的相似度
            similarities = {}
            for hairtype_id, hairtype_features in self.hairtype_features.items():
                similarity = torch.cosine_similarity(image_features, hairtype_features, dim=1)
                similarities[hairtype_id] = float(similarity.item())
            
            # 找到相似度最高的类型
            best_hairtype = max(similarities, key=similarities.get)
            best_similarity = similarities[best_hairtype]
            return best_hairtype, best_similarity, similarities
            
        except Exception as e:
            print(f"处理图片 {image_path} 时出错: {e}")
            return None, 0.0, {}
    
    def save_cropped_examples(self, output_folder):
        """保存裁剪示例，用于验证裁剪效果"""
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
        
        print("保存裁剪示例...")
        
        # 保存hairtype裁剪示例
        for png_file in self.hairtype_folder.glob('*.png'):
            image = Image.open(png_file).convert('RGB')
            cropped = self.crop_hairtype_region(image)
            gray_cropped = self.convert_to_grayscale_rgb(cropped)
            
            output_name = f"hairtype_{png_file.stem}_cropped.png"
            gray_cropped.save(output_folder / output_name)
        
        print(f"裁剪示例已保存到: {output_folder}")
    
    def process_folder(self, folder_path):
        """处理文件夹中的所有jpg图片"""
        folder_path = Path(folder_path)
        jpg_files = list(folder_path.glob('*.jpg'))
        
        if not jpg_files:
            print(f"在 {folder_path} 中没有找到JPG文件")
            return []
        
        print(f"\n处理文件夹: {folder_path}")
        print(f"找到 {len(jpg_files)} 个JPG文件")
        
        results = []
        
        for jpg_file in tqdm(jpg_files, desc="处理图片"):
            # 分类头发类型
            hairtype, similarity, all_similarities = self.classify_hair_type(jpg_file)
            
            if hairtype is not None:
                results.append({
                    'hair_type': hairtype,
                    'confidence': similarity,
                    'all_similarities': all_similarities,
                    'source_image': jpg_file.name
                })
                
                # 保存JSON文件
                json_file = jpg_file.with_suffix('.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump({"hair_type": hairtype}, f, indent=2, ensure_ascii=False)

        return results
    
    def summary_results(self, results):
        """统计结果"""
        if not results:
            print("没有处理任何图片")
            return
            
        print(f"处理完成！共处理 {len(results)} 张图片")
        
        # 统计各类型数量
        type_counts = {}
        for result in results:
            hairtype = result['hair_type']
            type_counts[hairtype] = type_counts.get(hairtype, 0) + 1
        
        print("\n头发类型分布:")
        for hairtype, count in sorted(type_counts.items()):
            print(f"  类型 {hairtype}: {count} 张图片")
        
        # 计算平均置信度
        avg_confidence = np.mean([r['confidence'] for r in results])
        print(f"\n平均置信度: {avg_confidence:.4f}")

def main():
    """主函数"""
    # 设置路径
    hairtype_folder = "E:/B9/face/style_dataset/filtered_faces/hairtype"
    base_folder = "E:/B9/face/style_dataset/filtered_faces"
    
    
    classifier = HairTypeClassifier(hairtype_folder)
    
    # 保存裁剪示例（可选，用于验证效果）
    classifier.save_cropped_examples("E:/B9/face/style_dataset/cropped_examples")

    # 处理训练集
    train_folder = Path(base_folder) / 'train'
    print("\n" + "="*50)
    print("处理训练集")
    print("="*50)
    train_results = classifier.process_folder(train_folder)
    classifier.summary_results(train_results)
    
    # 处理测试集
    test_folder = Path(base_folder) / 'test'
    print("\n" + "="*50)
    print("处理测试集")
    print("="*50)
    test_results = classifier.process_folder(test_folder)
    classifier.summary_results(test_results)
    
    print(f"\n总共处理: {len(train_results) + len(test_results)} 张图片")

if __name__ == "__main__":
    main()
