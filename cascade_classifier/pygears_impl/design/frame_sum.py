from pygears import gear
from pygears.typing import Int, Queue, Uint

from cascade_classifier.pygears_impl.design.gears.queue_ops import queue_head_tail


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
