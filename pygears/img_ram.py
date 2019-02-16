from pygears import gear, Intf
from pygears.typing import Queue, Uint, Tuple

from pygears.cookbook import sdp
from pygears.cookbook.rng import rng
from pygears.cookbook import release_after_eot
from pygears.common import shred, const, ccat, dreg, flatten

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from gearbox import Gearbox
from functools import partial

from gears.queue_one_by_one import queue_one_by_one

from image import loadImage

import math


@gear
def img_ram(din: Queue[Uint['w_data'], 1],
            rd_addr: Queue[Uint['w_addr'], 4],
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

    din, rd_addr_sdp = queue_one_by_one(din, rd_addr)
    wr_sdp = ccat(wr_addr[0], din[0])

    rd_data = sdp(wr_sdp, rd_addr_sdp[0], depth=ram_size)

    dout = ccat(rd_data, rd_addr[1] | dreg) | Queue[rd_data.dtype, 2]

    return dout


if __name__ == "__main__":
    img = loadImage("../datasets/rtl.pgm")
    img_size = img.shape

    din_t = Queue[Uint[8], 1]
    w_addr = math.ceil(math.log(img_size[0] * img_size[1], 2))
    addr_t = Queue[Uint[w_addr], 3]

    rd_seq = []
    for n in range(2):
        rd_seq_y = []
        for y in range(5):
            rd_seq_x = []
            for x in range(5):
                rd_seq_x.append(x + y * 5)
            rd_seq_y.append(rd_seq_x)
        rd_seq.append(rd_seq_y)

    rd_seq = [rd_seq]
    # rd_seq = [list(range(img_size[0] * 2))]
    seq = [img.flatten()]
    img_ram(
        din=drv(t=din_t, seq=seq),
        rd_addr=drv(t=addr_t, seq=rd_seq),
        img_size=img_size,
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(Gearbox, live=True, reload=True)])
