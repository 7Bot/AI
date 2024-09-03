import cv2
import numpy as np
import onnxruntime as ort

# 加载 ONNX 模型
model_path = "your_model.onnx"
session = ort.InferenceSession(model_path)

# 获取模型输入和输出的名称
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# 初始化摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def preprocess(frame):
    # 将图像调整为模型输入大小
    input_size = (224, 224)  # 根据模型的输入大小进行调整
    frame_resized = cv2.resize(frame, input_size)
    frame_normalized = frame_resized.astype(np.float32) / 255.0
    frame_transposed = np.transpose(frame_normalized, (2, 0, 1))  # HWC to CHW
    frame_expanded = np.expand_dims(frame_transposed, axis=0)  # 增加 batch 维度
    return frame_expanded

def postprocess(output):
    # 根据��型的输出进行后处理
    # 这里假设模型输出是一个分类结果
    class_id = np.argmax(output)
    return class_id

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 预处理图像
    input_data = preprocess(frame)

    # 进行推理
    outputs = session.run([output_name], {input_name: input_data})
    class_id = postprocess(outputs[0])

    # 在图像上绘制结果
    cv2.putText(frame, f"Class: {class_id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 显示图像
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

# 释放摄像头资源
cap.release()
# 关闭所有 OpenCV 窗口
cv2.destroyAllWindows()
