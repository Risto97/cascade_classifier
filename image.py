import cv2
import numpy as np
import time


class Frame(object):
    def __init__(self):
        frame_size = (0, 0)
        frame = []
        frame_ii = []
        frame_si = []
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
        self.frame_si = np.zeros(self.frame_size, dtype='u8')

        for x in range(len(self.frame[0])):
            for y in range(len(self.frame)):
                if y == 0:
                    self.frame_si[y][x] = np.uint64(
                        self.frame[y][x]) * np.uint64(self.frame[y][x])
                if y > 0:
                    self.frame_si[y][x] = self.frame_si[y - 1][x] + np.uint64(
                        self.frame[y][x]) * np.uint64(self.frame[y][x])

        for x in range(len(self.frame[0])):
            for y in range(len(self.frame)):
                if x == 0:
                    self.frame_si[y][x] = np.uint64(
                        self.frame[y][x]) * np.uint64(self.frame[y][x])
                else:
                    self.frame_si[y][x] = self.frame_si[y][x - 1] + np.uint64(
                        self.frame[y][x]) * np.uint64(self.frame[y][x])

        return self.frame_si


if __name__ == "__main__":
    img_fn = 'datasets/proba.pgm'

    img = Frame()
    img.frame = cv2.imread(img_fn, 0)
    img.frame_size = img.frame.shape

    start_time = time.time()
    img.calcIntegral()
    print("--- Integral Image calc ---------------- %s ms ---" %
        (time.time() * 1000 - start_time * 1000))
    start_time = time.time()
    img.calcSquareImage()
    print("--- Square Integral Image Calc --------- %s ms ---" %
        (time.time() * 1000 - start_time * 1000))
