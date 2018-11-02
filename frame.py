import cv2
import numpy as np
import time
import math


class FrameClass(object):
    def __init__(self):
        frame_size = (0, 0)
        frame = []
        frame_ii = []
        frame_sii = []
        stddev = 0
        mean = 0

    def calcCV(self):
        self.frame_ii, self.frame_sii = cv2.integral2(self.frame)

        self.frame_sii = np.delete(self.frame_sii, (0), axis=0)
        self.frame_sii = np.delete(self.frame_sii, (0), axis=1)
        self.frame_ii = np.delete(self.frame_ii, (0), axis=0)
        self.frame_ii = np.delete(self.frame_ii, (0), axis=1)

    def calcIntegral(self):
        self.frame_ii = np.zeros(self.frame_size, dtype='u4')

        for y in range(self.frame_size[0]):
            sum_row = 0
            for x in range(self.frame_size[1]):
                sum_row += self.frame[y][x]
                if y > 0:
                    self.frame_ii[y][x] = sum_row + self.frame_ii[y - 1][x]
                else:
                    self.frame_ii[y][x] = sum_row

        return self.frame_ii

    def calcSquareImage(self):
        self.frame_sii = np.zeros(self.frame_size, dtype='u8')
        col_sum = [0]*self.frame_size[1]

        for y in range(self.frame_size[0]):
            row_sum = 0
            for x in range(self.frame_size[1]):
                product = np.uint64(self.frame[y][x]) * np.uint64(self.frame[y][x])
                col_sum[x] += product
                row_sum += product
                if y == 0:
                    self.frame_sii[y][x] = row_sum
                else:
                    self.frame_sii[y][x] = col_sum[x]
                    if x > 0:
                        self.frame_sii[y][x] += self.frame_sii[y][x-1]

        return self.frame_sii

    def calcStddev(self):
        sii = np.zeros((2, 2), dtype='u8')
        feature_size = (self.frame_size[0] - 1, self.frame_size[1] - 1)

        mean = self.frame_ii[0][0] + self.frame_ii[feature_size[0]][feature_size[1]] - self.frame_ii[0][feature_size[1]] - self.frame_ii[feature_size[0]][0]

        sii[0][0] = self.frame_sii[0][0]
        sii[0][1] = self.frame_sii[0][feature_size[1]]
        sii[1][0] = self.frame_sii[feature_size[0]][0]
        sii[1][1] = self.frame_sii[feature_size[0]][feature_size[1]]

        stddev = sii[1][1] - sii[0][1] - sii[1][0] + sii[0][0]
        stddev = (stddev * feature_size[0] * feature_size[1])
        mean_sq = np.uint64(np.uint64(mean) * np.uint64(mean))
        stddev = stddev - mean_sq

        if (stddev > 0):
            stddev = int(math.sqrt(stddev))
        else:
            stddev = 1

        self.stddev = stddev
        return self.stddev


if __name__ == "__main__":
    img_fn = 'datasets/proba.pgm'

    img = FrameClass()
    img.frame = cv2.imread(img_fn, 0)
    # img.frame = img.frame[0:5, 0:5]
    # img.frame[0] = [5, 4, 8, 2, 1]
    # img.frame[1] = [7, 3, 5, 9, 1]
    # img.frame[2] = [3, 2, 7, 6, 4]
    # img.frame[3] = [4, 5, 1, 2, 9]
    # img.frame[4] = [9, 7, 3, 7, 2]
    img.frame_size = img.frame.shape

    start_time = time.time()
    img.calcIntegral()
    print("--- Integral Image calc ---------------- %s ms ---" %
          (time.time() * 1000 - start_time * 1000))
    start_time = time.time()
    img.calcSquareImage()
    print("--- Square Integral Image Calc --------- %s ms ---" %
          (time.time() * 1000 - start_time * 1000))
    stddev = img.calcStddev()
    print("--- Stddev calc  ------------- --------- %s ms ---" %
          (time.time() * 1000 - start_time * 1000))
    start_time = time.time()
    img.calcCV()
    print("--- OpenCV calc  ------------- --------- %s ms ---" %
          (time.time() * 1000 - start_time * 1000))
