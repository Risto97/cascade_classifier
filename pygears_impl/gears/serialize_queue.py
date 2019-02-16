from pygears import gear
from pygears.typing import Array, Queue, Tuple, Uint, bitw

TDin = Array[Uint['w_data'], 'no']
TOut = Queue[Uint['w_data'], 1]

@gear(svgen={'compile': True})
async def serialize_queue(din: TDin,
                           *,
                           w_data=b'w_data',
                           no=b'no') -> TOut:
    i = Uint[bitw(no)](0)
    async with din as val:
        for i in range(len(val)):
            yield(val[i], i == no-1)
