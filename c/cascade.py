import numpy.ctypeslib as ctl
import ctypes
import numpy as np
# from image import ImageClass
import cv2
import time

libname = 'cascade.so'
libdir = './'
lib = ctl.load_library(libname, libdir)

img_fn = '../datasets/lena.pgm'
img2_fn = '../datasets/cat.jpg'
img2 = cv2.imread(img2_fn)

img = cv2.imread(img_fn, 0)
img_clr = cv2.imread(img_fn)
img = img.astype('u2')

img_num = 1
detect = lib.detect
detect.argtypes = [
    ctl.ndpointer(np.uint16, flags='aligned, c_contiguous'),
    ctypes.c_int,
    ctypes.c_int,
    ctl.ndpointer(np.uint16, flags='aligned, c_contiguous'),
    ctypes.c_float
]

start_time = time.time()

# res = 5
# print(res.shape)
# print(res)
res = np.zeros(shape=(1000,4), dtype='u2')
res_num = 0
for i in range(img_num):
    res_num = detect(img, img.shape[0], img.shape[1], res, 1.2)
    print(res)

stop_time = time.time()
print(
    "--- Time --------- %s ms ---" % (stop_time * 1000 - start_time * 1000))

print("---- FPS ------- %.2f  fps ----" % float(img_num/float(stop_time-start_time)))

for i in range(res_num):
    print(res[i])
    cv2.rectangle(
        img_clr, (res[i][0], res[i][1]),
        (res[i][0] + res[i][2], res[i][1] + res[i][3]),
        (0, 255, 0), 2)

print(
    "--- Time --------- %s ms ---" % (time.time() * 1000 - start_time * 1000))

while(1):
    cv2.imshow('img', img_clr)
    cv2.waitKey(0)
    cv2.imshow('img', img2)
    cv2.waitKey(0)

cv2.destroyAllWindows()
