from pygears import gear, Intf
from pygears.typing import Queue, Uint, Tuple, Int
from pygears.svgen import svgen
from pygears.util.print_hier import print_hier

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears.common import dreg, const, decoupler, shred, union_collapse

# from pygears.common import add

from gears.fifo2 import fifo2
from gears.accum import accum
from gears.add2 import add2

from pygears.sim.extens.vcd import VCD
from pygears.cookbook import priority_mux

from pygears_view import main
from functools import partial
from pygears_view import PyGearsView
from pygears import bind

from pygears.common import ccat, czip, cart, fmap

@gear
def fill_void(din, fill):
    return priority_mux(din, fill) \
        | union_collapse

din_t = Queue[Uint[8], 2]

@gear
def ii_gen(din: din_t, *, frame_size=(25, 25)):
    accum_s = din | accum

    fifo_in = Intf(Queue[Uint[19], 1])
    fifo_out = fifo_in | fifo2(
        depth=32, preload=frame_size[1],
        regout=False)

    fifo_in |= add2(ccat(accum_s, fifo_out[0] | Uint[18])) | Queue[Uint[19], 1]

    return fifo_in | Uint[18]


frame_size = (5, 5)
seq = []
for i in range(2):
    seq_y = []
    for y in range(frame_size[0]):
        seq_x = []
        for x in range(frame_size[1]):
            seq_x.append(x+1)
        seq_y.append(seq_x)
    seq.append(seq_y)
print(seq)

        # seq.append([list(range(1, frame_size[1] + 1))])

ii_gen(din=drv(t=din_t, seq=seq), frame_size=frame_size, sim_cls=SimVerilated) | shred

sim(
    outdir='./build',
    # extens=[VCD])
    check_activity=True,
    extens=[partial(PyGearsView, live=True, reload=True)])

print()
print_hier()
print()
