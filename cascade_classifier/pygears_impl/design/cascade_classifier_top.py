from pygears import gear, Intf
from pygears.typing import Queue, Tuple, Uint, Union, Unit

from .ii_gen import ii_gen
from .ii_gen import sii_gen
from .img_ram import img_ram
from .rd_addrgen import rd_addrgen
from .stddev import stddev
from .frame_buffer import frame_buffer
from .classifier import classifier
from .features_mem import features_mem
from .addr_utils import feature_addr, stage_counter

from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from functools import partial

from pygears.common import czip, flatten, shred
from pygears.common.filt import qfilt

from .gears.yield_gears import yield_on_one, yield_on_one_uint, yield_zeros_and_eot


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
def cascade_classifier(din: Queue[Uint['w_din'], 1], *, casc_hw):

    rd_addr_s, maybe_send_addr = rd_addrgen(casc_hw=casc_hw)
    img_s = img_ram(din, rd_addr_s, img_size=casc_hw.img_size)

    ii_s = img_s | ii_gen(frame_size=casc_hw.frame_size)
    sii_s = img_s | sii_gen(frame_size=casc_hw.frame_size)

    stddev_s = stddev(ii_s, sii_s, casc_hw=casc_hw)

    rst_local = Intf(Unit)

    stage_cnt = stage_counter(rst_in=rst_local, stage_num=casc_hw.stage_num)
    rd_addr_feat = feature_addr(
        rst_in=rst_local, stage_counter=stage_cnt, casc_hw=casc_hw)

    rect_addr = features_mem(rd_addr_feat, rst_in=rst_local, casc_hw=casc_hw)

    fb_rd = frame_buffer(
        ii_s | flatten,
        rect_addr,
        rst_in=rst_local,
        frame_size=casc_hw.frame_size)

    class_res = classifier(
        rst_in=rst_local,
        fb_data=fb_rd,
        feat_addr=rd_addr_feat,
        stage_addr=stage_cnt,
        stddev=stddev_s,
        casc_hw=casc_hw)

    detected_addr, interrupt = send_result(addr=maybe_send_addr, res=class_res)

    rst_local |= class_res | yield_on_one

    return detected_addr, interrupt
