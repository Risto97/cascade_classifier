from pygears import gear
from pygears.typing import Queue, Uint, Tuple, Unit

from pygears.sim import sim
from pygears.sim.modules.verilator import SimVerilated
from gearbox import Gearbox
from functools import partial

from pygears.common import ccat, shred, dreg
from pygears.common import cart_sync_with
from pygears.common.rom import rom
from pygears.cookbook import rng

from pygears.common import local_rst

import math

## change this ##
xml_file = r"../xml_models/haarcascade_frontalface_default.xml"
from cascade_classifier.python_utils.cascade import CascadeClass
cascade = CascadeClass(xml_file)

featureStagesCount = cascade.getFeatureStagesCount()
stages_cnt_l = featureStagesCount[0]
w_stage_cnt = featureStagesCount[1]
#################


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

    return stage_cnt


@gear
def feature_addr(stage_counter: Queue[Uint['w_stage_addr'], 1], rst_in: Unit):
    rst_in | local_rst

    stage_counter = stage_counter | dreg
    feature_num_in_stage = stage_counter[0] | rom(
        data=stages_cnt_l, dtype=Uint[w_stage_cnt])

    cnt_end, cnt_start = feature_num_in_stage | Tuple[Uint[w_stage_cnt / 2],
                                                      Uint[w_stage_cnt / 2]]

    feature_cnt = ccat(cnt_start, cnt_end, 1) | rng
    stage_counter = stage_counter | cart_sync_with(feature_cnt)

    dout_eot = ccat(feature_cnt[1], stage_counter[1]) | Uint[2]
    feature_cnt = ccat(feature_cnt[0],
                       dout_eot) | Queue[Uint[int(w_stage_cnt / 2)], 2]

    return feature_cnt | dreg


if __name__ == "__main__":
    feature_num = 2913
    stage_num = 25

    feature_addr(
        feature_num=feature_num, stage_num=stage_num,
        sim_cls=SimVerilated) | shred
    sim(outdir='build',
        check_activity=True,
        extens=[partial(Gearbox, live=True, reload=True)])
