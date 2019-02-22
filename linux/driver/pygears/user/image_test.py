import numpy.ctypeslib as ctl
import ctypes
import numpy as np
import cv2
import time
import glob

displayRes = 1
breaker = 0

libname = 'detect.so'
libdir = './'
lib = ctl.load_library(libname, libdir)

filenames = [img for img in glob.glob("dataset/resized/*jpg")]
# filenames = [img for img in glob.glob("dataset/resized/img314.jpg")]
# filenames = [img for img in glob.glob("dataset/*.jpg")]
img_num = len(filenames)
res = np.zeros(shape=(1, 1024), dtype='u4')

stop_time = 0
exec_time = 0
for img_index, img_fn in enumerate(filenames):
    if breaker == 0:
        print(img_fn)
        start_time = time.time()
        img = cv2.imread(img_fn, 0)
        img = img.astype('u4')
        img[-1][-1] = 65535
        pos = []
        # print(img)

        detect = lib.detect

        detect.argtypes = [
            ctl.ndpointer(np.uint32, flags='aligned, c_contiguous'),
            ctl.ndpointer(np.uint32, flags='aligned, c_contiguous')
        ]

        stop_time = time.time()
        # print("--- SW Time --------- %s s ---" % (stop_time - start_time))
        start_time = time.time()
        res_num = detect(img, res)
        stop_time = time.time()
        print("IMG number ", img_index)
        print(res[0,:res_num-1])
        # exec_time += stop_time - start_time
        print("--- HW Time --------- %s s ---" % (stop_time - start_time))

        for val in res[0,:res_num-1]:
            scale = (val & 0x0000000F)
            pos_x = (val & 0x00003FF0) >> 4
            pos_y = (val & 0x00FFC000) >> 14
            print(scale, pos_y, pos_x)
            pos.append((scale, pos_y, pos_x))

        if displayRes:
            img_clr = cv2.imread(img_fn)
            for val in pos:
                scale_tmp = 1.33**val[0]
                cv2.rectangle(img_clr, (int(val[1]*scale_tmp), int(val[2]*scale_tmp)),
                            (int(val[1]*scale_tmp) + int(25*scale_tmp), int(val[2]*scale_tmp) + int(25*scale_tmp)),
                            (0, 255, 0), 2)
            cv2.imshow('img', img_clr)

            c = cv2.waitKey(0)

            if 'q' == chr(c & 255):
                breaker = 1
            else:
                continue

cv2.destroyAllWindows()
