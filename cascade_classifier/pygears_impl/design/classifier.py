from pygears import gear, Intf
from pygears.typing import Array, Int, Uint, Queue, Tuple, Int, Unit

from pygears.common import cart_sync_with, ccat, neg
from pygears.common.mux import mux_valve
from pygears.common import lt, mux_valve, union_collapse
from pygears.common import rom, dreg
from pygears.common import local_rst

from pygears.cookbook import replicate

from .gears.accum import accum_on_eot
from .gears.accum import accum
from .gears.queue_ops import last_data


@gear
def weighted_sum(din: Queue[Tuple[Uint['w_ii'], Uint[1], Int['w_weight']], 1]):
    data_neg = din[0][0] | neg
    data = din[0][0] | data_neg.dtype

    signed_data = mux_valve(din[0][1], data_neg, data) | union_collapse
    signed_data = signed_data * din[0][2]
    weighted_data = ccat(signed_data, din[1])
    weighted_data = weighted_data | Queue[weighted_data.dtype[0], 1]

    summed_data = weighted_data | accum(add_num=4)
    summed_data = summed_data | Queue[Int[len(summed_data.dtype[0]
                                              )], 1] | last_data

    return summed_data


@gear
def get_leaf_num(din: Tuple[Int['w_sum'], Int['w_thr'], Uint['w_stddev']]):
    thresh_norm = din[2] * din[1]
    thresh_norm = thresh_norm | Int[len(thresh_norm.dtype)]

    dout = lt(ccat(din[0], thresh_norm))

    return dout


@gear
def leaf_vals(feat_addr: Queue[Uint['w_addr_feat'], 2], din: Uint[1], *,
              casc_hw):

    leaf0 = rom(
        feat_addr[0],
        data=casc_hw.leaf_vals_mem[0],
        dtype=Int[casc_hw.w_leaf_vals])
    leaf1 = rom(
        feat_addr[0],
        data=casc_hw.leaf_vals_mem[1],
        dtype=Int[casc_hw.w_leaf_vals])

    sync = ccat(din, leaf0, leaf1)
    dout = mux_valve(sync[0], sync[1], sync[2]) | union_collapse

    return dout


@gear
def get_stage_res(stage_addr: Queue[Uint['w_stage_addr'], 1],
                  din: Int['w_din'], *, casc_hw):
    stage_threshold = rom(
        stage_addr[0],
        data=casc_hw.stage_threshold_mem,
        dtype=Int[casc_hw.w_stage_threshold])

    sync = ccat(din, stage_threshold)

    dout = lt(sync[1], sync[0])

    return dout


@gear
def rect_sum(fb_data: Queue[Array[
        Tuple[Uint['w_ii'], Uint[1], Int['w_weight']]], 3],
             *,
             w_ii=b'w_ii',
             w_weight=b'w_weight'):

    rect_data_t = Intf(Tuple[Uint[w_ii], Uint[1], Int[w_weight]])
    rect = []
    for i in range(3):
        rect_tmp = ccat(
            fb_data[0][i],
            fb_data[1][0]) | Queue[rect_data_t.dtype, 1] | weighted_sum
        rect_tmp = rect_tmp * 4096
        rect.append(rect_tmp)
    rect_sum = rect[0] + rect[1] + rect[2]

    return rect_sum


@gear
def classifier(fb_data: Queue[Array[
        Tuple[Uint['w_ii'], Uint[1], Int['w_weight']]], 3],
               feat_addr: Queue[Uint['w_addr_feat'], 2],
               stage_addr: Queue[Uint['w_stage_addr'], 1],
               stddev: Uint['w_stddev'],
               rst_in: Unit,
               *,
               w_ii=b'w_ii',
               w_weight=b'w_weight',
               casc_hw):
    rst_in | local_rst

    stage_addr = stage_addr | dreg
    stddev = stddev | dreg
    # fb_data = fb_data | dreg
    feat_addr = feat_addr | dreg

    stddev_repl = replicate(ccat(5000, stddev))
    stddev_repl = stddev_repl[0]

    rect_sum_s = fb_data | rect_sum(w_ii=w_ii, w_weight=w_weight)
    feature_threshold = rom(
        feat_addr[0],
        data=casc_hw.feature_threshold_mem,
        dtype=Int[casc_hw.w_feature_threshold])

    stddev_repl = stddev_repl | cart_sync_with(
        ccat(rect_sum_s, 0) | Queue[rect_sum_s.dtype, 1])
    res = ccat(rect_sum_s, feature_threshold, stddev_repl)

    leaf_num = res | get_leaf_num
    leaf_val = leaf_vals(feat_addr=feat_addr, din=leaf_num, casc_hw=casc_hw)

    stage_eot = feat_addr[1][0]
    leaf_val = ccat(leaf_val, stage_eot) | Queue[leaf_val.dtype, 1]

    accum_stage = leaf_val | accum_on_eot(add_num=256)

    stage_res = accum_stage | get_stage_res(
        stage_addr=stage_addr, casc_hw=casc_hw)

    stage_res = ccat(stage_res, stage_addr[1]) | Queue[stage_res.dtype, 1]

    return stage_res
