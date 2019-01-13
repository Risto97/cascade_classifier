from pygears import gear, Intf
from pygears.typing import Queue, Uint, Tuple

from ii_gen import ii_gen
from ii_gen import sii_gen
from img_ram import img_ram
from rd_addrgen import rd_addrgen, addr_trans
from stddev import stddev
from frame_buffer import frame_buffer
from classifier import classifier, get_leaf_num, leaf_vals
from features import features
from roms import feature_addr

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.common import shred, czip, ccat, zip_sync, flatten
from pygears.cookbook import rng

from pygears.svgen import svgen

from image import loadImage

import math

img = loadImage("../datasets/rtl.pgm")
img_size = img.shape
frame_size = (25, 25)
feature_num = 2913
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
        feature_num):

    rd_addr_s = rd_addrgen(
        img_size=img_size, frame_size=frame_size) | addr_trans(
            img_size=img_size) | Queue[Uint[12], 3]
    img_s = img_ram(din, rd_addr_s, img_size=img_size)

    ii_s = img_s | ii_gen(frame_size=frame_size)
    sii_s = img_s | sii_gen(frame_size=frame_size)

    stddev_s = stddev(ii_s, sii_s, frame_size=frame_size)

    rd_addr_feat = feature_addr(feature_num=feature_num)
    rect_addr = features(
        rd_addr_feat,
        feature_num=feature_num,
        feature_size=frame_size,
        w_rect_data=w_rect_data,
        w_weight_data=w_weight_data)

    fb_rd = frame_buffer(ii_s | flatten, rect_addr, frame_size=frame_size)

    classifier_o = classifier(fb_data=fb_rd, stddev=stddev_s, feature_num=feature_num) | leaf_vals(feature_num=feature_num)

    dout = classifier_o
    return dout


if __name__ == "__main__":

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
        # rd_addr=drv(t=addr_t, seq=rd_seq),
        img_size=img_size,
        frame_size=frame_size,
        feature_num=feature_num,
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
