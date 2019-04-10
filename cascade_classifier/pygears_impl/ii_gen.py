from pygears import gear, Intf
from pygears.typing import Queue, Uint, bitw
from gears.fifo2 import fifo2
from gears.accum import accum
from pygears.common import ccat, add, shred, flatten, dreg

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from gearbox import Gearbox
from functools import partial


@gear
def accum_wrap(din: Queue[Uint['w_din'], 2], *, add_num):
    accum_in = ccat(din[0], din[1][0]) | Queue[din.dtype[0], 1]
    accum_s = accum_in | accum(add_num=add_num)
    dout_s = ccat(accum_s, din[1]) | Queue[accum_s.dtype, 2] | flatten

    return dout_s


@gear
def ii_gen(din: Queue[Uint['w_din'], 2], *, frame_size=(25, 25)):
    fifo_depth = 2**bitw(frame_size[1])

    accum_s = din | dreg | accum_wrap(add_num=frame_size[0] * frame_size[1])

    fifo_out = Intf(accum_s.dtype[0])

    add_s = ccat(accum_s[0], fifo_out) | add

    fifo_in = ccat(add_s, accum_s[1]) | Queue[add_s.dtype, 2]

    fifo_out |= fifo_in | flatten | fifo2(
        depth=fifo_depth, preload=frame_size[1], regout=False)

    ii_s = fifo_in

    return ii_s | dreg


@gear
def sii_gen(din: Queue[Uint['w_din'], 2], *, frame_size=(25, 25)):
    din = din | dreg
    mult_s = din[0] * din[0]
    sii_in = ccat(mult_s, din[1]) | Queue[mult_s.dtype, 2]
    sii_s = sii_in | ii_gen(frame_size=frame_size)

    return sii_s


if __name__ == "__main__":
    din_t = Queue[Uint[8], 2]
    frame_size = (25, 25)
    seq = []
    for i in range(2):
        seq_y = []
        for y in range(frame_size[0]):
            seq_x = []
            for x in range(frame_size[1]):
                seq_x.append(x + 1)
            seq_y.append(seq_x)
        seq.append(seq_y)

    sii_gen(
        din=drv(t=din_t, seq=seq), frame_size=frame_size,
        sim_cls=SimVerilated) | shred
    ii_gen(
        din=drv(t=din_t, seq=seq), frame_size=frame_size,
        sim_cls=SimVerilated) | shred

    sim(outdir='./build',
        check_activity=True,
        extens=[partial(Gearbox, live=True, reload=True)])
