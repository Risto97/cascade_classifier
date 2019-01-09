from pygears import gear, Intf

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.typing import Tuple, Uint, Queue
from pygears.common import const, ccat, shred, cart, dreg, flatten
from pygears.cookbook.rng import rng
from pygears.cookbook import replicate

hop_t = Tuple[Uint[8], Uint[8]]

@gear
def hopper():
    cfg_hop_y = ccat(
        const(tout=Uint[1], val=0),
        const(tout=Uint[8], val=25),
        const(tout=Uint[1], val=1))
    hop_y = cfg_hop_y | rng

    cfg_hop_x = ccat(
        const(tout=Uint[1], val=0),
        const(tout=Uint[8], val=25),
        const(tout=Uint[1], val=1))
    hop_x = cfg_hop_x | rng

    dout = cart(hop_y, hop_x)

    return dout

@gear
def sweeper(cfg: Queue[Tuple[Uint[8], Uint[8]], 2]):

    cfg_sweep_y = ccat(
        # const(tout=Uint[8], val=0),
        cfg[0][0],
        const(tout=Uint[8], val=5),
        const(tout=Uint[1], val=1))
    sweep_y = cfg_sweep_y | rng

    cfg_sweep_x = ccat(
        # const(tout=Uint[8], val=0),
        cfg[0][1],
        const(tout=Uint[8], val=5),
        const(tout=Uint[1], val=1))
    sweep_x = cfg_sweep_x | rng

    dout = cart(sweep_y, sweep_x)

    return dout

@gear
def rd_addrgen():
    hop_out = hopper()

    sweep_out = hop_out | sweeper

    return sweep_out

rd_addrgen(sim_cls=SimVerilated) | shred

sim(outdir='build',
    check_activity=True,
    extens=[partial(PyGearsView, live=True, reload=True)])

# if __name__ == "__main__":

#     pass
