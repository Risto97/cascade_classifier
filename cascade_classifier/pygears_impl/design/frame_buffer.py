from pygears import gear
from pygears.typing import Queue, Uint, Array, Int, Tuple, Unit

from pygears.cookbook import sdp
from pygears.cookbook.rng import rng
from pygears.common import ccat, decoupler, dreg
from pygears.common import local_rst

from pygears.cookbook import alternate_queues

import math


@gear
def frame_buffer(din: Queue[Uint['w_din'], 1], rd_addr: Queue[
        Array[Tuple[Uint['w_rect'], Uint[1], Int['w_weight']], 3], 3],
                 rst_in: Unit, *, frame_size):
    ##########Parameters###################
    ram_size = frame_size[0] * frame_size[1]
    w_addr = math.ceil(math.log(ram_size, 2))
    #######################################
    rst_in | local_rst

    din_i, rd_addr_sdp = alternate_queues(din, rd_addr)
    rd_addr_sdp_dreg = rd_addr_sdp | dreg

    cfg_rng = ccat(0, Uint[w_addr](ram_size), 1)
    wr_addr = cfg_rng | rng

    wr_sdp = ccat(wr_addr[0], din_i[0])

    rd_data0 = sdp(wr_sdp, rd_addr_sdp[0][0][0], depth=ram_size)
    rd_data1 = sdp(wr_sdp, rd_addr_sdp[0][1][0], depth=ram_size)
    rd_data2 = sdp(wr_sdp, rd_addr_sdp[0][2][0], depth=ram_size)

    rd_data0 = ccat(rd_data0, rd_addr_sdp_dreg[0][0][1],
                    rd_addr_sdp_dreg[0][0][2])
    rd_data1 = ccat(rd_data1, rd_addr_sdp_dreg[0][1][1],
                    rd_addr_sdp_dreg[0][1][2])
    rd_data2 = ccat(rd_data2, rd_addr_sdp_dreg[0][2][1],
                    rd_addr_sdp_dreg[0][2][2])

    rd_data = ccat(rd_data0, rd_data1, rd_data2) | Array[rd_data0.dtype, 3]

    dout = ccat(rd_data, rd_addr_sdp_dreg[1]) | Queue[rd_data.dtype, 3]

    return dout | decoupler
