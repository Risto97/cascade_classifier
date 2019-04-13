from pygears import gear
from pygears.typing import Int, Queue, Uint

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from functools import partial

from pygears.common import shred
from gears.queue_ops import queue_head_tail


@gear(svgen={'compile': True})
async def frame_sum_rtl(din: Queue[Uint['w_din'], 2], *,
                        w_dout=b'w_din+2') -> b'Queue[Int[w_dout], 2]':
    cnt = Uint[2](0)
    acc = Int[w_dout](0)

    async for (data, eot) in din:
        if cnt == 0:
            acc = acc + int(data)
        elif cnt == 3:
            acc = acc + int(data)
            yield (acc, eot)
        elif cnt == 1 or cnt == 2:
            acc = acc - int(data)
        cnt = cnt + 1


@gear
def frame_sum(din: Queue[Uint['w_din'], 2], *, w_din=b'w_din'):
    dout = din | queue_head_tail | frame_sum_rtl
    return dout


# if __name__ == "__main__":
#     seq = []
#     for i in range(3):
#         seq_y = []
#         for y in range(5):
#             seq_x = []
#             for x in range(5):
#                 seq_x.append(x + 1 + y * 5)
#             seq_y.append(seq_x)
#         seq.append(seq_y)

#     frame_sum(
#         din=drv(t=Queue[Uint[8], 2], seq=seq), sim_cls=SimVerilated) | shred

#     sim(outdir='build',
#         check_activity=True,
#         extens=[partial(Gearbox, live=True, reload=True)])
