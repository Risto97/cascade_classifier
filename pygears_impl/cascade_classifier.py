from pygears import gear, Intf
from pygears.typing import Queue, Uint, Unit, Int, Tuple

from ii_gen import ii_gen
from ii_gen import sii_gen
from img_ram import img_ram
from rd_addrgen import rd_addrgen, addr_trans
from stddev import stddev
from frame_buffer import frame_buffer
from classifier import classifier
from features import features
from addr_utils import feature_addr, stage_counter

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from gearbox import Gearbox
from functools import partial

from pygears.common import flatten, shred, cart, fmap, invert, dreg, demux_by
from pygears.cookbook import replicate

from gears.accum import accum_on_eot
from gears.yield_on_one import yield_on_one

from image import loadImage

import math

img = loadImage("../datasets/proba.pgm")
# img = loadImage("../datasets/rtl7.jpg")
img_size = img.shape
frame_size = (25, 25)
feature_num = 2913
stage_num = 25
w_addr = math.ceil(math.log(frame_size[0] * frame_size[1], 2))
addr_t = Queue[Uint[w_addr], 2]
din_t = Queue[Uint[8], 1]

seq = [img.flatten(), img.flatten()]

w_rect_data = 20
w_weight_data = 3


@gear(svgen={'compile': True})
async def yield_zeros_and_eot(din: Queue['data_t', 1]) -> Uint[1]:
    async for (data, eot) in din:
        if data == 0:
            yield data
        elif data == 1 and eot == 1:
            yield data


@gear
def send_result(addr: Queue[Tuple['y_scaled', 'x_scaled'], 1],
                res: Queue[Uint[1], 1]):

    demux_ctrl = res | yield_zeros_and_eot

    no_detect, detect = demux_by(demux_ctrl, addr[0])
    no_detect | shred

    interrupt = addr[1]
    return detect, interrupt


@gear
def cascade_classifier(
        din: Queue[Uint['w_din'], 1],
        *,
        img_size=(240, 320),
        frame_size=(25, 25),
        stage_num,
        feature_num):
    ram_size = img_size[0] * img_size[1]
    w_addr_img = math.ceil(math.log(ram_size, 2))

    rd_addr_s, scaled_addr = rd_addrgen(frame_size=frame_size)
    rd_addr_s = rd_addr_s | addr_trans(img_size=img_size)
    img_s = img_ram(din, rd_addr_s, img_size=img_size)

    ii_s = img_s | ii_gen(frame_size=frame_size) | dreg
    sii_s = img_s | sii_gen(frame_size=frame_size) | dreg

    stddev_s = stddev(ii_s, sii_s, frame_size=frame_size)

    rst_local = Intf(Unit)
    rst_local_delayed = Intf(Unit)

    stage_cnt = stage_counter(rst_in=rst_local_delayed, stage_num=stage_num) | dreg
    rd_addr_feat = feature_addr(
        rst_in=rst_local_delayed,
        stage_counter=stage_cnt,
        feature_num=feature_num) | dreg
    rect_addr = features(
        rd_addr_feat,
        rst_in=rst_local_delayed,
        feature_num=feature_num,
        feature_size=frame_size,
        w_rect_data=w_rect_data,
        w_weight_data=w_weight_data) | dreg

    fb_rd = frame_buffer(
        ii_s | flatten, rect_addr, rst_in=rst_local, frame_size=frame_size) | dreg

    class_res = classifier(
        rst_in=rst_local_delayed,
        fb_data=fb_rd,
        feat_addr=rd_addr_feat,
        stage_addr=stage_cnt,
        stddev=stddev_s,
        feature_num=feature_num,
        stage_num=stage_num)

    detected_addr, interrupt = send_result(addr=scaled_addr, res=class_res)

    rst_local |= class_res | yield_on_one
    rst_local_delayed |= rst_local | dreg | dreg | dreg | dreg

    return detected_addr, interrupt


if __name__ == "__main__":

    detected_addr, interrupt = cascade_classifier(
        din=drv(t=din_t, seq=seq),
        img_size=img_size,
        frame_size=frame_size,
        feature_num=feature_num,
        stage_num=stage_num,
        sim_cls=partial(SimVerilated, timeout=1000000))

    detected_addr | shred
    interrupt | shred

    from pygears.svgen import svgen
    from pygears.conf.registry import registry, bind
    bind('svgen/debug_intfs', [])
    svgen('/cascade_classifier', outdir='/tools/home/work/cascade_classifier_vivado/iprepo/cascade_classifier_pygears/build/', wrapper=True)

    # from pygears.sim.extens.vcd import VCD
    # sim(outdir='build', extens=[VCD])

    # sim(outdir='build',
    #     check_activity=True,
    #     extens=[partial(Gearbox, live=True, reload=True)])
