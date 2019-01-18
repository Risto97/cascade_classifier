from pygears import gear, Intf
from pygears.typing import Queue, Uint, Unit, Int

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
from pygears_view import PyGearsView
from functools import partial

from pygears.common import flatten, shred, cart, fmap, neg
from pygears.cookbook import replicate

from gears.accum import accum_on_eot
from gears.yield_on_one import yield_on_one

from image import loadImage

import math

img = loadImage("../datasets/rtl2.jpg")
img_size = img.shape
frame_size = (25, 25)
feature_num = 2913
stage_num = 25
w_addr = math.ceil(math.log(frame_size[0] * frame_size[1], 2))
addr_t = Queue[Uint[w_addr], 2]
din_t = Queue[Uint[8], 1]

seq = [img.flatten()]

w_rect_data = 20
w_weight_data = 3
@gear
def cascade_classifier(
        din: Queue[Uint['w_din'], 1],
        # rd_addr: addr_t,
        *,
        img_size=(240, 320),
        frame_size=(25, 25),
        stage_num,
        feature_num):
    ram_size = img_size[0] * img_size[1]
    w_addr_img = math.ceil(math.log(ram_size, 2))

    rd_addr_s = rd_addrgen(
        img_size=img_size, frame_size=frame_size) | addr_trans(
            img_size=img_size) | Queue[Uint[w_addr_img], 3]
    img_s = img_ram(din, rd_addr_s, img_size=img_size)

    ii_s = img_s | ii_gen(frame_size=frame_size)
    sii_s = img_s | sii_gen(frame_size=frame_size)

    stddev_s = stddev(ii_s, sii_s, frame_size=frame_size)

    rst_local = Intf(Unit)

    stage_cnt = stage_counter(rst_in=rst_local, stage_num=stage_num)
    rd_addr_feat = feature_addr(rst_in=rst_local, stage_counter=stage_cnt, feature_num=feature_num)
    rect_addr = features(
        rd_addr_feat,
        feature_num=feature_num,
        feature_size=frame_size,
        w_rect_data=w_rect_data,
        w_weight_data=w_weight_data)

    fb_rd = frame_buffer(ii_s | flatten, rect_addr, rst_in=rst_local, frame_size=frame_size)

    class_res = classifier(
        rst_in=rst_local,
        fb_data=fb_rd,
        feat_addr=rd_addr_feat,
        stage_addr=stage_cnt,
        stddev=stddev_s,
        feature_num=feature_num,
        stage_num=stage_num)

    rst_local |= neg(class_res[0]) | yield_on_one
    return class_res


if __name__ == "__main__":

    # from pygears.sim.extens.vcd import VCD
    rd_seq = []
    for i in range(5):
        rd_seq_n = []
        for n in range(10):
            rd_seq2 = []
            for i in range(frame_size[0] * frame_size[1]):
                rd_seq2.append(i)
            rd_seq_n.append(rd_seq2)
        rd_seq.append(rd_seq_n)

    cascade_classifier(
        din=drv(t=din_t, seq=seq),
        img_size=img_size,
        frame_size=frame_size,
        feature_num=feature_num,
        stage_num=stage_num,
        sim_cls=partial(SimVerilated, timeout=1000000)) | shred

    # sim(outdir='build', extens=[VCD])
    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
