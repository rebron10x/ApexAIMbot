import ctypes
import numpy as np
from ctypes import wintypes
import atexit
import threading

class GrabScreen:
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32

    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)

    awareness = ctypes.c_void_p(0)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

    _monitor_width = round(width * scale_factor)
    _monitor_height = round(height * scale_factor)

    def __init__(self) -> None:
        pass

    def setArea(self, GrabWidth: int, GrabHeight: int) -> None:
        self._x = round((self._monitor_width / 2) - (GrabWidth / 2))
        self._y = round((self._monitor_height / 2) - (GrabHeight / 2))
        self._w = GrabWidth
        self._h = GrabHeight

    def init(self) -> None:
        self.hwnd = self.user32.GetDesktopWindow()
        self.desktop_dc = self.user32.GetDC(self.hwnd)
        self.mem_dc = self.gdi32.CreateCompatibleDC(self.desktop_dc)
        self.bitmap = self.gdi32.CreateCompatibleBitmap(self.desktop_dc, self._w, self._h)
        self.old_bitmap = self.gdi32.SelectObject(self.mem_dc, self.bitmap)

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ('biSize', wintypes.DWORD),
                ('biWidth', wintypes.LONG),
                ('biHeight', wintypes.LONG),
                ('biPlanes', wintypes.WORD),
                ('biBitCount', wintypes.WORD),
                ('biCompression', wintypes.DWORD),
                ('biSizeImage', wintypes.DWORD),
                ('biXPelsPerMeter', wintypes.LONG),
                ('biYPelsPerMeter', wintypes.LONG),
                ('biClrUsed', wintypes.DWORD),
                ('biClrImportant', wintypes.DWORD)
            ]

        bi = BITMAPINFOHEADER()
        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.biWidth = self._w
        bi.biHeight = -self._h
        bi.biPlanes = 1
        bi.biBitCount = 32
        bi.biCompression = 0

        self.__buffer__ = np.zeros((self._h, self._w, 4), dtype=np.uint8)

        self.__able2write = threading.Event()
        self.__able2read = threading.Event()
        def __refresh() -> None:
            while True:
                self.__able2write.wait()
                self.__able2read.clear()

                self.gdi32.BitBlt(
                    self.mem_dc, 0, 0, 
                    self._w, self._h, 
                    self.desktop_dc, 
                    self._x, self._y, 
                    0x00CC0020)

                self.gdi32.GetDIBits(
                    self.mem_dc, self.bitmap, 0, self._h, 
                    self.__buffer__.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)), 
                    ctypes.byref(bi), 0)
                
                self.__able2read.set()

        self.__able2write.set()
        __thread = threading.Thread(target=__refresh)
        __thread.daemon = True
        __thread.start()
        atexit.register(self.cleanup)

    def cleanup(self):
        self.gdi32.SelectObject(self.mem_dc, self.old_bitmap)
        self.gdi32.DeleteDC(self.mem_dc)
        self.gdi32.DeleteObject(self.bitmap)
        self.user32.ReleaseDC(self.hwnd, self.desktop_dc)

    def cap(self) -> np.ndarray:
        try:
            self.__able2read.wait()
            self.__able2write.clear()
            return self.__buffer__
        finally:
            self.__able2write.set()


if __name__ == "__main__":
    import cv2

    Bitblt_ = GrabScreen()
    Bitblt_.setArea(416, 416)
    Bitblt_.init()

    from time import perf_counter as tp

    while True:
        t1 = tp()
        img = Bitblt_.cap()
        t2 = tp()

        print((t2 - t1) * 1000)

        cv2.imshow('demo', img)
        cv2.waitKey(1)
