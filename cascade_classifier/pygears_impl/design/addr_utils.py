from pygears import gear
from pygears.typing import Queue, Uint, Tuple, Unit

from pygears.lib import ccat, dreg
from pygears.lib import cart_sync_with
from pygears.lib.rom import rom
from pygears.lib import rng
from pygears.lib import dreg as dreg_sp

from pygears.lib import local_rst

import math


@gear
def rng_cnt(*, cnt_num):
    w_cnt_addr = math.ceil(math.log(cnt_num, 2))
    cfg_rng = ccat(0, Uint[w_cnt_addr](cnt_num), 1)
    cnt = cfg_rng | rng

    return cnt


@gear
def stage_counter(rst_in: Unit, *, stage_num):
    rst_in | local_rst
    stage_cnt = rng_cnt(cnt_num=stage_num)

    return stage_cnt | dreg_sp


@gear
def feature_addr(stage_counter: Queue[Uint['w_stage_addr'], 1], rst_in: Unit,
                 *, casc_hw):
    rst_in | local_rst

    stage_counter = stage_counter
    feature_num_in_stage = stage_counter[0] | rom(
        data=casc_hw.features_stage_count_mem,
        dtype=Uint[casc_hw.w_features_stage_count])

    cnt_end, cnt_start = feature_num_in_stage | Tuple[Uint[
        casc_hw.w_features_stage_count /
        2], Uint[casc_hw.w_features_stage_count / 2]]

    feature_cnt = ccat(cnt_start, cnt_end, 1) | rng
    stage_counter = stage_counter | cart_sync_with(feature_cnt)

    dout_eot = ccat(feature_cnt[1], stage_counter[1]) | Uint[2]
    feature_cnt = ccat(
        feature_cnt[0],
        dout_eot) | Queue[Uint[int(casc_hw.w_features_stage_count / 2)], 2]

    return feature_cnt | dreg
