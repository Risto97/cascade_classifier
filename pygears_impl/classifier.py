from pygears import gear, Intf
from pygears.typing import Array, Int, Uint, Queue, Tuple, Int, Unit

from pygears.cookbook import rng
from pygears.common import cart_sync_with, ccat, fmap, neg, shred
from pygears.common.mux import mux_valve
from pygears.common import lt, mux_valve, union_collapse
from pygears.common import rom, dreg
from pygears.common import flatten
from pygears.common import local_rst

from pygears.cookbook import replicate

from addr_utils import rng_cnt
from gears.accum import accum_on_eot
from gears.accum import accum
from gears.queue_ops import last_data

import math

features_mem_t = Queue[Array[Uint['w_rect'], Uint[1], 3], 1]

w_rect_data = 20
w_weight_data = 3
w_leaf = 14

## change this ##
from cascade import create_cascade
cascade_model = create_cascade("../models/haarcascade_frontalface_default.xml")

featureThresholds_ret = cascade_model.getFeatureThresholds()
featureThresholds_l = featureThresholds_ret[0]
w_feat_thresh = featureThresholds_ret[1]

leafVal0_l, w_leafVal0 = cascade_model.getLeafVals(0)
leafVal1_l, w_leafVal1 = cascade_model.getLeafVals(1)
w_leafVal = max(w_leafVal0, w_leafVal1)

stageThreshold_l, w_stage_thresh = cascade_model.getStageThreshold()
#################


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
def leaf_vals(feat_addr: Queue[Uint['w_addr_feat'], 2], din: Uint[1]):

    leaf0 = rom(feat_addr[0], data=leafVal0_l, dtype=Int[w_leafVal])
    leaf1 = rom(feat_addr[0], data=leafVal1_l, dtype=Int[w_leafVal])

    sync = ccat(din, leaf0, leaf1)
    dout = mux_valve(sync[0], sync[1], sync[2]) | union_collapse

    return dout


@gear
def get_stage_res(stage_addr: Queue[Uint['w_stage_addr'], 1],
                  din: Int['w_din'], *, stage_num):
    stage_threshold = rom(
        stage_addr[0], data=stageThreshold_l, dtype=Int[w_stage_thresh])

    sync = ccat(din, stage_threshold)

    dout = lt(sync[1], sync[0])

    return dout


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
               feature_num,
               stage_num):
    rst_in | local_rst

    stage_addr = stage_addr | dreg
    stddev = stddev | dreg

    stddev_repl = replicate(ccat(2913, stddev))
    stddev_repl = stddev_repl[0]
    rect_data_t = Intf(Tuple[Uint[w_ii], Uint[1], Int[w_weight]])
    rect = []
    for i in range(3):
        rect_tmp = ccat(
            fb_data[0][i],
            fb_data[1][0]) | Queue[rect_data_t.dtype, 1] | weighted_sum
        rect_tmp = rect_tmp * 4096
        rect.append(rect_tmp)
    rect_sum = rect[0] + rect[1] + rect[2]

    feature_threshold = rom(
        feat_addr[0], data=featureThresholds_l, dtype=Int[w_feat_thresh])

    stddev_repl = stddev_repl | cart_sync_with(
        ccat(rect_sum, 0) | Queue[rect_sum.dtype, 1])
    res = ccat(rect_sum, feature_threshold, stddev_repl)

    leaf_num = res | get_leaf_num | dreg
    leaf_val = leaf_vals(feat_addr=feat_addr, din=leaf_num)

    stage_eot = feat_addr[1][0] | dreg
    leaf_val = ccat(leaf_val, stage_eot) | Queue[leaf_val.dtype, 1]

    accum_stage = leaf_val | accum_on_eot(add_num=256)

    stage_res = accum_stage | get_stage_res(
        stage_addr=stage_addr, stage_num=stage_num)

    stage_res = ccat(stage_res | dreg,
                     stage_addr[1]) | Queue[stage_res.dtype, 1]

    return stage_res


if __name__ == "__main__":
    from pygears.sim import sim
    from pygears.sim.modules import drv
    from pygears.sim.modules.verilator import SimVerilated
    from gearbox import Gearbox
    from functools import partial

    din_t = Queue[Tuple[Uint[19], Uint[1], Int[2]], 1]

    seq = []
    seq.append((805, 1, -1))
    seq.append((36407, 0, -1))
    seq.append((1273, 0, -1))
    seq.append((45228, 1, -1))

    seq = [seq] * 3

    weighted_sum(din=drv(t=din_t, seq=seq), sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(Gearbox, live=True, reload=True)])
