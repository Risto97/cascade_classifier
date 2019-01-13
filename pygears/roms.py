from pygears import gear
from pygears.typing import Array, Int, Uint, Queue, Tuple

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.common import ccat, shred, dreg, decoupler, fifo, zip_sync, cart
from pygears.common import serialize
from pygears.cookbook import rng
from gears.serialize_queue import serialize_queue

TRdDin = Uint['w_addr']
outnames = ['rd_data_if']

import math
@gear
def feature_addr(*, feature_num):
    w_feat_addr = math.ceil(math.log(feature_num, 2))
    cfg_rng = ccat(0, Uint[w_feat_addr](feature_num), 1)
    rd_addr_feat = cfg_rng | rng | Uint[w_feat_addr]

    return rd_addr_feat

@gear(outnames=outnames, sv_submodules=['leafVal_mem', 'rom_rd_port'])
def leafVal_mem(rd_addr_if: TRdDin,
                *,
                w_addr=b'w_addr',
                w_data,
                val_num,
                depth) -> b'Int[w_data]':
    pass

@gear(outnames=outnames, sv_submodules=['stageThreshold_mem', 'rom_rd_port'])
def stageThreshold_mem(rd_addr_if: TRdDin,
                         *,
                         w_addr=b'w_addr',
                         w_data,
                         depth) -> b'Int[w_data]':
    pass

@gear(outnames=outnames, sv_submodules=['featureCount_mem', 'rom_rd_port'])
def featureCount_mem(rd_addr_if: TRdDin,
                         *,
                         w_addr=b'w_addr',
                         w_data,
                         depth) -> b'Uint[w_data]':
    pass

@gear(outnames=outnames, sv_submodules=['featureThreshold_mem', 'rom_rd_port'])
def featureThreshold_mem(rd_addr_if: TRdDin,
                         *,
                         w_addr=b'w_addr',
                         w_data,
                         depth) -> b'Int[w_data]':
    pass

@gear(outnames=outnames, sv_submodules=['features_rom', 'rom_rd_port'])
def features_rom(rd_addr_if: TRdDin,
                 *,
                 rects_weights,
                 inst_num,
                 w_addr=b'w_addr',
                 w_data,
                 depth=5) -> b'Uint[w_data]':
    pass


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
    B = (A + width) | Uint[w_rect]
    D = (A + width + height * feature_size[1]) | Uint[w_rect]
    C = ((A + width + height * feature_size[1]) - width) | Uint[w_rect]

    sign = ccat(1, 0, 0, 1) | Array[Uint[1], 4] | serialize
    rect_coord = ccat(A, B, C, D) | Array[Uint[w_rect], 4] | serialize_queue

    return ccat(rect_coord[0], sign, rect_coord[1]) | \
        Queue[Tuple[Uint[w_rect], Uint[1]], 1]

@gear
def rects_mem(rd_addr_if: TRdDin, *, inst_num, w_rect_data, w_weight_data,
              feature_num, feature_size):
    w_rect = int(w_rect_data / 2)
    rect_tuple = features_rom(
        rd_addr_if,
        rects_weights=0,
        inst_num=inst_num,
        w_data=w_rect_data,
        depth=feature_num) | \
        Tuple[Uint[w_rect/2], Uint[w_rect/2], Uint[w_rect]]

    rect_coords = rect_tuple | calc_rect_coords(feature_size=feature_size)

    weight = features_rom(
        rd_addr_if,
        rects_weights=1,
        inst_num=inst_num,
        w_data=w_weight_data,
        depth=feature_num) | Int[w_weight_data]

    return cart(rect_coords, weight)


@gear
def weights_mem(rd_addr_if: TRdDin, *, inst_num, w_data, feature_num):
    weight = features_rom(
        rd_addr_if,
        rects_weights=1,
        inst_num=inst_num,
        w_data=w_data,
        depth=feature_num) | Int[w_data]

    return weight


if __name__ == "__main__":
    feature_num = 2913
    w_rect_data = 20
    w_weight_data = 3
    feature_size = (25, 25)
    seq = list(range(feature_num))
    # rects_mem(
    #     rd_addr_if=drv(t=Uint[12], seq=seq),
    #     inst_num=0,
    #     feature_num=feature_num,
    #     w_rect_data=w_rect_data,
    #     w_weight_data=w_weight_data,
    #     feature_size=feature_size,
    #     sim_cls=SimVerilated) | shred
    featureThreshold_mem(
        rd_addr_if=drv(t=Uint[12], seq=seq),
        w_data=13,
        depth=feature_num,
        sim_cls=SimVerilated) | shred


    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
