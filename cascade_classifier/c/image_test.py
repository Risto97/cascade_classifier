import numpy.ctypeslib as ctl
import ctypes
import numpy as np
import cv2
import time
import glob

libname = 'cascade.so'
libdir = './'
lib = ctl.load_library(libname, libdir)

# filenames = [img for img in glob.glob("../datasets/thesis/rotated.jpg")]
filenames = [img for img in glob.glob("../datasets/testset/resized/*.jpg")]
img_num = len(filenames)

en_hit_stat = 1

# img_fn = '../datasets/proba3.pgm'
stop_time = 0
exec_time = 0

for img_index, img_fn in enumerate(filenames):
    img = cv2.imread(img_fn, 0)
    img_clr = cv2.imread(img_fn)
    img = img.astype('u1')

    detect = lib.detect
    detect.argtypes = [
        ctl.ndpointer(np.uint8, flags='aligned, c_contiguous'), ctypes.c_int,
        ctypes.c_int,
        ctl.ndpointer(np.uint16, flags='aligned, c_contiguous'), ctypes.c_int,
        ctl.ndpointer(np.float32,
                      flags='aligned, c_contiguous'), ctypes.c_float
    ]

    res = np.zeros(shape=(1000, 4), dtype='u2')
    hit = np.zeros(shape=(25, 1), dtype='f4')
    res_num = 0

    start_time = time.time()
    res_num = detect(img, img.shape[0], img.shape[1], res, 1, hit, 1.33)
    stop_time = time.time()
    exec_time += stop_time - start_time

    print("results")
    for i in range(res_num):
        # print(res[i][0], res[i][1])
        cv2.rectangle(img_clr, (res[i][0], res[i][1]),
                      (res[i][0] + res[i][2], res[i][1] + res[i][3]),
                      (0, 255, 0), 2)

    # np.set_printoptions(precision=3)
    # np.set_printoptions(suppress=True)
    # print(hit)

    # cv2.imwrite(f'../datasets/thesis/rotated_res.jpg', img_clr)
    cv2.imshow('img', img_clr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

print("--- TOTAl Time --------- %s s ---" % (exec_time))
print("--- AVG Time --------- %s ms ---" % (exec_time / img_num * 1000))
print("---- FPS ------- %.2f  fps ----" % float(img_num / float(exec_time)))