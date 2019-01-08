from pygears import gear, Intf
from pygears.typing import Queue, Uint, Tuple

from ii_gen import ii_gen
from img_ram import img_ram

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.common import shred

from image import loadImage

import math

img = loadImage("../datasets/rtl.pgm")
img_size = img.shape
frame_size = (5, 5)

din_t = Queue[Uint[8], 1]
w_addr = math.ceil(math.log(img_size[0] * img_size[1], 2))
addr_t = Queue[Uint[w_addr], 3]


@gear
def cascade_classifier(din: Queue[Uint['w_din'], 1],
                       rd_addr: Queue[Uint['w_addr'], 3],
                       *,
                       img_size=(240, 320),
                       frame_size=(25, 25)):

    dout = img_ram(din, rd_addr, img_size=img_size) \
        | ii_gen(frame_size=frame_size)

    return dout


if __name__ == "__main__":
    rd_seq = []
    for n in range(2):
        rd_seq_y = []
        for y in range(frame_size[0]):
            rd_seq_x = []
            for x in range(frame_size[1]):
                rd_seq_x.append(x + y * frame_size[1])
            rd_seq_y.append(rd_seq_x)
        rd_seq.append(rd_seq_y)
    rd_seq = [rd_seq]
    seq = [img.flatten()]

    cascade_classifier(
        din=drv(t=din_t, seq=seq),
        rd_addr=drv(t=addr_t, seq=rd_seq),
        img_size=img_size,
        frame_size=frame_size,
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
