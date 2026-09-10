from pathlib import Path
from k2p import KeypointsToParamsPredictor
from hair_classify import HairClassifierPredictor
from simulator import Simulator
from extract_facial_keypoints import FacialKeypointExtractor
from calculate_real_keypoint_offset import transform_real_to_anime
from normalize_facial_keypoints import FacialKeypointNormalizer

class FaceParameterPipeline:
    """人脸参数预测管道"""
    
    def __init__(self, 
                 k2p_model_path='models/k2p_model.pth',
                 hair_model_path='models/hair_classifier.pth'):
        print("初始化管道...")
        
        self.keypoint_extractor = FacialKeypointExtractor()
        self.k2p_predictor = KeypointsToParamsPredictor(k2p_model_path)
        self.hair_predictor = HairClassifierPredictor(hair_model_path)
        self.normalizer = FacialKeypointNormalizer()

        # 使用ResNet预训练模型训练头发分类器
        from hair_classify_balance_data_and_resnet import HairClassifierPredictor as HairClassifierPredictorResNet
        self.hair_predictor_with_resnet = HairClassifierPredictorResNet(model_path='models/hair_classifier_resnet.pth')

        print("管道初始化完成")
    
    def process(self, image_path):
        # 提取关键点
        keypoints = self.keypoint_extractor.extract_keypoints(image_path)
        keypoints = self.normalizer.normalize_keypoints(keypoints)
        # 风格化转换
        keypoints = transform_real_to_anime(keypoints)
        
        # 预测人脸参数
        landmarks = [{'x': point[0], 'y': point[1]} for point in keypoints]
        print("关键点：",landmarks)
        face_params = self.k2p_predictor.predict_from_landmarks(landmarks) #重复normalize但没关系
        
        # 预测头发类型
        #hair_type, confidence = self.hair_predictor.predict_from_image(image_path)
        hair_type, confidence = self.hair_predictor_with_resnet.predict_from_image(image_path)
        # 组合参数
        combined_params = face_params.copy()
        combined_params['hairType'] = hair_type-1
        
        return combined_params
        


def main():
    pipeline = FaceParameterPipeline()
    
    test_image = "E:/B9/face/style_dataset/filtered_faces/test/realface (200).jpg"
    params = pipeline.process(test_image)
    print("参数：",params)
    
    
    
    # 发送到模拟器看结果
    simulator = Simulator()
    simulator.get_landmarks(params)


if __name__ == "__main__":
    main()
