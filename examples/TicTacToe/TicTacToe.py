"""
File: aiGame.py
Description: 井字棋 AI 游戏主控制模块，整合视觉检测、机器人控制和游戏逻辑
Author: Jerry Peng @ PineconeAI（湖南松果智能科技有限公司）
Date: 2024-09-03
Version: 1.0
GitHub: https://github.com/7Bot
License: MIT
"""

# 定义机器人端口
port="/dev/cu.SLAB_USBtoUART"

import time
from game import Game
from VisionDetection import VisionDetection
from RobotCtrl import RobotCtrl

class AIGame:
    def __init__(self):
        self.game = Game()
        self.vision = VisionDetection()
        self.robot = RobotCtrl(port)
        self.is_robot_moving = False

    def update_board_from_vision(self):
        frame = self.vision.get_frame()
        hands_results = self.vision.hand_detect(frame)
        
        if self.vision.no_hand_detected(hands_results):
            piece_results = self.vision.detect_piece(frame)
            detected_board = self.vision.detect_piece_on_board(piece_results)
            
            for i in range(9):
                if self.game.board[i] == " " and detected_board[i] != " ":
                    self.game.board[i] = detected_board[i]
                    return i  # 返回人类玩家的移动
        
        return None

    def human_player_move(self):
        move = None
        while move is None:
            move = self.update_board_from_vision()
            if move is not None:
                return move
            time.sleep(0.2)  # 短暂暂停以避免过度占用 CPU

    def ai_player_move(self):
        move = self.game.ai_player_move()
        self.is_robot_moving = True
        self.robot.robot_move_piece(self.robot.get_arm_cell_centers()[move])
        self.is_robot_moving = False
        self.game.board[move] = "O"
        return move

    def display_game(self):
        frame = self.vision.get_frame()
        if not self.is_robot_moving:
            hands_results = self.vision.hand_detect(frame)
            piece_results = self.vision.detect_piece(frame)
            self.vision.draw_hand_landmarks(frame, hands_results)
            self.vision.draw_piece(frame, piece_results)
        
        cam_cell_centers, cam_cell_half_width = self.vision.get_board_grid_centers()
        self.vision.draw_board_grid(frame, cam_cell_centers, cam_cell_half_width)
        self.vision.show_frame(frame)

    def play_game(self):
        print("欢迎来到 AI 井字棋游戏！")
        self.game.print_board()

        current_player = "X"  # 人类玩家先手

        while True:
            if current_player == "X":
                print("轮到你下棋了。")
                move = self.human_player_move()
                print(f"你选择了位置: {move}")
            else:
                print("AI 正在思考...")
                move = self.ai_player_move()
                print(f"AI 选择了位置: {move}")

            self.game.print_board()

            if self.game.is_winner(current_player):
                print(f"玩家 {current_player} 获胜！")
                break

            if self.game.is_board_full():
                print("平局！")
                break

            current_player = "O" if current_player == "X" else "X"

            self.display_game()

        print("游戏结束！")

if __name__ == "__main__":
    game = AIGame()
    game.play_game()