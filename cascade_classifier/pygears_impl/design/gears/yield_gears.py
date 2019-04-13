from pygears import gear
from pygears.typing import Queue, Uint, Unit

@gear
def yield_on_one(din: Queue[Uint[1], 1]) -> Unit:
    pass

@gear(svgen={'compile': True})
async def yield_on_one_uint(din: Uint[1]) -> Uint[1]:
    async with din as data:
        if data == 1:
            yield data


@gear(svgen={'compile': True})
async def yield_zeros_and_eot(din: Queue['data_t', 1]) -> Uint[1]:
    async for (data, eot) in din:
        if data == 0:
            yield data
        elif data == 1 and eot == 1:
            yield data
