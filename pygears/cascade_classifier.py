from pygears import gear, Intf
from pygears.typing import Queue, Uint, Tuple

from ii_gen import ii_gen
from ii_gen import sii_gen
from img_ram import img_ram
from rd_addrgen import rd_addrgen, addr_trans
from stddev import stddev

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.common import shred, czip, ccat, zip_sync

from pygears.svgen import svgen

from image import loadImage

import math

img = loadImage("../datasets/rtl.pgm")
img_size = img.shape
frame_size = (25, 25)
w_addr = math.ceil(math.log(img_size[0] * img_size[1], 2))
addr_t = Queue[Uint[w_addr], 3]
din_t = Queue[Uint[8], 1]

seq = [img.flatten()]

@gear
def cascade_classifier(din: Queue[Uint['w_din'], 1],
                       # rd_addr: Queue[Uint['w_addr'], 3],
                       *,
                       img_size=(240, 320),
                       frame_size=(25, 25)):

    rd_addr_s = rd_addrgen(img_size=img_size, frame_size=frame_size) | addr_trans(img_size=img_size) | Queue[Uint[12], 3]
    img_s = img_ram(din, rd_addr_s, img_size=img_size)

    ii_s1 = img_s | ii_gen(frame_size=frame_size)
    sii_s1 = img_s | sii_gen(frame_size=frame_size)

    ii_s, sii_s = zip_sync(ii_s1, sii_s1, outsync=False)

    # print(ii_s.dtype)
    # print(sii_s.dtype)

    # stddev_in = ccat(ii_s[0], sii_s[0])

    # stddev_in = ccat(stddev_in, ii_s[1]) | Queue[Tuple[ii_s[0].dtype, sii_s[0].dtype], 2]

    # print(stddev_in.dtype)

    # dout = stddev_in | stddev( frame_size=frame_size)
    dout = stddev(ii_s, sii_s, frame_size=frame_size)

    return dout
    # return (ccat(ii_s, sii_s))


if __name__ == "__main__":

    # cascade_classifier(Intf(Queue[Uint[8],1]), img_size=img_size, frame_size=frame_size)
    # svgen('/cascade_classifier', outdir='build2/cascade_classifier', wrapper=True)

    cascade_classifier(
        din=drv(t=din_t, seq=seq),
        # rd_addr=drv(t=addr_t, seq=rd_seq),
        img_size=img_size,
        frame_size=frame_size,
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
