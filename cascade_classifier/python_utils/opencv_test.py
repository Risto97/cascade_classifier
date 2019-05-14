import numpy as np
import cv2
import time
import glob


face_cascade = cv2.CascadeClassifier('../xml_models/haarcascade_frontalface_default.xml')

filenames = [img for img in glob.glob("../datasets/testset/resized/*.jpg")]
img_num = len(filenames)

stop_time = 0
exec_time = 0

for img_index, img_fn in enumerate(filenames):
    img = cv2.imread(img_fn)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    start_time = time.time()
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1/0.75)
    stop_time = time.time()
    print("--- openCV --------- %s ms ---" % (stop_time * 1000 - start_time * 1000))

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]


    cv2.imshow('img', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
