from pygears import gear, Intf
from pygears.typing import Queue, Uint
from gears.fifo2 import fifo2
from gears.accum import accum
from pygears.common import ccat, add, shred

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

din_t = Queue[Uint[8], 2]


@gear
def accum_wrap(din: din_t):
    accum_in = ccat(din[0], din[1][0]) | Queue[din.dtype[0], 1]
    accum_s = accum_in | accum
    eot_s = din[1][1] * din[1][0]
    dout_s = ccat(accum_s, eot_s) | Queue[accum_s.dtype, 1]

    return dout_s


@gear
def ii_gen(din: din_t, *, frame_size=(25, 25)):
    accum_s = din | accum_wrap

    fifo_out = Intf(accum_s.dtype[0])

    add_s = ccat(accum_s[0], fifo_out) | add

    fifo_in = ccat(add_s, accum_s[1])

    fifo_out |= fifo_in | fifo2(depth=32, preload=frame_size[1], regout=False)

    dout_s = fifo_in

    return dout_s


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

ii_gen(
    din=drv(t=din_t, seq=seq), frame_size=frame_size,
    sim_cls=SimVerilated) | shred

sim(outdir='./build',
    check_activity=True,
    extens=[partial(PyGearsView, live=True, reload=True)])
