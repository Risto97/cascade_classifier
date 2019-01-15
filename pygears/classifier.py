from pygears import gear, Intf
from pygears.typing import Array, Int, Uint, Queue, Tuple, Int

from pygears.cookbook import rng
from pygears.common import cart_sync_with, ccat, fmap
from pygears.common import lt, mux_valve, union_collapse
from pygears.common import rom
from pygears.common import flatten

from addr_utils import rng_cnt
from gears.accum import accum_on_eot

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


@gear(svgen={'compile': True})
async def weighted_sum(
        din: Queue[Tuple[Uint['w_ii'], Uint[1], Int['w_weight']], 1],
        *,
        w_ii=b'w_ii',
        w_weight=b'w_weight',
        w_out=b'math.ceil(math.log(2**w_ii*4*2**w_weight, 2))'
) -> b'Int[w_out]':
    accum = Int[w_out](0)
    async for (data, eot) in din:
        if data[1] == 0:
            accum = accum - data[0]
        elif data[1] == 1:
            accum = accum + data[0]

        if eot == 1:
            yield data[2] * (accum + data[0])


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
    # rd_addr = rng_cnt(cnt_num=stage_num)
    stage_threshold = rom(
        stage_addr[0], data=stageThreshold_l, dtype=Int[w_stage_thresh])

    sync = ccat(din, stage_threshold)

    dout = lt(sync[1], sync[0])

    return dout


@gear
def classifier(fb_data: Queue[Array[Tuple[Uint['w_ii'], Uint[1], Int[
        'w_weight']]], 3],
               feat_addr: Queue[Uint['w_addr_feat'], 2],
               stage_addr: Queue[Uint['w_stage_addr'], 1],
               stddev: Uint['w_stddev'],
               *,
               w_ii=b'w_ii',
               w_weight=b'w_weight',
               feature_num,
               stage_num):

    rect_data_t = Intf(Tuple[Uint[w_ii], Uint[1], Int[w_weight]])
    rect = []
    for i in range(3):
        rect_tmp = ccat(
            fb_data[0][i],
            fb_data[1][0]) | Queue[rect_data_t.dtype, 1] | weighted_sum
        rect.append(rect_tmp)
    rect_sum = rect[0] + rect[1] + rect[2]

    feature_threshold = rom(
        feat_addr[0], data=featureThresholds_l, dtype=Int[w_feat_thresh])

    stddev = stddev | cart_sync_with(
        ccat(rect_sum, 0) | Queue[rect_sum.dtype, 1])
    res = ccat(rect_sum, feature_threshold, stddev)

    leaf_num = res | get_leaf_num
    leaf_val = leaf_vals(feat_addr=feat_addr, din=leaf_num)

    stage_eot = feat_addr[1][0]
    leaf_val = ccat(leaf_val, stage_eot) | Queue[leaf_val.dtype, 1]

    accum_stage = leaf_val | accum_on_eot(add_num=256)

    stage_res = accum_stage | get_stage_res(
        stage_addr=stage_addr, stage_num=stage_num)

    stage_res = ccat(stage_res, stage_addr[1]) | Queue[stage_res.dtype, 1]

    return stage_res
