from pygears import gear

from pygears.sim import sim
from pygears.sim.modules.verilator import SimVerilated
from functools import partial

from pygears.typing import Tuple, Uint, Queue
from pygears.common import cart, cart, cart_sync_with, ccat, dreg, flatten, shred, union_collapse
from pygears.common import decoupler
from pygears.common.mux import mux_valve
from pygears.cookbook.rng import rng

import math

from cascade_classifier.python_utils.dumpVerilog import scaleParams
from cascade_classifier.python_utils.image import ImageClass
###### CHANGE  ##############
img_fn = '../../datasets/proba.pgm'
img_fn = '../../datasets/rtl7.jpg'
img = ImageClass()
img.loadImage(img_fn)
scale_params = scaleParams(img.img.shape, frame=(25, 25), factor=1 / 0.75)

w_boundary = max(
    math.ceil(math.log(max(scale_params['boundary_y']), 2)),
    math.ceil(math.log(max(scale_params['boundary_x']), 2))) + 1
w_ratio = max(
    math.ceil(math.log(max(scale_params['y_ratio']), 2)),
    math.ceil(math.log(max(scale_params['x_ratio']), 2)))

print(scale_params)
#############################


@gear
def scale_counter():
    cfg_scale_cnt = ccat(0, scale_params['scaleNum'], 1)
    scale_cnt = cfg_scale_cnt | rng

    return scale_cnt


@gear
def boundaries(scale_counter: Queue[Uint['w_scale'], 1]):
    bound_y_param = []
    for val in scale_params['boundary_y']:
        bound_y_param.append(Uint[w_boundary](val + 1))
    bound_x_param = []
    for val in scale_params['boundary_x']:
        bound_x_param.append(Uint[w_boundary](val + 1))

    boundary_y = mux_valve(scale_counter[0], *bound_y_param) | union_collapse
    boundary_x = mux_valve(scale_counter[0], *bound_x_param) | union_collapse

    boundary = ccat(boundary_y, boundary_x)
    boundary = ccat(boundary, scale_counter[1]) | Queue[boundary.dtype, 1]

    return boundary


@gear
def scale_ratio(scale_counter: Queue[Uint['w_scale'], 1]):
    y_ratio_param = []
    for val in scale_params['y_ratio']:
        y_ratio_param.append(Uint[w_ratio](val))

    x_ratio_param = []
    for val in scale_params['x_ratio']:
        x_ratio_param.append(Uint[w_ratio](val))

    y_ratio = mux_valve(scale_counter[0], *y_ratio_param) | union_collapse
    x_ratio = mux_valve(scale_counter[0], *x_ratio_param) | union_collapse

    ratio = ccat(y_ratio, x_ratio)
    ratio = ccat(ratio, scale_counter[1]) | Queue[ratio.dtype, 1]

    return ratio


@gear
def hopper(hopper_cfg: Queue[Tuple[Uint['w_bound', Uint['w_bound']]], 1]):
    cfg_hop_y = ccat(0, hopper_cfg[0][0], 1)
    hop_y = cfg_hop_y | rng

    cfg_hop_x = ccat(0, hopper_cfg[0][1], 1)
    cfg_hop_x = cfg_hop_x | cart_sync_with(hop_y)
    hop_x = cfg_hop_x | rng

    dout = cart(hop_y, hop_x)

    return dout


@gear
def sweeper(hop: Queue[Tuple[Uint['w_y'], Uint['w_x']], 2],
            scale_ratio: Queue[Tuple[Uint['w_ratio'], Uint['w_ratio']], 1],
            *,
            frame_size=(25, 25)):

    scale_ratio = scale_ratio | cart_sync_with(hop)

    cfg_sweep_y = ccat(hop[0][0], frame_size[0], 1)
    sweep_y = cfg_sweep_y | rng(cnt_steps=True)
    ratio_y = scale_ratio | cart_sync_with(sweep_y)
    scaled_y = ((sweep_y[0] * ratio_y[0][0]) >> 16) | sweep_y.dtype[0]
    sweep_y = ccat(scaled_y, sweep_y[1]) | Queue[sweep_y.dtype[0], 1]

    cfg_sweep_x = ccat(hop[0][1], frame_size[1], 1) \
        | cart_sync_with(sweep_y)
    sweep_x = cfg_sweep_x | rng(cnt_steps=True)
    ratio_x = ratio_y | cart_sync_with(sweep_x)
    scaled_x = ((sweep_x[0] * ratio_x[0][1]) >> 16) | sweep_x.dtype[0]
    sweep_x = ccat(scaled_x, sweep_x[1]) | Queue[sweep_x.dtype[0], 1]

    dout = cart(sweep_y, sweep_x)
    dout = cart(hop | flatten, dout)

    dout_eot = ccat(dout[1], ratio_x[1]) | Uint[4]

    dout = ccat(dout[0][1], dout_eot) | Queue[dout.dtype[0][1], 4]

    return dout | decoupler


@gear
def addr_trans(din: Queue[Tuple[Uint['w_y'], Uint['w_x']], 4],
               *,
               img_size=(240, 320)):

    ram_size = img_size[0] * img_size[1]
    w_addr = math.ceil(math.log(ram_size, 2))

    addr_abs = din[0][1] + din[0][0] * img_size[1] | Uint[w_addr]

    return ccat(addr_abs, din[1]) | Queue[addr_abs.dtype, 4]


@gear
def rd_addrgen(*, img_size=(240,320), frame_size=(25, 25)):
    scale = scale_counter()
    ratio = scale_ratio(scale)
    boundary = boundaries(scale)

    hop_out = boundary | hopper | decoupler
    sweep_out = hop_out | sweeper(
        scale_ratio=ratio, frame_size=frame_size) | dreg
    scaled_addr = cart(scale, hop_out) | flatten(lvl=2)

    sweep_linear = sweep_out | addr_trans(img_size=img_size)

    return sweep_linear, scaled_addr

# if __name__ == "__main__":
#     frame_size = (25, 25)
#     sweep_addr, scaled_addr = rd_addrgen(
#         frame_size=frame_size, sim_cls=SimVerilated)

#     sweep_addr | shred
#     scaled_addr | shred

#     sim(outdir='build',
#         check_activity=True,
#         extens=[partial(Gearbox, live=True, reload=True)])