from pygears import gear
from pygears.typing import Queue, Uint, Int


@gear(hdl={'compile': True, 'inline_conditions': True})
async def first_data(din: Queue[Uint['w_data'], 1]) -> b'Uint[w_data]':
    eot_s = 1
    async for (data, eot) in din:
        if eot_s == 1:
            yield data
        eot_s = eot


@gear(hdl={'compile': True, 'inline_conditions': True})
async def last_data(din: Queue[Int['w_data'], 1]) -> b'Int[w_data]':
    async for (data, eot) in din:
        if eot == 1:
            yield data


@gear(hdl={'compile': True, 'inline_conditions': True})
async def queue_edges(din: Queue[Uint['w_data'], 2], *,
                      w_data=b'w_data') -> b'Queue[Uint[w_data], 2]':
    eot_s = Uint[2](1)
    async for (data, eot) in din:
        if eot_s == 1 or (eot == 1 or eot == 3):
            yield (data, eot)

        eot_s = eot


@gear(hdl={'compile': True, 'inline_conditions': True})
async def pick_queue_edges(din: Queue[Uint['w_data'], 2], *,
                           w_data=b'w_data') -> b'Queue[Uint[w_data], 2]':
    output_active = Uint[1](1)
    async for (data, eot) in din:
        if eot == 1:
            output_active = 0

        if output_active == 1 or (eot == 2 or eot == 3):
            yield (data, eot)


@gear
def queue_head_tail(din: Queue[Uint['w_data'], 2], *, w_data=b'w_data'):
    dout = din | queue_edges | pick_queue_edges
    return dout
