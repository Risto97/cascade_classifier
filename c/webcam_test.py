import numpy.ctypeslib as ctl
import ctypes
import numpy as np
# from image import ImageClass
import cv2
import time


libname = 'cascade.so'
libdir = './'
lib = ctl.load_library(libname, libdir)

detect = lib.detect
detect.argtypes = [
    ctl.ndpointer(np.uint8, flags='aligned, c_contiguous'),
    ctypes.c_int,
    ctypes.c_int,
    ctl.ndpointer(np.uint16, flags='aligned, c_contiguous'),
    ctypes.c_float
]

cap = cv2.VideoCapture(0)
ret = cap.set(3,240)
ret = cap.set(4,320)

res = np.zeros(shape=(1000,4), dtype='u2')
res_num = 0
frames_num = 0
exec_time = 0
while(True):

    if frames_num == 20:
        print("--- FPS --------- %.2f fps ---" % float(20/(exec_time/1000)))
        frames_num = 0

    if frames_num == 0:
        exec_time = 0

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = gray.astype('u1')

    start_time = time.time()
    res_num = detect(gray, gray.shape[0], gray.shape[1], res, 1.2)
    exec_time += time.time()*1000 - start_time*1000

    for i in range(res_num):
        cv2.rectangle(
            frame, (res[i][0], res[i][1]),
            (res[i][0] + res[i][2], res[i][1] + res[i][3]),
            (0, 255, 0), 2)

    cv2.imshow('img', frame)
    frames_num += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
