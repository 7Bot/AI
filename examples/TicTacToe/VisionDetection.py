"""
File: VisionDetection.py
Description: 视觉检测模块，用于井字棋游戏中的棋盘和棋子识别和人手检测
Author: Jerry Peng @ PineconeAI（湖南松果智能科技有限公司）
Date: 2024-09-03
Version: 1.0
GitHub: https://github.com/7Bot
License: MIT
"""

# 导入必要的库
import cv2
from ultralytics import YOLO
import mediapipe as mp
import numpy as np
import json

class VisionDetection:
    def __init__(self):
        # 初始化视觉检测所需的组件
        # 初始化 MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                         max_num_hands=1,
                                         min_detection_confidence=0.5,
                                         min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # 初始化 YOLO
        self.model = YOLO("TicTacToe.pt", verbose=False)
        self.class_names = ['O', 'X']

        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # 从 board.json 文件读取角点坐标
        self.cornersRec = self.load_corners_from_json()

    def load_corners_from_json(self):
        try:
            with open('board.json', 'r') as f:
                corners_data = json.load(f)
            
            # 确保角点顺序正确
            cornersRec = [
                corners_data['UpLeft'],
                corners_data['UpRight'],
                corners_data['DownRight'],
                corners_data['DownLeft']
            ]
            return cornersRec
        except FileNotFoundError:
            print("board.json 文件不存在。请先运行 recBoardCorner.py 生成角点坐标。")
            return [[131, 52], [497, 56], [494, 420], [125, 414]]  # 使用默认值
        except json.JSONDecodeError:
            print("board.json 文件格式错误。使用默认角点坐标。")
            return [[131, 52], [497, 56], [494, 420], [125, 414]]  # 使用默认值

    # 获取当前帧
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return None
        return frame

    # 显示当前帧
    def show_frame(self, frame):
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()

    # 计算棋盘格子的中心坐标
    def get_board_grid_centers(self):
        corners = self.cornersRec  # 使用从 JSON 文件加载的角点坐标
        width = corners[2][0] - corners[0][0]
        height = corners[2][1] - corners[0][1]
        centers = [
            (int(corners[0][0] + width * (2 - i) / 3 + width / 6), int(corners[0][1] + height * j / 3 + height / 6))
            for i in range(3)
            for j in range(3)
        ]
        detect_width = int(width / 8)
        return centers, detect_width

    # 在图像上绘制棋盘网格
    def draw_board_grid(self, frame, centers, half_width):
        for i in range(9):
            cv2.putText(frame, str(i), centers[i], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.rectangle(frame, (centers[i][0] - half_width, centers[i][1] - half_width), 
                          (centers[i][0] + half_width, centers[i][1] + half_width), 
                          (0, i * 25, 255 - i * 25), 1)

    # 使用MediaPipe检测手部
    def hand_detect(self, frame_rgb):
        return self.hands.process(frame_rgb)

    # 检查是否没有检测到手
    def no_hand_detected(self, hands_results):
        return not hands_results.multi_hand_landmarks

    # 在图像上绘制手部关键点
    def draw_hand_landmarks(self, frame, hands_results):
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                pt = hand_landmarks.landmark[12]
                x = int(pt.x * frame.shape[1])
                y = int(pt.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    # 使用YOLO模型检测棋子
    def detect_piece(self, frame_rgb):
        return self.model.predict(frame_rgb)

    # 检测棋盘上的棋子位置
    def detect_piece_on_board(self, piece_results):
        cam_cell_centers, cam_cell_half_width = self.get_board_grid_centers()
        board_status = [" "] * 9

        result = piece_results[0]
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = self.class_names[class_id]
            x_center = int((box.xyxy[0][0] + box.xyxy[0][2]) / 2)
            y_center = int((box.xyxy[0][1] + box.xyxy[0][3]) / 2)

            for i, center in enumerate(cam_cell_centers):
                if (center[0] - cam_cell_half_width <= x_center <= center[0] + cam_cell_half_width and
                        center[1] - cam_cell_half_width <= y_center <= center[1] + cam_cell_half_width):
                    board_status[i] = class_name.upper()
        return board_status

    # 在图像上绘制检测到的棋子
    def draw_piece(self, frame, piece_results):
        result = piece_results[0]
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = self.class_names[class_id]
            color = (0, 255, 0) if class_id == 0 else (255, 0, 0)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.rectangle(frame, (x1, y1-15), (x1+15, y1), color, -1)
            cv2.putText(frame, class_name, (x1+3, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # 主要的棋子检测循环
    def detect_chesspiece(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            hands_results = self.hand_detect(frame_rgb)
            piece_results = self.detect_piece(frame_rgb)
            board_status = self.detect_piece_on_board(piece_results)
            print(board_status)

            self.draw_hand_landmarks(frame, hands_results)
            self.draw_piece(frame, piece_results)
            cam_cell_centers, cam_cell_half_width = self.get_board_grid_centers()
            self.draw_board_grid(frame, cam_cell_centers, cam_cell_half_width)
            
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = VisionDetection()
    detector.detect_chesspiece()