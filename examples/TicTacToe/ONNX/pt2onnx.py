import torch
from ultralytics import YOLO
import torch.onnx
from torchvision import models

# 加载预训练的 PyTorch 模型
model = YOLO("TicTacToe.pt")
model.eval()  # 设置模型为评估模式

# 创建一个示例输入张量
dummy_input = torch.randn(1, 3, 224, 224)  # 这里的形状应与模型的输入形状匹配

# 导出模型
onnx_model_path = "model.onnx"
torch.onnx.export(model,               # 要转换的模型
                  dummy_input,         # 模型的示例输入
                  onnx_model_path,     # 保存 ONNX 模型的路径
                  export_params=True,  # 保存模型参数
                  opset_version=11,    # ONNX 版本
                  do_constant_folding=True,  # 是否执行常量折叠优化
                  input_names=['input'],   # 输入名称
                  output_names=['output'], # 输出名称
                  dynamic_axes={'input': {0: 'batch_size'},    # 动态轴
                                'output': {0: 'batch_size'}})

print(f"模型已成功导出为 {onnx_model_path}")