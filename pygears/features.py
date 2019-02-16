from pygears import gear, Intf
from pygears.typing import Uint, Queue, Array, Tuple, Int, Unit

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from gearbox import Gearbox
from functools import partial

from rects_data import rects_mem
from pygears.cookbook.rng import rng
from pygears.cookbook.priority_mux import priority_mux
from pygears.common import union_collapse, cart_sync_with, quenvelope

from pygears.common import ccat, czip, shred, zip_sync, fmap, cart, dreg

from gears.czip_alt import czip_alt3

from pygears.common import local_rst

import math


rd_addr_t = Queue[Uint['w_addr'], 2]
@gear
def features(rd_addr: Queue[Uint['w_addr'], 2],
             rst_in: Unit,
             *, feature_num, feature_size,
             w_rect_data, w_weight_data):
    rst_in | local_rst
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
    features_zip = czip_alt3(*features_data) | Queue[Array[feature_data_t.dtype, 3], 1]

    sync = cart( rd_addr[1] | dreg, features_zip)

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
        extens=[partial(Gearbox, live=True, reload=True)])
