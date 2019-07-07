from pygears.lib.verif import drv
from pygears.sim.modules.verilator import SimVerilated
from functools import partial

from pygears.typing import Queue, Tuple, Uint, Union, Unit
from cascade_classifier.pygears_impl.design import cascade_classifier
from pygears.lib import shred

from cascade_classifier.python_utils.image import ImageClass
from cascade_classifier.python_utils.cascade_hw import CascadeHW

xml_file = r"../../xml_models/haarcascade_frontalface_default.xml"

img_fn = "../../datasets/rtl7.jpg"
img = ImageClass()
img.loadImage(img_fn)
img = img.img

cascade_hw = CascadeHW(xml_file, img_size=img.shape)

din_t = Queue[Uint[8], 1]
seq = [img.flatten(), img.flatten()]

detected_addr, interrupt = cascade_classifier(
    din=drv(t=din_t, seq=seq),
    casc_hw=cascade_hw,
    sim_cls=partial(SimVerilated, timeout=1000000))

detected_addr | shred
interrupt | shred
