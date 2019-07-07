from pygears import gear
from pygears.typing import Queue, Uint

from pygears.lib import sdp
from pygears.lib.rng import rng
from pygears.lib import ccat, dreg
from pygears.lib import dreg as dreg_sp

from pygears.lib import alternate_queues


@gear
def img_ram(din: Queue[Uint['w_data'], 1],
            rd_addr: Queue[Uint['w_addr'], 4],
            *,
            img_size=(240, 320)):
    ##########Parameters###################
    ram_size = img_size[0] * img_size[1]
    #######################################

    cfg_rng = ccat(0, ram_size, 1)
    wr_addr = cfg_rng | rng

    din, rd_addr_sdp = alternate_queues(din, rd_addr)
    wr_sdp = ccat(wr_addr[0], din[0])

    rd_data = sdp(wr_sdp, rd_addr_sdp[0], depth=ram_size)

    dout = ccat(rd_data, rd_addr[1] | dreg) | Queue[rd_data.dtype, 2]

    return dout | dreg_sp
