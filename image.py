import cv2
import numpy as np
import time
import math


class Frame(object):
    def __init__(self):
        frame_size = (0, 0)
        frame = []
        frame_ii = []
        frame_sii = []
        stddev = 0
        mean = 0

    def calcIntegral(self):
        self.frame_ii = np.zeros(self.frame_size, dtype='u4')

        for x in range(len(self.frame[0])):
            for y in range(len(self.frame)):
                if y == 0:
                    self.frame_ii[y][x] = self.frame[y][x]
                if y > 0:
                    self.frame_ii[y][
                        x] = self.frame_ii[y - 1][x] + self.frame[y][x]

        for x in range(len(self.frame[0])):
            for y in range(len(self.frame)):
                if x == 0:
                    self.frame_ii[y][x] = self.frame_ii[y][x]
                else:
                    self.frame_ii[y][
                        x] = self.frame_ii[y][x - 1] + self.frame_ii[y][x]

        return self.frame_ii

    def calcSquareImage(self):
        self.frame_sii = np.zeros(self.frame_size, dtype='u8')

        for x in range(len(self.frame[0])):
            for y in range(len(self.frame)):
                if y == 0:
                    self.frame_sii[y][x] = np.uint64(
                        self.frame[y][x]) * np.uint64(self.frame[y][x])
                if y > 0:
                    self.frame_sii[y][
                        x] = self.frame_sii[y - 1][x] + np.uint64(
                            self.frame[y][x]) * np.uint64(self.frame[y][x])

        for x in range(len(self.frame[0])):
            for y in range(len(self.frame)):
                if x == 0:
                    self.frame_sii[y][x] = np.uint64(
                        self.frame[y][x]) * np.uint64(self.frame[y][x])
                else:
                    self.frame_sii[y][
                        x] = self.frame_sii[y][x - 1] + np.uint64(
                            self.frame[y][x]) * np.uint64(self.frame[y][x])

        for x in range(len(self.frame[0])):
            for y in range(len(self.frame)):
                if(y > 0):
                    self.frame_sii[y][x] = self.frame_sii[y-1][x] + self.frame_sii[y][x]

        return self.frame_sii

    def calcStddev(self):
        sii = np.zeros((2, 2), dtype='u8')
        feature_size = (self.frame_size[0] - 1, self.frame_size[1] - 1)

        mean = self.frame_ii[0][0] + self.frame_ii[feature_size[0]][feature_size[1]] - self.frame_ii[0][feature_size[1]] - self.frame_ii[feature_size[0]][0]

        sii[0][0] = self.frame_sii[0][0]
        sii[0][1] = self.frame_sii[0][feature_size[1]]
        sii[1][0] = self.frame_sii[feature_size[0]][0]
        sii[1][1] = self.frame_sii[feature_size[0]][feature_size[1]]

        print(sii)
        stddev =  sii[1][1] - sii[0][1] - sii[1][0] + sii[0][0]
        print(stddev)
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

    img = Frame()
    img.frame = cv2.imread(img_fn, 0)
    img.frame = img.frame[0:25,0:25]
    img.frame_size = img.frame.shape

    start_time = time.time()
    img.calcIntegral()
    print("--- Integral Image calc ---------------- %s ms ---" %
          (time.time() * 1000 - start_time * 1000))
    start_time = time.time()
    img.calcSquareImage()
    print("--- Square Integral Image Calc --------- %s ms ---" %
          (time.time() * 1000 - start_time * 1000))
    start_time = time.time()
    stddev = img.calcStddev()
    print("--- Stddev calc  ------------- --------- %s ms ---" %
          (time.time() * 1000 - start_time * 1000))
