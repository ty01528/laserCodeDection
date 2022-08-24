import time

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QMutex, QThread
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMainWindow
from skimage.viewer.qt import Signal

from lib import gxipy


class displayCam(QThread, QMainWindow):
    updateFrame = Signal(QImage)

    def __init__(self):
        super(QThread, self).__init__()
        self.isCamOpen = None
        # self.isCamOpen = self.getCamStatus()
        # self.thread_lock = QMutex()

    def setCamStatus(self, status):
        self.isCamOpen = status

    def getCamStatus(self):
        return self.isCamOpen

    def run(self):
        # cam = True  # 写这句没什么用，就是不初始化会有黄线警告
        # 这里是对摄像头做初始化
        self.isCamOpen = self.getCamStatus()
        try:
            device_manager = gxipy.DeviceManager()
            self.cam = device_manager.open_device_by_index(1)
            self.cam.TriggerMode.set(gxipy.GxSwitchEntry.OFF)
            self.cam.ExposureTime.set(10000)
            self.cam.Gain.set(10.0)
            self.cam.stream_on()
        except:
            print("错误，找不到摄像头")
            self.isCamOpen = False
            return
        print(f'当前摄像头状态：{self.isCamOpen}')
        while self.isCamOpen:
            # print(self.status)
            raw_image = self.cam.data_stream[0].get_image()
            frame = raw_image.get_numpy_array()
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 这个可能是qt和opencv的通道顺序不一样，所以需要调整
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)
            self.updateFrame.emit(scaled_img)
        # sys.exit(-1)

    def kill_thread(self):  # 希望线程暂停 保存图像然后再开启
        # self.th.is_lock = True
        print(self.isCamOpen)
        if self.isCamOpen:
            self.terminate()  # 关闭线程
            # Give time for the thread to finish
            self.cam.stream_off()  # 关闭线程同时也要关闭相机，线程再次打开会出错
            self.cam.close_device()
