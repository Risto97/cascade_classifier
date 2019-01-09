from pygears import gear

from pygears.sim import sim
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.typing import Tuple, Uint, Queue
from pygears.common import cart, cart_sync_with, ccat, shred
from pygears.cookbook.rng import rng

import math

@gear
def hopper(*, img_size=(240, 320), frame_size=(25, 25)):
    cfg_hop_y = ccat(0, img_size[0] - frame_size[0], 1)
    hop_y = cfg_hop_y | rng

    cfg_hop_x = ccat(0, img_size[1] - frame_size[1], 1)
    hop_x = cfg_hop_x | rng

    dout = cart(hop_y, hop_x)

    return dout


@gear
def sweeper(cfg: Queue[Tuple[Uint['w_y'], Uint['w_x']], 2],
            *,
            frame_size=(25, 25)):

    cfg_sweep_y = ccat(cfg[0][0], frame_size[0], 1)
    sweep_y = cfg_sweep_y | rng(cnt_steps=True, cnt_one_more=True)

    cfg_sweep_x = ccat(cfg[0][1], frame_size[1], 1) \
        | cart_sync_with(sweep_y)

    sweep_x = cfg_sweep_x | rng(cnt_steps=True, cnt_one_more=True)

    dout = cart(sweep_y, sweep_x)

    return dout

@gear
def addr_trans(din: Queue[Tuple[Uint['w_y'], Uint['w_x']], 2], *, img_size=(240,320)):

    ram_size = img_size[0] * img_size[1]
    w_addr = math.ceil(math.log(ram_size, 2))

    addr_abs = din[0][0] + din[0][1] * img_size[1] | Uint[w_addr]

    return ccat(addr_abs, din[1]) | Queue[addr_abs.dtype, 2]


@gear
def rd_addrgen(*, img_size=(240, 320), frame_size=(25, 25)):
    hop_out = hopper(img_size=img_size, frame_size=frame_size)

    sweep_out = hop_out | sweeper(frame_size=frame_size)

    return sweep_out


if __name__ == "__main__":
    img_size = (25, 25)
    frame_size = (5, 5)
    rd_addrgen(
        img_size=img_size, frame_size=frame_size, sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])


#     pass
