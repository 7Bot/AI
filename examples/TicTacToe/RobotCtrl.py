"""
File: RobotCtrl.py
Description: 机器人控制模块，用于控制机械臂的运动和操作
Author: Jerry Peng @ PineconeAI（湖南松果智能科技有限公司）
Date: 2024-09-03
Version: 1.0
GitHub: https://github.com/7Bot
License: MIT
"""

# 定义机器人端口
default_port="/dev/cu.SLAB_USBtoUART"

import time
import numpy as np
from lib.Arm7Bot import Arm7Bot

class RobotCtrl:
    def __init__(self, port=default_port):
        # 初始化机器人接口
        self.arm = Arm7Bot(port)
        
        # 初始设置
        self.j6 = np.array([0, 250, 100])  # 机器人的关节位置
        self.vec56 = np.array([0, 0, -1])   # 向量，用于控制抓取方向
        self.theta6 = 80                    # 机器人末端关节的角度
        self.get_pose = np.array([-140, 105, -5])  # 机器人抓取位置
        self.pieces_index = 0                 # 计数，跟踪抓取的物体数量
        self.debug_mode = False               # 是否启用调试模式

        #
        time.sleep(0.3)
        self.hold_pos()

    # 定义机械臂下棋位置坐标
    def get_arm_cell_centers(self):
        centers = [
            np.array([-125, 220, 35]),
            np.array([-81, 160, 35]),
            np.array([-40, 130, 35]),
            np.array([-88, 271, 35]),
            np.array([-26, 212, 35]),
            np.array([23, 155, 35]),
            np.array([-28, 323, 35]),
            np.array([28, 269, 35]),
            np.array([80, 203, 35])
        ]
        return centers

    # 函数：走子运动
    def robot_move_piece(self, position):
        """ 移动机器人手臂到指定的位置 """
        # 1- 准备抓取
        pos = self.get_pose + np.array([0, 0, 20])  # 计算准备抓取的位置
        if not isinstance(pos, np.ndarray):
            pos = np.array(pos)

        self.set_ik(pos, self.vec56, 90, self.theta6)  # 设置逆运动学参数
        time.sleep(1.7)  # 等待一段时间以确保动作完成
        
        # 2- 抓取
        pos = self.get_pose + np.array([0, 0, -5 * self.pieces_index])  # 计算实际抓取的位置
        self.pieces_index += 1  # 更新抓取计数
        self.set_ik(pos, self.vec56, 90, self.theta6 - 50)  # 设置抓取位置
        time.sleep(1.5)  # 等待抓取完成

        pos = self.get_pose + np.array([0, 0, 20])  # 移回准备位置
        self.set_ik(pos, self.vec56, 90, self.theta6 - 50)
        time.sleep(1.0)
        
        # 释放物体
        # 1- 准备放置
        self.set_ik(position, self.vec56, 90, self.theta6 - 80)  # 设置放置位置
        time.sleep(2.0)

        # 2- 放置
        self.set_ik(position, self.vec56, 90, self.theta6)  # 完成放置
        time.sleep(1.0)
        
        # 3- 持续保持当前位置
        self.hold_pos()
        time.sleep(0.8)

    # 函数：机械臂保持位置
    def hold_pos(self):
        """ 机器人保持当前位置 """
        self.set_ik(np.array([100, 50, 250]), np.array([1, 1, 0]), 90, self.theta6)

    # 函数： IK运动封装
    def set_ik(self, j6, vec56, theta5, theta6):
        """ 设置IK参数以控制机器人 """
        self.arm.setIK6(j6.tolist(), vec56.tolist())  # 设置关节参数
        if theta6 < 50:
            self.arm.setVacuum(1)  # 启动真空吸力
        else:
            self.arm.setVacuum(0)  # 关闭真空吸力

    # 函数：运动调试
    def pose_test(self):
        """ 测试机器人运动位置 """
        self.hold_pos()  # 先保持当前位置
        time.sleep(1.5)
        self.pieces_index = 0  # 重置抓取计数

        cell_centers = self.get_arm_cell_centers()
        for i in range(len(cell_centers)):
            if 0 <= i < len(cell_centers):
                self.robot_move_piece(cell_centers[i])
            self.pieces_index += 1  # 更新抓取计数

        self.pieces_index = 0  # ��新设置计数

if __name__ == "__main__":
    robot = RobotCtrl()
    robot.pose_test()  # 测试机器人运动