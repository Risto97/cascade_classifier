from pygears import gear
from pygears.typing import Queue, Uint, Int

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from gearbox import Gearbox
from functools import partial


@gear(svgen={'compile': True})
async def first_data(din: Queue[Uint['w_data'], 1]) -> b'Uint[w_data]':
    eot_s = 1
    async for (data, eot) in din:
        if eot_s == 1:
            yield data
        eot_s = eot


@gear(svgen={'compile': True})
async def last_data(din: Queue[Int['w_data'], 1]) -> b'Int[w_data]':
    async for (data, eot) in din:
        if eot == 1:
            yield data


@gear(svgen={'compile': True})
async def queue_edges(din: Queue[Uint['w_data'], 2], *,
                      w_data=b'w_data') -> b'Queue[Uint[w_data], 2]':
    eot_s = Uint[2](1)
    async for (data, eot) in din:
        if eot_s == 1 or (eot == 1 or eot == 3):
            yield (data, eot)

        eot_s = eot


@gear(svgen={'compile': True})
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


if __name__ == "__main__":
    from pygears.common import shred
    seq = []
    for i in range(3):
        seq_y = []
        for y in range(5):
            seq_x = []
            for x in range(5):
                seq_x.append(x)
            seq_y.append(seq_x)
        seq.append(seq_y)

    queue_head_tail(
        din=drv(t=Queue[Uint[8], 2], seq=seq), sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(Gearbox, live=True, reload=True)])
