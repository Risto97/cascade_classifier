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
img = cv2.imread(img_fn, 0)
img = img.astype('u2')

img_num = 1
detect = lib.detect
detect.argtypes = [
    ctl.ndpointer(np.uint16, flags='aligned, c_contiguous'), ctypes.c_int,
    ctypes.c_int, ctypes.c_float
]

start_time = time.time()

for i in range(img_num):
    print(detect(img, img.shape[0], img.shape[1], 1.2))
stop_time = time.time()
print(
    "--- Time --------- %s ms ---" % (stop_time * 1000 - start_time * 1000))

print("---- FPS ------- %.2f  fps ----" % float(img_num/float(stop_time-start_time)))
