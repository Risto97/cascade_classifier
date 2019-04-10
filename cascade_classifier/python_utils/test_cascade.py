import cv2
import xmltodict
from cascade_classifier.python_utils.cascade import CascadeClass
from cascade_classifier.python_utils.frame import FrameClass
from cascade_classifier.python_utils.image import ImageClass
import numpy as np

import time

img_fn = '../datasets/lena.pgm'
xml_file = r"../xml_models/haarcascade_frontalface_default.xml"

img = ImageClass()
cascade = CascadeClass(xml_file)

img.loadImage(img_fn)
img.scaleFactor = 1.2

start_time = time.time()
bounding_box = [cascade.featureSize[0], cascade.featureSize[1]]
subwindow = []
while (img.orig_img.shape[0] / img.factor > cascade.featureSize[0] + 1
       and img.orig_img.shape[1] / img.factor > cascade.featureSize[1] + 1):

    bounding_box_factor = img.bounding_box_factor

    for y in range(len(img.img) - cascade.featureSize[1] - 1):
        for x in range(len(img.img[0]) - cascade.featureSize[0]):
            frame = FrameClass()
            frame.frame = img.img[y:y + cascade.featureSize[0]+1, \
                                     x:x + cascade.featureSize[1]+1]

            frame.frame_size = (cascade.featureSize[0] + 1,
                                cascade.featureSize[1] + 1)
            # frame.calcIntegral()
            # frame.calcSquareImage()
            frame.calcCV()
            stddev = frame.calcStddev()

            if cascade.detect(frame, stddev) is True:
                window = {
                    'x': int(x * bounding_box_factor),
                    'y': int(y * bounding_box_factor),
                    'width': int(cascade.featureSize[1] * bounding_box_factor),
                    'height': int(cascade.featureSize[0] * bounding_box_factor)
                }
                subwindow.append(window)
                print(f"detected x:{x}, y:{y}")
    img.imageScaler()

for window in subwindow:
    cv2.rectangle(
        img.img_marked, (window['x'], window['y']),
        (window['x'] + window['width'], window['y'] + window['height']),
        (0, 255, 0), 2)

print("--- Time --------- %s ms ---" % (time.time() * 1000 - start_time * 1000))
cv2.imshow('img', img.img_marked)
cv2.waitKey(0)
cv2.destroyAllWindows()
