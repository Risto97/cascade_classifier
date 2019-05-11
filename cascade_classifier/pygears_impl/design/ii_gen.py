from pygears import gear, Intf
from pygears.typing import Queue, Uint, bitw
from cascade_classifier.pygears_impl.design.gears.fifo2 import fifo2
from cascade_classifier.pygears_impl.design.gears.accum import accum
from pygears.common import add, ccat, dreg, flatten


@gear
def accum_wrap(din: Queue[Uint['w_din'], 2], *, add_num):
    accum_in = ccat(din[0], din[1][0]) | Queue[din.dtype[0], 1]
    accum_s = accum_in | accum(add_num=add_num)
    dout_s = ccat(accum_s, din[1]) | Queue[accum_s.dtype, 2] | flatten

    return dout_s


@gear
def ii_gen(din: Queue[Uint['w_din'], 2], *, frame_size=(25, 25)):
    fifo_depth = 2**bitw(frame_size[1])

    accum_s = din | accum_wrap(add_num=frame_size[0] * frame_size[1])

    fifo_out = Intf(accum_s.dtype[0])

    add_s = ccat(accum_s[0], fifo_out) | add

    fifo_in = ccat(add_s, accum_s[1]) | Queue[add_s.dtype, 2]

    fifo_out |= fifo_in | flatten | fifo2(
        depth=fifo_depth, preload=frame_size[1], regout=False)

    ii_s = fifo_in

    return ii_s


@gear
def sii_gen(din: Queue[Uint['w_din'], 2], *, frame_size=(25, 25)):
    mult_s = din[0] * din[0]
    sii_in = ccat(mult_s, din[1]) | Queue[mult_s.dtype, 2]
    sii_s = sii_in | ii_gen(frame_size=frame_size)

    return sii_s
