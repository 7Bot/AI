"""
File: game.py
Description: 井字棋游戏逻辑模块，包含游戏规则、AI 决策和人机交互
Author: Jerry Peng @ PineconeAI（湖南松果智能科技有限公司）
Date: 2024-09-03
Version: 1.0
GitHub: https://github.com/7Bot
License: MIT
"""

class Game:
    def __init__(self):
        self.board = self.initialize_board()

    # 初始化棋盘，返回一个包含9个空格的列表
    def initialize_board(self):
        return [" "] * 9

    # 打印当前棋盘状态
    def print_board(self):
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print()
            print(self.board[i], end=" ")
        print()

    # 检查玩家是否胜利
    def is_winner(self, player):
        win_conditions = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        return any(self.board[i] == self.board[j] == self.board[k] == player for i, j, k in win_conditions)  # 返回玩家是否满足任一胜利条件

    # 检查棋盘是否已满
    def is_board_full(self):
        return " " not in self.board

    # 评估当前棋盘状态
    def evaluate(self):
        # 评估函数: 计算当前棋盘状态的分数
        if self.is_winner("X"):
            return 10
        elif self.is_winner("O"):
            return -10

        # 计算潜在获胜路径
        score = 0
        for i in range(3):
            if self.board[i * 3:(i + 1) * 3].count("X") == 2 and self.board[i * 3:(i + 1) * 3].count(" ") == 1:
                score += 1  # X 潜在胜利
            if self.board[i * 3:(i + 1) * 3].count("O") == 2 and self.board[i * 3:(i + 1) * 3].count(" ") == 1:
                score -= 1  # O 潜在胜利

        # 也可以在此增加对角线和列的评估
        for j in range(3):
            if [self.board[j], self.board[j + 3], self.board[j + 6]].count("X") == 2 and [self.board[j], self.board[j + 3], self.board[j + 6]].count(" ") == 1:
                score += 1
            if [self.board[j], self.board[j + 3], self.board[j + 6]].count("O") == 2 and [self.board[j], self.board[j + 3], self.board[j + 6]].count(" ") == 1:
                score -= 1

        return score

    def minimax(self, depth, alpha, beta, is_maximizing):
        # 增加最大深度限制
        max_depth = 5  # 设定最大搜索深度
        score = self.evaluate()

        if score != 0 or depth == max_depth:
            return score

        if self.is_board_full():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(len(self.board)):
                if self.board[i] == " ":
                    self.board[i] = "X"
                    score = self.minimax(depth + 1, alpha, beta, False)
                    self.board[i] = " "
                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
            return best_score
        else:
            best_score = float('inf')
            for i in range(len(self.board)):
                if self.board[i] == " ":
                    self.board[i] = "O"
                    score = self.minimax(depth + 1, alpha, beta, True)
                    self.board[i] = " "
                    best_score = min(score, best_score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
            return best_score

    # AI查找最佳落子位置
    def find_best_move(self, is_maximizing):
        best_move = -1
        best_score = -float('inf') if is_maximizing else float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        for i in range(len(self.board)):
            if self.board[i] == " ":
                self.board[i] = "X" if is_maximizing else "O"
                score = self.minimax(0, alpha, beta, not is_maximizing)
                self.board[i] = " "
                
                if is_maximizing and score > best_score:
                    best_score = score
                    best_move = i
                elif not is_maximizing and score < best_score:
                    best_score = score
                    best_move = i

        return best_move

    def human_player_move(self):
        while True:
            move = int(input("选择一个位置 (0-8): "))
            if self.board[move] == " ":
                return move
            else:
                print("该位置已被占用，请重新选择。")

    def ai_player_move(self):
        return self.find_best_move(True)

    def play_game(self):
        while True:
            first_player = input("选择谁先下棋 (X = 玩家, O = AI): ").upper()
            if first_player in ["X", "O"]:
                current_player = first_player
                break
            else:
                print("无效输入，请输入 'X' 或 'O'.")

        while True:
            self.print_board()
            if current_player == "O":
                move = self.ai_player_move()
                print(f"AI 选择了位置: {move}")
            else:
                move = self.human_player_move()
                print(f"您选择了位置: {move}")

            self.board[move] = current_player

            if self.is_winner(current_player):
                self.print_board()
                print(f"玩家 {current_player} 获胜！")
                break

            if self.is_board_full():
                self.print_board()
                print("平局！")
                break

            current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    game = Game()
    game.play_game()