from pygears import gear
from pygears.typing import Int, Queue, Uint, Tuple

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from frame_sum import frame_sum_tmp

from pygears.common import czip, ccat, dreg, zip_sync, decoupler

from image import loadImage

# img = loadImage("../datasets/rtl.pgm")
# img_size = img.shape
# frame_size = (25, 25)
# print(img[0:5, 0:5])

@gear
def stddev(ii_s: Queue[Uint['w_ii'], 2], sii_s: Queue[Uint['w_sii'], 2], *, frame_size=(25,25)):
# def stddev(din: Queue[Tuple[Uint['w_ii'], Uint['w_sii']],2], *, frame_size=(25,25)):
# def stddev(din: Tuple[Uint['w_ii'], Uint['w_sii']], *, frame_size=(25,25)):
    # din_s = zip_sync(ii_s, sii_s)

    # print(din_s[0].dtype)
    # print(din_s[1].dtype)

    # ii_s2 = ccat(din_s[0][0], din_s[1]) | Queue[din_s[0][0].dtype, 2]
    # sii_s2 = ccat(din_s[0][1], din_s[1]) | Queue[din_s[0][1].dtype, 2]
    ii_sum = ii_s | frame_sum_tmp


    ii_sum_squared = ii_sum[0] * ii_sum[0]# | dreg | dreg

    sii_sum = sii_s | frame_sum_tmp
    # # print("sii_sum", sii_sum.dtype)
    sii_mult1 = sii_sum[0] * (frame_size[0]-1)# | dreg
    sii_mult2 = sii_mult1 * (frame_size[1]-1)# | dreg

    sqrt_addr = sii_mult2 - ii_sum_squared # | dreg

    # return ccat(ii_sum, sii_sum)
    return sqrt_addr
    # dout_ii = ii_s2 | dreg
    # dout_sii = sii_s2 | dreg
    # return ccat(ii_s2, sii_s2)
    # return ccat(dout_ii, dout_sii)


if __name__ == "__main__":

    pass
