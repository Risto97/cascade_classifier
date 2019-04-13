from pygears import gear, Intf
from pygears.typing import Array, Int, Uint, Queue, Tuple

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from functools import partial

from pygears.common import ccat, shred, dreg, decoupler, fifo, zip_sync, cart
from pygears.common.serialize import serialize, active_serialize
from pygears.common import rom
from pygears.cookbook import rng

TRdDin = Uint['w_addr']
outnames = ['rd_data_if']

## change this ##
from cascade_classifier.python_utils.cascade import CascadeClass
xml_file = r"../xml_models/haarcascade_frontalface_default.xml"
cascade_model = CascadeClass(xml_file)

rect_coords_l = []
rect_weights_l = []
for r in range(3):
    rect_coords_tmp, w_rect_coords = cascade_model.getRectCoords(r)
    rect_weights_tmp, w_weights = cascade_model.getRectWeights(r)
    rect_coords_l.append(rect_coords_tmp)
    rect_weights_l.append(rect_weights_tmp)

#################

import math
@gear
def feature_addr(*, feature_num):
    w_feat_addr = math.ceil(math.log(feature_num, 2))
    cfg_rng = ccat(0, Uint[w_feat_addr](feature_num), 1)
    rd_addr_feat = cfg_rng | rng | Uint[w_feat_addr]

    return rd_addr_feat

@gear(svgen={'compile': True})
def calc_rect_coords(
        din: Tuple[Uint['w_meas'], Uint['w_meas'], Uint['w_rect']],
        *,
        w_meas=b'w_meas',
        w_rect=b'w_rect',
        feature_size):
    assert (w_meas * 2 == w_rect)  # Not really...

    width = din[1]
    height = din[0]
    A = din[2]
    B = (A + width) | Uint[w_rect] | dreg
    tmp = height * feature_size[1] | dreg
    D = (B + tmp) | Uint[w_rect]

    C = (D - width) | Uint[w_rect]

    sign = ccat(1, 0, 0, 1) | Array[Uint[1], 4] | serialize
    rect_coord = ccat(A | dreg, B, C, D) | Array[Uint[w_rect], 4]
    rect_coord = ccat(rect_coord, 4) | Tuple[Array[Uint[w_rect], 4], Uint[3]] | active_serialize

    return ccat(rect_coord[0], sign, rect_coord[1]) | \
        Queue[Tuple[Uint[w_rect], Uint[1]], 1]

@gear
def rects_mem(rd_addr_if: TRdDin, *, inst_num, w_rect_data, w_weight_data,
              feature_num, feature_size):
    w_rect = w_rect_data // 2
    rect_tuple = rom(
        rd_addr_if,
        data=rect_coords_l[inst_num],
        dtype=Uint[w_rect_coords]) | \
        Tuple[Uint[w_rect/2], Uint[w_rect/2], Uint[w_rect]]

    rect_coords = rect_tuple | calc_rect_coords(feature_size=feature_size)

    weight = rom(
        rd_addr_if,
        data=rect_weights_l[inst_num],
        dtype=Int[w_weights])

    data_t = Intf(Tuple[Uint[w_rect], Uint[1], Int[w_weight_data]])

    cart_sync = cart(rect_coords, weight)
    tuple_rect = ccat(cart_sync[0][0], cart_sync[0][1]) | data_t.dtype
    dout = ccat(tuple_rect, cart_sync[1]) | Queue[data_t.dtype, 1]
    return dout


# if __name__ == "__main__":
#     feature_num = 2913
#     w_rect_data = 20
#     w_weight_data = 3
#     feature_size = (25, 25)
#     seq = list(range(feature_num))
#     rects_mem(
#         rd_addr_if=drv(t=Uint[12], seq=seq),
#         inst_num=0,
#         feature_num=feature_num,
#         w_rect_data=w_rect_data,
#         w_weight_data=w_weight_data,
#         feature_size=feature_size,
#         sim_cls=SimVerilated) | shred

#     sim(outdir='build',
#         check_activity=True,
#         extens=[partial(Gearbox, live=True, reload=True)])
