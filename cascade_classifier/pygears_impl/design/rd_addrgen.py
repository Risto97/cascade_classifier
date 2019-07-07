from pygears import gear

from pygears.typing import Tuple, Uint, Queue
from pygears.lib import cart, cart, cart_sync_with, ccat, dreg, flatten, union_collapse
from pygears.lib import decoupler as decoupler_sp
from pygears.lib import dreg as dreg_sp
from pygears.lib.mux import mux_valve
from pygears.lib.rng import rng

import math


@gear
def scale_counter(*, scale_num):
    cfg_scale_cnt = ccat(0, scale_num, 1)
    scale_cnt = cfg_scale_cnt | rng

    return scale_cnt


@gear
def boundaries(scale_counter: Queue[Uint['w_scale'], 1], *, casc_hw):
    bound_y_param = []
    for val in casc_hw.boundary_y:
        bound_y_param.append(Uint[casc_hw.w_boundary](val + 1))
    bound_x_param = []
    for val in casc_hw.boundary_x:
        bound_x_param.append(Uint[casc_hw.w_boundary](val + 1))

    boundary_y = mux_valve(scale_counter[0], *bound_y_param) | union_collapse
    boundary_x = mux_valve(scale_counter[0], *bound_x_param) | union_collapse

    boundary = ccat(boundary_y, boundary_x)
    boundary = ccat(boundary, scale_counter[1]) | Queue[boundary.dtype, 1]

    return boundary


@gear
def scale_ratio(scale_counter: Queue[Uint['w_scale'], 1], *, casc_hw):
    y_ratio_param = []
    for val in casc_hw.y_ratio:
        y_ratio_param.append(Uint[casc_hw.w_ratio](val))

    x_ratio_param = []
    for val in casc_hw.x_ratio:
        x_ratio_param.append(Uint[casc_hw.w_ratio](val))

    y_ratio = mux_valve(scale_counter[0], *y_ratio_param) | union_collapse
    x_ratio = mux_valve(scale_counter[0], *x_ratio_param) | union_collapse

    ratio = ccat(y_ratio, x_ratio)
    ratio = ccat(ratio, scale_counter[1]) | Queue[ratio.dtype, 1]

    return ratio


@gear
def hopper(hopper_cfg):
    cfg_hop_y = ccat(0, hopper_cfg[0][0], 1)
    hop_y = cfg_hop_y | rng

    cfg_hop_x = ccat(0, hopper_cfg[0][1], 1)
    cfg_hop_x = cfg_hop_x | cart_sync_with(hop_y)
    hop_x = cfg_hop_x | rng

    dout = cart(hop_y, hop_x)

    return dout


@gear
def sweeper(hop: Queue[Tuple[Uint['w_y'], Uint['w_x']], 2],
            scale_ratio: Queue[Tuple[Uint['w_ratio'], Uint['w_ratio']], 1], *,
            frame_size):

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
    scaled_x = ((sweep_x[0] * ratio_x[0][1]) >> 16) | sweep_x.dtype[0] | decoupler_sp
    sweep_x = ccat(scaled_x, sweep_x[1] | decoupler_sp) | Queue[sweep_x.dtype[0], 1]

    dout = cart(sweep_y | decoupler_sp, sweep_x )
    dout = cart(hop | flatten, dout)

    dout_eot = ccat(dout[1], ratio_x[1] | decoupler_sp) | Uint[4]

    dout = ccat(dout[0][1], dout_eot) | Queue[dout.dtype[0][1], 4]

    return dout | decoupler_sp


@gear
def addr_trans(din: Queue[Tuple[Uint['w_y'], Uint['w_x']], 4], *, img_size):

    ram_size = img_size[0] * img_size[1]
    w_addr = math.ceil(math.log(ram_size, 2))

    addr_abs = din[0][1] + din[0][0] * img_size[1] | Uint[w_addr]

    return ccat(addr_abs, din[1]) | Queue[addr_abs.dtype, 4]


@gear
def rd_addrgen(*, casc_hw):
    # import pdb; pdb.set_trace();
    scale = scale_counter(scale_num=casc_hw.scale_num)
    ratio = scale_ratio(scale, casc_hw=casc_hw)
    boundary = boundaries(scale, casc_hw=casc_hw)

    hop_out = boundary | hopper | decoupler_sp
    sweep_out = hop_out | sweeper(
        scale_ratio=ratio, frame_size=casc_hw.frame_size)
    scaled_addr = cart(scale, hop_out) | flatten(lvl=2)

    sweep_linear = sweep_out | addr_trans(img_size=casc_hw.img_size)

    return sweep_linear, scaled_addr
