from pygears import gear, Intf
from pygears.typing import Uint, Queue, Array, Tuple, Int

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from roms import rects_mem
from pygears.cookbook.rng import rng
from pygears.cookbook.priority_mux import priority_mux
from pygears.common import union_collapse, cart_sync_with, quenvelope

from pygears.common import ccat, czip, shred, zip_sync, fmap, cart

import math


rd_addr_t = Queue[Uint['w_addr'], 2]
@gear
def features(rd_addr: Queue[Uint['w_addr'], 2], *, feature_num, feature_size,
             w_rect_data, w_weight_data):
    w_rect = w_rect_data//2
    features_data = []
    for i in range(3):
        feature = rects_mem(
            rd_addr_if=rd_addr[0],
            inst_num=i,
            feature_num=feature_num,
            w_rect_data=w_rect_data,
            w_weight_data=w_weight_data,
            feature_size=feature_size)
        features_data.append(feature)

    feature_data_t = Intf(Tuple[Uint[w_rect], Uint[1], Int[w_weight_data]])
    features_zip = czip(*features_data) | Queue[Array[feature_data_t.dtype, 3], 1]

    sync = cart( rd_addr[1] , features_zip)

    dout_eot = ccat(sync[1], sync[0][0]) | Uint[3]
    dout = ccat(sync[0][1], dout_eot) | Queue[Array[feature_data_t.dtype, 3], 3]
    return dout


if __name__ == "__main__":
    feature_num = 2913
    w_rect_data = 20
    w_weight_data = 3
    feature_size = (25, 25)
    w_addr = math.ceil(math.log(feature_num, 2))

    rd_seq = [[list(range(9)), list(range(9,25)), list(range(25,32)), list(range(32, 55)), list(range(55,100))]]

    features(
        rd_addr=drv(t=rd_addr_t[w_addr], seq=rd_seq),
        feature_num=feature_num,
        w_rect_data=w_rect_data,
        w_weight_data=w_weight_data,
        feature_size=feature_size,
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
