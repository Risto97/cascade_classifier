from pygears import gear
from pygears.typing import Queue, Uint

from pygears.cookbook import sdp
from pygears.cookbook.rng import rng
from pygears.common import ccat, dreg, flatten

from gears.queue_ops import queue_one_by_one

import math


@gear
def frame_buffer(din: Queue[Uint['w_din'], 1],
                 rd_addr: Queue[Uint['w_addr'], 2],
                 *,
                 frame_size=(25, 25)):
    ##########Parameters###################
    ram_size = frame_size[0] * frame_size[1]
    w_addr = math.ceil(math.log(ram_size, 2))
    #######################################
    din_i, rd_addr_sdp = queue_one_by_one(din, rd_addr | flatten)

    cfg_rng = ccat(0, Uint[w_addr](ram_size), 1)
    wr_addr = cfg_rng | rng

    wr_sdp = ccat(wr_addr[0], din_i[0])

    rd_data = sdp(wr_sdp, rd_addr_sdp[0], depth=ram_size)

    dout = ccat(rd_data, rd_addr_sdp[1] | dreg) | Queue[rd_data.dtype, 2]

    return dout
