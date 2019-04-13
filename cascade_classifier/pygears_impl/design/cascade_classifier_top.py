from pygears import gear, Intf
from pygears.typing import Queue, Tuple, Uint, Union, Unit

from ii_gen import ii_gen
from ii_gen import sii_gen
from img_ram import img_ram
from rd_addrgen import rd_addrgen
from stddev import stddev
from frame_buffer import frame_buffer
from classifier import classifier
from features_mem import features_mem
from addr_utils import feature_addr, stage_counter

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from functools import partial

from pygears.common import czip, dreg, flatten, shred
from pygears.common.filt import qfilt

from gears.yield_gears import yield_on_one, yield_on_one_uint, yield_zeros_and_eot

from cascade_classifier.python_utils.image import ImageClass

import math

img_fn = "../../datasets/rtl7.jpg"
img = ImageClass()
img.loadImage(img_fn)
img = img.img
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


@gear
def send_result(
        addr: Queue[Tuple[Uint['w_scale'], Tuple['y_scaled', 'x_scaled']], 1],
        res: Queue[Uint[1], 1]):

    demux_ctrl = res | yield_zeros_and_eot

    maybe_send = czip(addr, demux_ctrl) | Queue[Union[Unit, addr.dtype[0]], 1]
    detected_addr = maybe_send | qfilt(sel=1)
    interrupt = maybe_send[1] | yield_on_one_uint

    return detected_addr, interrupt


@gear
def cascade_classifier(din: Queue[Uint['w_din'], 1],
                       *,
                       img_size=(240, 320),
                       frame_size=(25, 25),
                       stage_num,
                       feature_num):

    rd_addr_s, maybe_send_addr = rd_addrgen(
        img_size=img_size, frame_size=frame_size)
    img_s = img_ram(din, rd_addr_s, img_size=img_size)

    ii_s = img_s | ii_gen(frame_size=frame_size)
    sii_s = img_s | sii_gen(frame_size=frame_size)

    stddev_s = stddev(ii_s, sii_s, frame_size=frame_size)

    rst_local = Intf(Unit)

    stage_cnt = stage_counter(rst_in=rst_local, stage_num=stage_num)
    rd_addr_feat = feature_addr(rst_in=rst_local, stage_counter=stage_cnt)
    rect_addr = features_mem(
        rd_addr_feat,
        rst_in=rst_local,
        feature_num=feature_num,
        feature_size=frame_size,
        w_rect_data=w_rect_data,
        w_weight_data=w_weight_data)

    fb_rd = frame_buffer(
        ii_s | flatten, rect_addr, rst_in=rst_local, frame_size=frame_size)

    class_res = classifier(
        rst_in=rst_local,
        fb_data=fb_rd,
        feat_addr=rd_addr_feat,
        stage_addr=stage_cnt,
        stddev=stddev_s,
        feature_num=feature_num,
        stage_num=stage_num)

    detected_addr, interrupt = send_result(addr=maybe_send_addr, res=class_res)

    rst_local |= class_res | yield_on_one

    return detected_addr, interrupt


# if __name__ == "__main__":

detected_addr, interrupt = cascade_classifier(
    din=drv(t=din_t, seq=seq),
    img_size=img_size,
    frame_size=frame_size,
    feature_num=feature_num,
    stage_num=stage_num,
    sim_cls=partial(SimVerilated, timeout=1000000))

detected_addr | shred
interrupt | shred

# from pygears.svgen import svgen
# from pygears.conf.registry import registry, bind
# bind('svgen/debug_intfs', [])
# svgen('/cascade_classifier', outdir='/tools/work/vivado/iprepo/cascade_classifier_pygears/build/', wrapper=True)

# from pygears.sim.extens.vcd import VCD
# sim(outdir='build', extens=[VCD])

# sim(outdir='build',
#     check_activity=True,
#     extens=[partial(Gearbox, live=True, reload=True)])
