from pygears import gear
from pygears.typing import Queue, Tuple, Integer, Uint

@gear(svgen={'compile': True})
async def accum(din: Queue['data_t', 2]) -> b'Queue[Uint[18], 1]':
    acc = Uint[18](0)
    ret = Uint[18](0)
    async for (data, eot) in din:
        if(eot[0] == 1):
            ret = acc + int(data)
            acc = Uint[18](0)
            yield (ret, eot[1] * eot[0])
        else:
            acc = acc + int(data)
            yield (acc, eot[1] * eot[0])
