import os
import cv2
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from front.startupWindows import Ui_MainWindow
from runtime.infer import Rotate, use_auto_tune, auto_tune, parse_args, Predictor
from runtime.predict_rec import start_rec
from ui.dispalyStatus import disTime, disCamStatus
from ui.displayCam import displayCam


class uiFunction(Ui_MainWindow):
    def startUi(self, window):
        self.setupUi(window)
        self.dectProgess.setVisible(False)
        self.onLunch()
        self.Video.setScaledContents(True)
        self.resPicFirst.setScaledContents(True)
        self.resPicSecond.setScaledContents(True)

    def onLunch(self):
        # 显示时间
        self.timeDisplay = disTime(self.LocalTime)
        self.timeDisplay.start()
        # 开启结果展示的点击函数调用
        self.resClick()
        # 显示状态
        self.camStatusDisplay = disCamStatus(self.camStatus)
        self.camStatusDisplay.start()
        # 调用摄像头并显示
        self.th1 = displayCam()
        self.th1.updateFrame.connect(self.setImage)
        QTimer.singleShot(1500, self.start)
        QTimer.singleShot(1500, self.initModel)
        self.startDec.setEnabled(False)
        self.rescue.setEnabled(False)
        # 开始检测事件
        self.startDec.clicked.connect(self.startDection)
        self.rescue.clicked.connect(self.rescueCam)

        self.Video.setPixmap(QPixmap('front/icon/logo.jpg'))

        # 这里是设置小键盘不可见
        self.widget_2.setVisible(False)
        self.widget_3.setVisible(False)
        # 这里是定义结果修改的鼠标点击事件
        self.resClickEvent()

        # 这里是设置选择的背景颜色
        self.nowSelectBG = None

    # 将摄像头的图片传递给LABEL
    def setImage(self, image):
        self.Video.setPixmap(QPixmap.fromImage(image))
        if image is None:
            self.camStatus.setStyleSheet(self.redCircle)
        else:
            self.camStatus.setStyleSheet(self.greenCircle)
        self.Video.setScaledContents(True)

    # 开始启动摄像头
    def start(self):
        print("starting....")
        self.th1.setCamStatus(True)
        self.th1.start()

    # 定义结果按钮的连接
    def resClick(self):
        self.button0.clicked.connect(lambda: self.resButtonClickEvent(0))
        self.button1.clicked.connect(lambda: self.resButtonClickEvent(1))
        self.button2.clicked.connect(lambda: self.resButtonClickEvent(2))
        self.button3.clicked.connect(lambda: self.resButtonClickEvent(3))
        self.button4.clicked.connect(lambda: self.resButtonClickEvent(4))
        self.button5.clicked.connect(lambda: self.resButtonClickEvent(5))
        self.button6.clicked.connect(lambda: self.resButtonClickEvent(6))
        self.button7.clicked.connect(lambda: self.resButtonClickEvent(7))
        self.button8.clicked.connect(lambda: self.resButtonClickEvent(8))
        self.button9.clicked.connect(lambda: self.resButtonClickEvent(9))
        self.button0_2.clicked.connect(lambda: self.resButtonClickEvent(0))
        self.button1_2.clicked.connect(lambda: self.resButtonClickEvent(1))
        self.button2_2.clicked.connect(lambda: self.resButtonClickEvent(2))
        self.button3_2.clicked.connect(lambda: self.resButtonClickEvent(3))
        self.button4_2.clicked.connect(lambda: self.resButtonClickEvent(4))
        self.button5_2.clicked.connect(lambda: self.resButtonClickEvent(5))
        self.button6_2.clicked.connect(lambda: self.resButtonClickEvent(6))
        self.button7_2.clicked.connect(lambda: self.resButtonClickEvent(7))
        self.button8_2.clicked.connect(lambda: self.resButtonClickEvent(8))
        self.button9_2.clicked.connect(lambda: self.resButtonClickEvent(9))

    # 这里是所有插槽或者说是线程的初始化
    def initModel(self):
        self.pro = Process()
        self.Reslabel.setText("-- 等待检测 --")
        self.startDec.setEnabled(True)
        self.rescue.setEnabled(True)

    # 重置按钮事件操作
    def rescueCam(self):

        self.th1.setCamStatus(True)
        self.th1.start()
        self.initialDisplayRes(None, None, clear=True)
        self.resPicFirst.clear()
        self.resPicSecond.clear()
        self.widget_2.setVisible(False)
        self.widget_3.setVisible(False)
        self.nowSelectBG = None
        self.Reslabel.setText("-- 等待检测 --")

    # 开始检测按钮操作
    def startDection(self):
        self.Reslabel.setVisible(False)
        self.dectProgess.setVisible(True)
        self.dectProgess.setValue(24)

        # 这里是图片格式的转换
        qimg = self.Video.pixmap().toImage()
        if qimg is None:
            return
        temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
        temp_shape += (4,)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3]

        # 关线程
        if self.th1.getCamStatus():
            self.th1.kill_thread()
            self.th1.setCamStatus(False)

        cv2.imwrite("temp.png", result)
        self.dectProgess.setValue(80)
        # 读取临时图片准备识别
        # 否则应读取temp.png图片
        pic, ret, preds = self.pro.getRes("pic/1.bmp", self.dectProgess)
        cv2.imwrite("temp0.png", pic[0])
        cv2.imwrite("temp1.png", pic[1])

        if pic is None and ret is None:
            self.Reslabel.setText("-- 无法找到图中激光码区域 --")
            self.th1.start()
        else:
            self.Reslabel.setText("检测完成！")

        self.Reslabel.setVisible(True)
        self.dectProgess.setVisible(False)
        self.initialDisplayRes(ret, preds)
        self.Video.setPixmap(QPixmap('draw.png'))
        self.resPicFirst.setPixmap(QPixmap('temp1.png'))
        self.resPicSecond.setPixmap(QPixmap('temp0.png'))
        os.remove('temp.png')
        os.remove('temp0.png')
        os.remove('temp1.png')
        # os.remove('draw.png')
        # print(type(result))
        # return self.Video.setPixmap(QPixmap.fromImage(image))

    # 用于两张图片下的值的显示
    def initialDisplayRes(self, res, preds, clear=False):
        self.dis1 = [self.res1, self.res2, self.res3, self.res4, self.res5, self.res6, self.res7, self.res8, self.res9,
                     self.res10, self.res11, self.res12, self.res13, self.res14, self.res15, self.res16]
        self.dis2 = [self.res17, self.res18, self.res19, self.res20, self.res21, self.res22, self.res23, self.res24,
                     self.res25, self.res26, self.res27, self.res28, self.res29, self.res30, self.res31, self.res32]
        print(f'res')
        if clear is True:
            for i in range(0, 16):
                self.dis1[i].setText('#')
                self.dis1[i].setStyleSheet("background-color: rgb(218, 227, 243);")
            for i in range(0, 16):
                self.dis2[i].setText('#')
                self.dis2[i].setStyleSheet('background-color: rgb(218, 227, 243);')
            self.finalRes.setText("--------------------------------")
        else:
            for i in range(0, len(res[0]) if len(res[0]) <= 16 else 16):
                self.dis1[i].setText(res[0][i])
                if preds[0][i] < 0.92:
                    self.dis1[i].setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.dis1[i].setStyleSheet('background-color: rgb(0, 255, 0);')

            for i in range(0, len(res[1]) if len(res[1]) <= 16 else 16):
                self.dis2[i].setText(res[1][i])
                if preds[1][i] < 0.92:
                    self.dis2[i].setStyleSheet('background-color: rgb(255, 0, 0);')
                else:
                    self.dis2[i].setStyleSheet('background-color: rgb(0, 255, 0);')

            res0 = ''.join(res[0])
            res1 = ''.join(res[1])
            rec_result = res0 + res1
            self.finalRes.setText(rec_result)
            print(rec_result)

    def changeDisplayRes(self):
        finalres = [self.res1.text(), self.res2.text(), self.res3.text(), self.res4.text(), self.res5.text(),
                    self.res6.text(),
                    self.res7.text(), self.res8.text(), self.res9.text(), self.res10.text(), self.res11.text(),
                    self.res12.text(),
                    self.res13.text(), self.res14.text(), self.res15.text(), self.res16.text(), self.res17.text(),
                    self.res18.text(), self.res19.text(), self.res20.text(), self.res21.text(), self.res22.text(),
                    self.res23.text(), self.res24.text(), self.res25.text(), self.res26.text(), self.res27.text(),
                    self.res28.text(), self.res29.text(), self.res30.text(), self.res31.text(), self.res32.text()]
        res = ''.join(finalres)
        self.finalRes.setText(res)
        print(res)

    def resClickEvent(self):
        self.res1.connect_customized_slot(lambda: self.changeResTop(self.res1))
        self.res2.connect_customized_slot(lambda: self.changeResTop(self.res2))
        self.res3.connect_customized_slot(lambda: self.changeResTop(self.res3))
        self.res4.connect_customized_slot(lambda: self.changeResTop(self.res4))
        self.res5.connect_customized_slot(lambda: self.changeResTop(self.res5))
        self.res6.connect_customized_slot(lambda: self.changeResTop(self.res6))
        self.res7.connect_customized_slot(lambda: self.changeResTop(self.res7))
        self.res8.connect_customized_slot(lambda: self.changeResTop(self.res8))
        self.res9.connect_customized_slot(lambda: self.changeResTop(self.res9))
        self.res10.connect_customized_slot(lambda: self.changeResTop(self.res10))
        self.res11.connect_customized_slot(lambda: self.changeResTop(self.res11))
        self.res12.connect_customized_slot(lambda: self.changeResTop(self.res12))
        self.res13.connect_customized_slot(lambda: self.changeResTop(self.res13))
        self.res14.connect_customized_slot(lambda: self.changeResTop(self.res14))
        self.res15.connect_customized_slot(lambda: self.changeResTop(self.res15))
        self.res16.connect_customized_slot(lambda: self.changeResTop(self.res16))

        self.res17.connect_customized_slot(lambda: self.changeResButtom(self.res17))
        self.res18.connect_customized_slot(lambda: self.changeResButtom(self.res18))
        self.res19.connect_customized_slot(lambda: self.changeResButtom(self.res19))
        self.res20.connect_customized_slot(lambda: self.changeResButtom(self.res20))
        self.res21.connect_customized_slot(lambda: self.changeResButtom(self.res21))
        self.res22.connect_customized_slot(lambda: self.changeResButtom(self.res22))
        self.res23.connect_customized_slot(lambda: self.changeResButtom(self.res23))
        self.res24.connect_customized_slot(lambda: self.changeResButtom(self.res24))
        self.res25.connect_customized_slot(lambda: self.changeResButtom(self.res25))
        self.res26.connect_customized_slot(lambda: self.changeResButtom(self.res26))
        self.res27.connect_customized_slot(lambda: self.changeResButtom(self.res27))
        self.res28.connect_customized_slot(lambda: self.changeResButtom(self.res28))
        self.res29.connect_customized_slot(lambda: self.changeResButtom(self.res29))
        self.res30.connect_customized_slot(lambda: self.changeResButtom(self.res30))
        self.res31.connect_customized_slot(lambda: self.changeResButtom(self.res31))
        self.res32.connect_customized_slot(lambda: self.changeResButtom(self.res32))

    def changeResTop(self, MyQLabel):
        self.widget_3.setVisible(False)
        self.widget_2.setVisible(True)
        if self.nowSelectBG is not None:
            self.nowSelectBG.setStyleSheet("background-color: rgb(0, 200, 0);")
        if self.nowSelectBG == MyQLabel:
            self.widget_2.setVisible(False)
            self.nowSelectBG = None
        else:
            self.nowSelectBG = MyQLabel
            self.nowSelectBG.setStyleSheet("background-color: rgb(255, 255, 0);")

    def changeResButtom(self, MyQLabel):
        self.widget_2.setVisible(False)
        self.widget_3.setVisible(True)
        if self.nowSelectBG is not None:
            self.nowSelectBG.setStyleSheet("background-color: rgb(0, 200, 0);")
        if self.nowSelectBG == MyQLabel:
            self.widget_3.setVisible(False)
            self.nowSelectBG = None
        else:
            self.nowSelectBG = MyQLabel
            MyQLabel.setStyleSheet("background-color: rgb(255, 255, 0);")

    def resButtonClickEvent(self, val):
        self.nowSelectBG.setText(str(val))
        self.changeDisplayRes()


# 这里是识别的流程
class Process(QThread):
    def __init__(self, agrs=parse_args()):
        super().__init__()
        if agrs is None:
            self.args = parse_args()
        else:
            self.args = agrs
        self.predictor = Predictor(self.args)

    def getRes(self, img, process=QtWidgets.QProgressBar):
        # collect dynamic shape by auto_tune
        process.setValue(30)
        if use_auto_tune(self.args):
            auto_tune(self.args, img)
        process.setValue(65)
        result, img = self.predictor.run(img)
        process.setValue(90)
        pic, ret, preds = self.startRec(result, img)
        process.setValue(98)
        return pic, ret, preds

    def startRec(self, result, img):
        # 最麻烦的就是这里，需要对矩阵做转换才能提取出图像中的信息
        # 二值化的矩阵需要转置才能做叉乘
        # (1, 492, 656)这是二值化矩阵的shape
        # (492, 656, 3)这是RGB矩阵的shape
        # 取三阶矩阵前两阶与二值化矩阵做叉乘
        # 灰度图的数据格式需要转换为符合RGB的uint8格式
        # img = img * result.astype(np.uint8)
        # img = img[[not np.all(img[i] == [0, 0, 0]) for i in range(img.shape[0])], :]
        # img = img[:, [not np.all(img[:, i] == 0) for i in range(img.shape[1])]]
        # 将矩阵转成opencv的MAT格式
        result = result.transpose(1, 2, 0)
        result = result.astype(np.uint8)
        # 这里将矩阵转换为MAT的8UC3类型
        # result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        # 这里是查找图片轮廓
        drawImg = img.copy()
        contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(drawImg, contours, -1, (0, 0, 255), 1)
        # **绘制**最小外接矩形
        # bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours]
        # for bbox in bounding_boxes:
        #     [x, y, w, h] = bbox
        #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        imgs, res, preds = [], [], []
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)  # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
            # print(f"最小外接矩形的角度为{rect[1][1]}")
            area = int(rect[1][1]) * int(rect[1][0])
            # print(f"最小外接矩形的面积为{area}")
            if area < 15000:
                continue
            box = cv2.boxPoints(rect)  # cv2.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点坐标
            tmp = Rotate(img, box, rect).getImg()
            imgs.append(tmp)
            # print(f"旋转角度为{rect[2]}")
            box = np.int0(box)
            cv2.drawContours(img, [box], 0, (255, 0, 0), 1)
        cv2.imwrite("draw.png", img)
        # for i in imgs:
        #     res.append(start_rec(i).start())
        try:
            imgs[1] = cv2.resize(imgs[1], (320, 48), interpolation=cv2.INTER_CUBIC)
            imgs[0] = cv2.resize(imgs[0], (320, 48), interpolation=cv2.INTER_CUBIC)
            # image = np.hstack((imgs[1], imgs[0]))
            # cv2.imshow('1', image)
            # cv2.waitKey()
            res_temp, preds_temp = start_rec().start(imgs[1])
            res.append(res_temp)
            preds.append(preds_temp)

            res_temp, preds_temp = start_rec().start(imgs[0])
            res.append(res_temp)
            preds.append(preds_temp)
        except:
            print('找不到激光码！')
            res, imgs = None, None
        return imgs, res, preds
