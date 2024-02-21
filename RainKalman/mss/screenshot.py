from mss import mss
import numpy as np
import cv2

# import pyautogui
# from PIL import ImageGrab

class grab_screen:
    """mss 截图模块"""
    def __init__(self,
                 grab_size : int,
                 screen_x : int,
                 screen_y : int
    ) -> None:



    #这段是标准mss方法,10+ms
         
        self.grab_area = {
            'left' : (screen_x - grab_size) // 2,
            'top' : (screen_y - grab_size) // 2,
            'width' : grab_size,
            'height' : grab_size
        }

        self.sct = mss()
        
    def cap(self) -> np.ndarray:
        img = self.sct.grab(self.grab_area)
        img = np.array(img)
        img = cv2.cvtColor(img,cv2.COLOR_BGRA2BGR)
        return img
    


    #这段是pyautogui方法,50+ms
          
    #     self.grab_area = ((screen_x - grab_size) // 2, (screen_y - grab_size) // 2, grab_size, grab_size)
        
    # def cap(self) -> np.ndarray:
    #     img = pyautogui.screenshot(region=self.grab_area)
    #     img = np.array(img)
    #     img = cv2.cvtColor(img,cv2.COLOR_BGRA2BGR)
    #     return img
    


    #这段是pillow方法,40+ms

    #     self.grab_area = ((screen_x - grab_size) // 2, (screen_y - grab_size) // 2, ((screen_x - grab_size) // 2) + grab_size, ((screen_y - grab_size) // 2) + grab_size)
    
    # def cap(self) -> np.ndarray:
    #     img = ImageGrab.grab(self.grab_area)
    #     img = np.array(img)
    #     img = cv2.cvtColor(img,cv2.COLOR_BGRA2BGR)
    #     return img



if __name__ == '__main__':
    sc = grab_screen(
        240,
        1600,
        900
    )
    from time import perf_counter as tp

    while True:
        t1 = tp()
        img = sc.cap()
        t2 = tp()
        print(
            round(((t2 - t1)*1000),6)
        )
        cv2.imshow(
            'green player',
            img
        )
        
        cv2.waitKey(1)