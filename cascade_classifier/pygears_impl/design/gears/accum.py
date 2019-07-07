from pygears import gear
from pygears.typing import Queue, Uint
import math


@gear(hdl={'compile': True, 'inline_conditions': True})
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


@gear(hdl={'compile': True, 'inline_conditions': True})
async def accum_on_eot(
        din: Queue['data_t', 1],
        *,
        add_num,
        data_t=b'data_t',
        dout_w=b'math.ceil(math.log(add_num*2**len(data_t), 2))') -> b'din[0]':
    acc = Uint[dout_w](0)
    async for (data, eot) in din:
        acc = acc + int(data)
    yield acc


@gear(hdl={'compile': True, 'inline_conditions': True})
async def accum_when_eot(
        din: Queue['data_t', 2],
        *,
        add_num,
        data_t=b'data_t',
        dout_w=b'math.ceil(math.log(add_num*2**len(data_t), 2))'
) -> b'Queue[Uint[dout_w], 2]':
    acc = Uint[dout_w](0)
    async for (data, eot) in din:
        if (eot == 1):
            acc = acc + int(data) + 1
        yield (acc, eot)
