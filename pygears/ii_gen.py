from pygears import gear, Intf
from pygears.typing import Queue, Uint, Tuple, Int
from pygears.svgen import svgen
from pygears.util.print_hier import print_hier

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears.common import dreg, add, const, decoupler, shred, union_collapse
from gears.fifo2 import fifo2
from gears.accum import accum

from pygears.sim.extens.vcd import VCD
from pygears.cookbook import priority_mux

from pygears_view import main
from functools import partial
from pygears_view import PyGearsView
from pygears import bind


@gear
def fill_void(din, fill):
    return priority_mux(din, fill) \
        | union_collapse


din_t = Queue[Uint[8]]


@gear
def ii_gen(din: din_t, *, frame_size=(25, 25)):
    accum_s = din | accum

    dout = Intf(accum_s.dtype[0])
    fifo_out = dout | fifo2(
        depth=32, preload=frame_size[1]-1,
        regout=True) | fill_void(fill=accum_s.dtype[0](0)) | decoupler

    dout |= (accum_s[0] + fifo_out) | dout.dtype

    return dout


frame_size = (25, 25)
seq = []
for i in range(frame_size[0]):
    seq.append(list(range(1, frame_size[1] + 1)))

ii_gen(din=drv(t=din_t, seq=seq), frame_size=frame_size, sim_cls=SimVerilated)

sim(
    outdir='./build',
    # extens=[VCD])
    check_activity=True,
    extens=[partial(PyGearsView, live=True, reload=True)])

print()
print_hier()
print()
