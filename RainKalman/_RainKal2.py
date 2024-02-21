from grab_gdi import GrabScreen 
import inference
import cv2
from time import perf_counter as tp
import time
import ctypes
import threading
from filterpy.kalman import KalmanFilter
import numpy as np
from enemy_kal2 import EnemyTracker

User32 = ctypes.windll.user32

get_async_key_state = User32.GetAsyncKeyState
get_async_key_state.argtypes = (ctypes.c_int,)

Ghub = ctypes.cdll.LoadLibrary('./tools/Ghub.dll')  # 文件路径

# 设置目标帧率，鼠标平滑的步长和间隔
TargetFps = 10
step_count = 8
interval = 1 / (TargetFps * step_count)
# 灵敏度系数
sens_scaler = 1.8
# 创建一个敌人追踪器对象，传入子弹速度和时间步长
bullet_speed = 150
time_step = 1 / TargetFps

# 定义目标类别
target = 1

def show_window(result, img) -> None:
    """可视化推理结果"""
    for x1, y1, x2, y2, _, cls in result:
        if cls == target:
            color = (0, 0, 255)
            text = 'target'
        else:
            color = (0, 255, 0)
            text = 'not target'
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 1)
        cv2.putText(img, text, (int(x1), int(y1)), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)  
    # cv2.namedWindow('green player', cv2.WINDOW_AUTOSIZE)
    # cv2.setWindowProperty('green player', cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow('green player', img)
    cv2.waitKey(1)  

def smooth_mouse_move(x_target, y_target):
    # 获取当前鼠标位置
    start_x, start_y = 0, 0
    # 计算鼠标移动的距离和步长
    dx = (x_target - start_x) / step_count
    dy = (y_target - start_y) / step_count
    # 执行插值移动
    for _ in range(step_count):
        start_x += dx
        start_y += dy
        Ghub.MoveR(int(start_x.item()), int(start_y.item()))

        time.sleep(interval)

det = inference.inference(4, './weight/_apex416.onnx')

print("""
  _____       _                _____ __  __ 
 |  __ \     (_)         /\   |_   _|  \/  |
 | |__) |__ _ _ _ __    /  \    | | | \  / |
 |  _  // _` | | '_ \  / /\ \   | | | |\/| |
 | | \ \ (_| | | | | |/ ____ \ _| |_| |  | |
 |_|  \_\__,_|_|_| |_/_/    \_\_____|_|  |_|                                
""")

# 初始化目标追踪器
enemy_tracker = EnemyTracker(bullet_speed, time_step)

# 加载模型
det = inference.inference(4, './weight/_apex416.onnx')

# 初始化Ghub
Ghub.INIT()
target = 1

# 初始化屏幕捕获对象
grab_size = 416
Bitblt_ = GrabScreen()
Bitblt_.setArea(grab_size, grab_size)
Bitblt_.init()
img = Bitblt_.cap()

# 开始捕获和处理循环
def main_loop():
    last_capture_time = time.time()
    while True:
        t1 = time.time()
        img = Bitblt_.cap()
        if img is not None:
            result = det.infer(img)
            cls_target = []
            x_di = 0
            y_di = 0
            if result is not None:
                for box in result:
                    x1, y1, x2, y2, _, cls = box
                    if cls == target:
                        cls_target.append([x1, y1, x2, y2])
                if len(cls_target) > 0:
                    t = cls_target[0]
                    x_di = (t[0] + t[2]) // 2 - grab_size // 2
                    y_di = (t[1] + t[3]) // 2 - grab_size // 2
                    current_enemy_pos = (x_di, y_di)
                    # 使用敌人追踪器预测敌人位置
                    predicted_x = enemy_tracker.predict_enemy_position(current_enemy_pos)
                    predicted_y = current_enemy_pos[1]  # 这里仍然使用原始的y值
                    x_di = predicted_x // sens_scaler
                    y_di = predicted_y // sens_scaler

                    if get_async_key_state(0x10) > 1:
                        threading.Thread(target=smooth_mouse_move, args=(x_di, y_di)).start()

        t2 = time.time()
        
        last_capture_time = t1
        
        delay = max(10, int(1000 / TargetFps - (t2 - t1) * 1000)) 
        time.sleep(delay / 1000)

# 启动主循环线程
threading.Thread(target=main_loop).start()