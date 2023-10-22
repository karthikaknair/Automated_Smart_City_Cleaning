import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# 加载预训练的MobileNetV2模型
base_model = MobileNetV2(weights='imagenet', include_top=False)
global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
feature_extractor = tf.keras.Sequential([
    base_model,
    global_average_layer
])

# 特征提取函数
def extract_features(img_path):
    img = load_img(img_path, target_size=(224, 224))
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = feature_extractor.predict(x)
    return features

# 垃圾检测函数
def detect_trash(img_path, threshold=0.5):
    features = extract_features(img_path)
    # 这里我们简单地使用特征的均值作为判定标准
    # 可根据实际数据调整阈值
    if np.mean(features) > threshold:
        return 1
    else:
        return 0


