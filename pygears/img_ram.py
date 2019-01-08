from pygears import gear, Intf
from pygears.typing import Queue, Uint, Tuple

from pygears.cookbook import sdp
from pygears.cookbook.rng import rng
from pygears.cookbook import release_after_eot
from pygears.common import shred, const, ccat, decoupler

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from image import loadImage

import math

img = loadImage("../datasets/rtl.pgm")
img_size = img.shape

din_t = Queue[Uint[8], 1]
w_addr = math.ceil(math.log(img_size[0]*img_size[1], 2))
addr_t = Queue[Uint[w_addr], 1]


@gear
def img_ram(din: Queue[Uint['w_data'], 1],
            rd_addr: Queue[Uint['w_addr'], 1],
            *,
            img_size=(240, 320)):
    ##########Parameters###################
    ram_size = img_size[0] * img_size[1]
    w_addr = math.ceil(math.log(ram_size, 2))
    #######################################

    cfg_rng = ccat(
        const(tout=Uint[1], val=0), const(tout=Uint[w_addr], val=ram_size),
        const(tout=Uint[1], val=1))
    wr_addr = cfg_rng | rng

    wr_sdp = ccat(wr_addr[0], din[0])
    rd_addr_sdp, pred = release_after_eot(rd_addr, din)
    pred | shred

    rd_data = sdp(wr_sdp, rd_addr_sdp[0], depth=ram_size)

    return rd_data


rd_seq = [list(range(img_size[0] * img_size[1]))]
seq = [img.flatten()]
img_ram(
    din=drv(t=din_t, seq=seq),
    rd_addr=drv(t=addr_t, seq=rd_seq),
    img_size=img_size,
    sim_cls=SimVerilated) | shred

sim(outdir='build',
    check_activity=True,
    extens=[partial(PyGearsView, live=True, reload=True)])
