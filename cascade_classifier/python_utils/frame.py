import cv2
import numpy as np
import time
import math


class FrameClass(object):
    def __init__(self, img_fn, frame_size=None):
        self.img = cv2.imread(img_fn, 0)

        if frame_size is not None:
            self.img = self.img[0:frame_size[0], 0:frame_size[1]]

    def __str__(self):
        return f"""frame_size: {self.frame_size}
img: {self.img}
ii: {self.ii}
sii: {self.sii}
stddev: {self.stddev}
        """

    def calcCV(self):
        self.ii, self.sii = cv2.integral2(self.img)

        self.sii = np.delete(self.sii, (0), axis=0)
        self.sii = np.delete(self.sii, (0), axis=1)
        self.ii = np.delete(self.ii, (0), axis=0)
        self.ii = np.delete(self.ii, (0), axis=1)

    def set_frame_size(self, frame_size):
        self.img = self.img[0:frame_size[0], 0:frame_size[1]]

    @property
    def ii_sum(self):
        ii, frame_size = self.ii, self.frame_size
        return ii[0][0] + ii[frame_size[0] - 1][frame_size[1] - 1] - ii[
            frame_size[0] - 1][0] - ii[0][frame_size[1] - 1]

    @property
    def sii_sum(self):
        sii, frame_size = self.sii, self.frame_size
        return sii[0][0] + sii[frame_size[0] - 1][frame_size[1] - 1] - sii[
            frame_size[0] - 1][0] - sii[0][frame_size[1] - 1]

    @property
    def frame_size(self):
        return self.img.shape

    @property
    def ii(self):
        ii = np.zeros(self.frame_size, dtype='u4')

        for y in range(self.frame_size[0]):
            sum_row = 0
            for x in range(self.frame_size[1]):
                sum_row += self.img[y][x]
                if y > 0:
                    ii[y][x] = sum_row + ii[y - 1][x]
                else:
                    ii[y][x] = sum_row

        return ii

    @property
    def sii(self):
        sii = np.zeros(self.frame_size, dtype='u8')
        col_sum = [0] * self.frame_size[1]

        for y in range(self.frame_size[0]):
            row_sum = 0
            for x in range(self.frame_size[1]):
                product = np.uint64(self.img[y][x]) * np.uint64(self.img[y][x])
                col_sum[x] += product
                row_sum += product
                if y == 0:
                    sii[y][x] = row_sum
                else:
                    sii[y][x] = col_sum[x]
                    if x > 0:
                        sii[y][x] += sii[y][x - 1]

        return sii

    @property
    def stddev(self):
        sii = np.zeros((2, 2), dtype='u8')
        feature_size = (self.frame_size[0] - 1, self.frame_size[1] - 1)

        mean = self.ii[0][0] + self.ii[feature_size[0]][feature_size[
            1]] - self.ii[0][feature_size[1]] - self.ii[feature_size[0]][0]

        sii[0][0] = self.sii[0][0]
        sii[0][1] = self.sii[0][feature_size[1]]
        sii[1][0] = self.sii[feature_size[0]][0]
        sii[1][1] = self.sii[feature_size[0]][feature_size[1]]

        stddev = sii[1][1] - sii[0][1] - sii[1][0] + sii[0][0]
        stddev = (stddev * feature_size[0] * feature_size[1])
        mean_sq = np.uint64(np.uint64(mean) * np.uint64(mean))
        stddev = stddev - mean_sq

        if (stddev > 0):
            stddev = int(math.sqrt(stddev))
        else:
            stddev = 1

        return stddev


if __name__ == "__main__":
    img_fn = '../datasets/proba.pgm'

    img = FrameClass(img_fn)

    for i in range(5):
        for j in range(5):
            img.img[i, j] = j + 1 + i * 5

    img.set_frame_size((5, 5))

    print(img)
    print(img.ii_sum)
    print(img.sii_sum)
