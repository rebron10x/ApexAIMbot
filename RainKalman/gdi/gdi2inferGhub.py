from grab_gdi import GrabScreen 
import inference
import cv2
from time import perf_counter as tp
import time
from pynput import mouse
import ctypes

User32 = ctypes.windll.user32

get_async_key_state = User32.GetAsyncKeyState
get_async_key_state.argtypes = (ctypes.c_int,)

Ghub = ctypes.cdll.LoadLibrary('./tools/Ghub.dll')#文件路径

def show_window(result) -> None :
    """可视化推理结果"""
    for x1, y1, x2, y2, _, cls in result:

        if cls == target:
            color = (0,0,255)
            text = 'target'

        else:
            color = (0,255,0)
            text = 'not target'

        cv2.rectangle(img,(int(x1),int(y1)),(int(x2),int(y2)),color,1)
        cv2.putText(img,text,(int(x1),int(y1)),cv2.FONT_HERSHEY_COMPLEX,0.6,color,1)  
    cv2.namedWindow('green player', cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty('green player', cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow('green player',img)
    cv2.waitKey(1)  

def on_click(x,y,button,pressed):
    print('click at',x,y,button,pressed)

def listen_mouse_nblock():
    listener = mouse.Listener(
        on_move=None, # 因为on_move太多输出了，就不放进来了，有兴趣可以加入
        on_click=on_click,
        on_scroll=None
    )
    listener.start()

det = inference.inference(
    4,'./weight/_apex416.onnx'
)

target = 1

Ghub.INIT()

grab_size = 416

Bitblt_ = GrabScreen()
Bitblt_.setArea(grab_size, grab_size)
Bitblt_.init()

while True:

    t1 = tp()

    img = Bitblt_.cap()

    if img is not None:
        
        result = det.infer(img)

        cls_target = []
        cls_other = []
        x_di = 0
        y_di = 0

        if result is not None:
            show_window(result)
            for box in result:
                x1,y1,x2,y2,_,cls = box
                if cls == target:
                    cls_target.append([x1,y1,x2,y2])
                else:
                    cls_other.append([x1,y1,x2,y2])
        if len(cls_target) == 0:
            pass
        elif len(cls_target) == 1:
            t = cls_target[0]

            x_di = (t[0]+t[2]) //2 - grab_size //2
            y_di = (t[1]+t[3]) //2 - grab_size //2
        
        else:
            distance = []
            for t in cls_target:
                x_dist = (t[0] + t[2]) // 2 - grab_size // 2
                y_dist = (t[1] + t[3]) // 2 - grab_size // 2

                dist = (x_dist ** 2 + y_dist ** 2) ** 0.5

                distance.append(dist)
            min_index = distance.index(min(distance))
            t = cls_target[min_index]

            x_di = (t[0] + t[2]) // 2 - grab_size // 2
            y_di = (t[1] + t[3]) // 2 - grab_size // 2
        
        # print(
        #     f'x轴距离：{x_di} || y轴距离：{y_di}'
        # )
        
        if get_async_key_state(0x01) > 1:
            Ghub.MoveR(int(x_di),int(y_di))
    t2 = tp()
    print(t2-t1)
    if (t2-t1) < 30 :
        time.sleep((50-t2+t1)/1000)
        
            


