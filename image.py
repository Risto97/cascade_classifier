import numpy as np
import cv2

class ImageClass(object):
    def __init__(self):
        self.img_size = (0, 0)
        self.img_marked = []
        self.img_scaled = 0
        self.orig_img = []
        self.img = []
        self.scaleFactor = 1
        self.factor = 1
        self.bounding_box_factor = 0

    def imageScaler(self):
        self.img_scaled = 1
        self.factor = self.factor * self.scaleFactor

        src_size = self.orig_img.shape
        self.img_size = (int(src_size[0] / self.factor),
                         int(src_size[1] / self.factor))

        self.bounding_box_factor = src_size[0] / self.img_size[0]
        w1 = int(src_size[1])
        h1 = int(src_size[0])
        w2 = int(self.img_size[1])
        h2 = int(self.img_size[0])
        self.img = np.zeros((h2, w2), dtype=('u2'))

        x_ratio = int((w1 << 16) / w2 + 1)
        y_ratio = int((h1 << 16) / h2 + 1)

        for i in range(h1):
            for j in range(w1):
                if j < w2 and i < h2:
                    self.img[i][j] = self.orig_img[
                        (i * y_ratio) >> 16][(j * x_ratio) >> 16]

        return self.img

    def loadImage(self, fn):
        self.orig_img = cv2.imread(fn,0)
        self.img = self.orig_img
        self.img_marked = cv2.imread(fn)
        self.img_size = self.orig_img.shape
        self.img_scaled = 0
        self.factor = 1
