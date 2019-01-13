from pygears import gear
from pygears.typing import Int, Queue, Uint, Tuple

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from frame_sum import frame_sum_tmp

from pygears.common import czip, ccat, dreg, zip_sync, decoupler
from pygears.common.rom import rom

from sqrt_approx import createSqrtApprox

from image import loadImage

import math

sqrt_addr_w = 31
sqrt_rom_depth = 256

sqrt = createSqrtApprox(sqrt_addr_w, sqrt_rom_depth)
w_sqrt = sqrt[1]
sqrt_mem = sqrt[0]


@gear
def stddev(ii_s: Queue[Uint['w_ii'], 2], sii_s: Queue[Uint['w_sii'], 2], *, frame_size=(25,25)):
    #### PARAMETERS ####
    sqrt_step = 2**sqrt_addr_w // sqrt_rom_depth
    sqrt_shift = math.ceil(math.log(sqrt_step, 2))
    ###################

    ii_sum = ii_s | frame_sum_tmp
    ii_sum_squared = ii_sum[0] * ii_sum[0]# | dreg | dreg

    sii_sum = sii_s | frame_sum_tmp
    sii_mult1 = sii_sum[0] * (frame_size[0]-1)# | dreg
    sii_mult2 = sii_mult1 * (frame_size[1]-1)# | dreg

    sub_s = sii_mult2 - ii_sum_squared # | dreg

    sqrt_addr = sub_s >> sqrt_shift | Uint[8]

    stddev_res = sqrt_addr | rom(data=sqrt_mem, dtype=Uint[w_sqrt])

    return stddev_res

if __name__ == "__main__":

    pass
