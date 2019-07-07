from pygears import gear
from pygears.typing import Queue, Uint

from .frame_sum import frame_sum

from pygears.lib.rom import rom
from pygears.lib import dreg as dreg_sp


@gear
def stddev(ii_s: Queue[Uint['w_ii'], 2], sii_s: Queue[Uint['w_sii'], 2], *,
           casc_hw):

    ii_sum = ii_s | frame_sum | dreg_sp
    ii_sum_squared = ii_sum[0] * ii_sum[0]

    sii_sum = sii_s | frame_sum | dreg_sp
    sii_mult1 = sii_sum[0] * (casc_hw.frame_size[0] - 1)
    sii_mult2 = sii_mult1 * (casc_hw.frame_size[1] - 1)

    sub_s = sii_mult2 - ii_sum_squared

    sqrt_addr = sub_s >> casc_hw.sqrt_shift | Uint[8]

    stddev_res = sqrt_addr | rom(
        data=casc_hw.sqrt_mem, dtype=Uint[casc_hw.w_sqrt])

    return stddev_res
