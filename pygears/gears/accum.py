from pygears import gear
from pygears.typing import Queue, Tuple, Integer, Uint

@gear(svgen={'compile': True})
async def accum(din: Queue['data_t', 1]) -> b'Uint[18]':
    acc = Uint[18](0)
    async for (data, eot) in din:
        acc = acc + int(data)
        yield acc
