from pygears import gear
from pygears.typing import Queue, Uint
import math

@gear(svgen={'compile': True})
async def accum(din: Queue['data_t', 1],
                *,
                add_num,
                data_t=b'data_t',
                dout_w=b'math.ceil(math.log(add_num*2**len(data_t), 2))'
                ) -> b'Queue[Uint[dout_w]]':
    acc = Uint[dout_w](0)
    async for (data, eot) in din:
        acc = acc + int(data)
        yield (acc, eot)
