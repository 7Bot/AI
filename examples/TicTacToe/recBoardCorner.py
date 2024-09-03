import cv2
import json
import os

cap = cv2.VideoCapture(0) 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 创建角点坐标结构体
corners = {"UpLeft": None, "UpRight": None, "DownRight": None, "DownLeft": None}
current_corner = 0
corner_names = list(corners.keys())
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 255)]  # 红、绿、蓝、白

# JSON文件路径
json_file = 'board.json'

def save_json():
    with open(json_file, 'w') as f:
        json.dump(corners, f, ensure_ascii=False, indent=4)

def click_callback(event, x, y, flags, param):
    global current_corner
    if event == cv2.EVENT_LBUTTONDOWN and current_corner < 4:
        corners[corner_names[current_corner]] = [x, y]
        current_corner += 1
        save_json()  # 每次点击后保存JSON

cv2.namedWindow('Video')
cv2.setMouseCallback('Video', click_callback)

while True:
    ret, frame = cap.read()
    
    # 显示提示文字
    if current_corner < 4:
        text = f"Click {corner_names[current_corner]}"
    else:
        text = "Finish"
    
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 绘制已记录的点
    for i, corner in enumerate(corners.values()):
        if corner is not None:
            cv2.circle(frame, tuple(corner), 5, colors[i], -1)
    
    cv2.imshow('Video', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or current_corner == 4:
        break

cap.release()
cv2.destroyAllWindows()

# 程序结束时再次保存JSON，以确保所有数据都被保存
save_json()