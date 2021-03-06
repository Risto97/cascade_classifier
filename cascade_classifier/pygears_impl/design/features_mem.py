from pygears import gear, Intf
from pygears.typing import Uint, Queue, Array, Tuple, Int, Unit

from pygears.lib import cart, ccat, czip, dreg, local_rst, rom
from pygears.lib.serialize import serialize_plain
from pygears.lib import decouple as decouple_sp
from pygears.lib import dreg as dreg_sp
from pygears.lib import replicate


@gear
def features_mem(rd_addr: Queue[Uint['w_addr'], 2], rst_in: Unit, *, casc_hw):

    w_rect = casc_hw.w_rect_data // 2

    rst_in | local_rst
    rd_addr = rd_addr | decouple_sp

    features_data = []
    for i in range(3):
        feature = rects_mem(rd_addr_if=rd_addr[0], inst_num=i, casc_hw=casc_hw)
        features_data.append(feature | decouple_sp)

    feature_data_t = Intf(Tuple[Uint[w_rect], Uint[1], Int[casc_hw.w_weight]])
    features_zip = czip(
        *features_data) | Queue[Array[feature_data_t.dtype, 3], 1]

    sync = cart(rd_addr[1] | dreg, features_zip)

    dout_eot = ccat(sync[1], sync[0][0]) | Uint[3]
    dout = ccat(sync[0][1],
                dout_eot) | Queue[Array[feature_data_t.dtype, 3], 3]
    return dout


@gear
def calc_rect_coords(
        din: Tuple[Uint['w_meas'], Uint['w_meas'], Uint['w_rect']],
        *,
        w_meas=b'w_meas',
        w_rect=b'w_rect',
        casc_hw):

    width = din[1]
    height = din[0]
    A = din[2]
    B = (A + width) | Uint[w_rect] | dreg_sp
    tmp = height * casc_hw.frame_size[1] | dreg_sp
    D = (B + tmp) | Uint[w_rect]

    C = (D - (width | dreg_sp)) | Uint[w_rect]

    sign = ccat(1, 0, 0, 1) | Array[Uint[1], 4] | serialize_plain
    rect_coord = ccat(A | dreg_sp, B, C, D) | Array[Uint[w_rect], 4]
    rect_coord = rect_coord |  serialize_plain

    return ccat(rect_coord[0], sign[0], rect_coord[1]) | \
        Queue[Tuple[Uint[w_rect], Uint[1]], 1]


@gear
def rects_mem(rd_addr_if: Uint['w_addr'], *, inst_num, casc_hw):
    w_rect = casc_hw.w_rect_data // 2
    rect_tuple = rom(
        rd_addr_if,
        data=casc_hw.rects_mem[inst_num],
        dtype=Uint[casc_hw.w_rect_data]) | \
        Tuple[Uint[w_rect/2], Uint[w_rect/2], Uint[w_rect]]

    rect_coords = rect_tuple | calc_rect_coords(casc_hw=casc_hw)

    weight = rom(
        rd_addr_if,
        data=casc_hw.weights_mem[inst_num],
        dtype=Int[casc_hw.w_weight])

    data_t = Intf(Tuple[Uint[w_rect], Uint[1], Int[casc_hw.w_weight]])

    cart_sync = cart(rect_coords, weight)
    tuple_rect = ccat(cart_sync[0][0], cart_sync[0][1]) | data_t.dtype
    dout = ccat(tuple_rect, cart_sync[1]) | Queue[data_t.dtype, 1]
    return dout
