from pygears import gear
from pygears.typing import Uint

from pygears.sim import sim
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from features_rom import rects_mem
from pygears.cookbook.rng import rng

from pygears.common import ccat, czip, shred

import math

@gear
def features(*, feature_num, feature_size, w_rect_data, w_weight_data):
    w_addr = math.ceil(math.log(feature_num, 2))
    cfg_rng = ccat(0, Uint[w_addr](feature_num), 1)
    rd_addr = cfg_rng | rng | Uint[w_addr]

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

    return czip(*features_data)



if __name__ == "__main__":
    feature_num = 2913
    w_rect_data = 20
    w_weight_data = 3
    feature_size = (25, 25)
    seq = list(range(feature_num))
    features(
        feature_num=feature_num,
        w_rect_data=w_rect_data,
        w_weight_data=w_weight_data,
        feature_size=feature_size,
        sim_cls=SimVerilated) | shred


    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
