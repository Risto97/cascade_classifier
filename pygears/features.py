from pygears import gear
from pygears.typing import Uint, Queue, Array, Tuple, Int

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from roms import rects_mem
from pygears.cookbook.rng import rng

from pygears.common import ccat, czip, shred, zip_sync, fmap

import math


@gear
def features(rd_addr: Uint['w_addr'], *, feature_num, feature_size,
             w_rect_data, w_weight_data):
    features_data = []
    for i in range(3):
        feature = rects_mem(
            rd_addr_if=rd_addr,
            inst_num=i,
            feature_num=feature_num,
            w_rect_data=w_rect_data,
            w_weight_data=w_weight_data,
            feature_size=feature_size)
        features_data.append(feature)

    features_zip = czip(*features_data)

    # features_zip_arr = features_zip[0] | Array[Tuple[Tuple[Uint[w_rect_data//2], Uint[1], Int[w_weight_data]]], 3]
    features_zip_arr = features_zip[0] | Array[Tuple[Uint[w_rect_data//2], Uint[1], Int[w_weight_data]], 3]
    features_zip_arr = ccat(features_zip_arr, features_zip[1]) | Queue[features_zip_arr.dtype, 2]

    return features_zip_arr


if __name__ == "__main__":
    feature_num = 2913
    w_rect_data = 20
    w_weight_data = 3
    feature_size = (25, 25)
    w_addr = math.ceil(math.log(feature_num, 2))

    rd_seq = list(range(feature_num))
    features(
        rd_addr=drv(t=Uint[w_addr], seq=rd_seq),
        feature_num=feature_num,
        w_rect_data=w_rect_data,
        w_weight_data=w_weight_data,
        feature_size=feature_size,
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
