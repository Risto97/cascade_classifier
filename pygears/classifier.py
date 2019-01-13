from pygears import gear, Intf
from pygears.typing import Array, Int, Uint, Queue, Tuple, Int


from pygears.cookbook import rng
from pygears.common import cart_sync_with, ccat
from pygears.common import lt, mux_valve, union_collapse

from roms import featureThreshold_mem, feature_addr, stageThreshold_mem
from roms import leafVal_mem
from roms import featureCount_mem
from gears.accum import accum_on_eot

import math

features_mem_t = Queue[Array[Uint['w_rect'], Uint[1], 3], 1]

w_rect_data = 20
w_weight_data = 3
w_leaf = 14



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
def leaf_vals(din: Uint[1], *, feature_num):
    rd_addr = feature_addr(feature_num=feature_num)

    leaf0 = leafVal_mem(rd_addr, w_data=w_leaf, val_num=0, depth=feature_num)
    leaf1 = leafVal_mem(rd_addr, w_data=w_leaf, val_num=1, depth=feature_num)

    sync = ccat(din, leaf0, leaf1)
    dout = mux_valve(sync[0], sync[1], sync[2]) | union_collapse

    return dout

@gear
def get_stage_res(din: Int['w_din'], *, stage_num):
    rd_addr = feature_addr(feature_num=stage_num)
    stage_threshold = stageThreshold_mem(rd_addr, w_data=11, depth=stage_num)

    sync = ccat(din, stage_threshold)

    dout = lt(sync[1], sync[0])

    return dout

@gear
def add_stage_eot(din: Int['w_leaf']):
    stage_cnt = feature_addr(feature_num=25)
    feature_num_in_stage = featureCount_mem(
        stage_cnt, w_data=8, depth=25)

    feature_cnt = ccat(0, feature_num_in_stage, 1) | rng
    feature_cnt = feature_cnt | cart_sync_with(feature_num_in_stage)

    dout = ccat(din, feature_cnt[1]) | Queue[din.dtype, 1]

    return dout

@gear
def classifier(fb_data: Queue[Array[Tuple[Uint['w_ii'], Uint[1], Int[
        'w_weight']]], 2],
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

    feat_thr_addr = feature_addr(feature_num=feature_num)
    feature_threshold = featureThreshold_mem(
        feat_thr_addr, depth=feature_num, w_data=13)

    stddev = stddev | cart_sync_with(
        ccat(rect_sum, 0) | Queue[rect_sum.dtype, 1])
    res = ccat(rect_sum, feature_threshold, stddev)

    leaf_num = res | get_leaf_num
    leaf_val = leaf_num | leaf_vals(feature_num=feature_num) | add_stage_eot

    accum_stage = leaf_val | accum_on_eot(add_num=256)

    stage_res = accum_stage | get_stage_res(stage_num=stage_num)

    return stage_res
