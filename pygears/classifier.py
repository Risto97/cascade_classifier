from pygears import gear, Intf
from pygears.typing import Array, Int, Uint, Queue, Tuple, Int

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial
from pygears.sim.extens.vcd import VCD

from pygears.cookbook import rng
from pygears.common import ccat, dreg, shred, czip, zip_sync, cart, cart_sync, cart_sync_with
from pygears.common import lt, mux, union_collapse, mux_valve

from features import features
from roms import featureThreshold_mem, feature_addr
from roms import leafVal_mem

import math

features_mem_t = Queue[Array[Uint['w_rect'], Uint[1], 3], 1]

w_rect_data = 20
w_weight_data = 3
w_leaf = 14

import math


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

    leaf0 = leafVal_mem(rd_addr,
                        w_data=w_leaf,
                        val_num=0,
                        depth=feature_num)
    leaf1 = leafVal_mem(rd_addr,
                        w_data=w_leaf,
                        val_num=1,
                        depth=feature_num)

    sync = ccat(din, leaf0, leaf1)
    dout = mux_valve(sync[0], sync[1], sync[2]) | union_collapse

    # dout = temp
    return dout


@gear
def classifier(fb_data: Queue[Array[Tuple[Uint['w_ii'], Uint[1], Int[
        'w_weight']]], 2],
               stddev: Uint['w_stddev'],
               *,
               w_ii=b'w_ii',
               w_weight=b'w_weight',
               feature_num):

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

    leaf_val = leaf_num #| leaf_vals(feature_num=feature_num)

    return leaf_val


if __name__ == "__main__":
    seq = []

    for n in range(50):
        seq_r = []
        for r in range(4):
            # if r == 0 or r == 3:
            #     sign = 1
            # else:
            #     sign = 0
            # weight = -3
            # tmp = (50 + (r + 1) * (n + 5), sign, weight)
            if r == 0:
                tmp = (1761, 1, -3)
            elif r == 1:
                tmp = (6589, 0, -3)
            elif r == 2:
                tmp = (6142, 0, -3)
            elif r == 3:
                tmp = (27812, 1, -3)
            seq_r.append(tmp)
        seq.append(seq_r)

    weighted_sum(
        din=drv(t=Queue[Tuple[Uint[19], Uint[1], Int[3]], 1], seq=seq),
        sim_cls=SimVerilated) | shred
    # weighted_sum(din=drv(t=Queue[Uint[19], 1], seq=seq), sim_cls=SimVerilated) | shred

    sim(outdir='build', extens=[VCD])

    # sim(outdir='build',
    #     check_activity=True,
    #     extens=[partial(PyGearsView, live=True, reload=True)])

    pass
