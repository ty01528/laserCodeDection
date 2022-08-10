import os

import cv2
import numpy as np

from infer import Rotate, use_auto_tune, auto_tune, parse_args, Predictor
from predict_rec import start_rec


class Process():
    def __init__(self, agrs=parse_args()):
        super().__init__()
        if agrs is None:
            self.args = parse_args()
        else:
            self.args = agrs
        self.predictor = Predictor(self.args)

    def getRes(self, img):
        # collect dynamic shape by auto_tune
        if use_auto_tune(self.args):
            auto_tune(self.args, img)
        result, img = self.predictor.run(img)
        pic, ret, preds = self.startRec(result, img)
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
            imgs[1] = cv2.resize(imgs[1], (380, 60), interpolation=cv2.INTER_CUBIC)
            imgs[0] = cv2.resize(imgs[0], (380, 60), interpolation=cv2.INTER_CUBIC)
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


if __name__ == '__main__':
    pro = Process()
    pic, ret, _ = pro.getRes("pic/6.bmp")
    cv2.imshow("pic", pic[0])
    print(ret)
    cv2.waitKey(100000)
    os.remove('draw.png')
