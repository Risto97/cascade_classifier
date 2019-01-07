from pygears import alternative, gear
from pygears.conf import safe_bind
from pygears.core.intf import IntfOperPlugin
from pygears.typing import Integer, Tuple, Queue
from pygears.util.hof import oper_tree
from pygears.common import ccat


@gear(svgen={'compile': True})
async def add2(din: Tuple[Queue[Integer['N1'], 1], Integer['N2']]) -> b'Queue[din[0][0] + din[1], 1]':
    # dout_s = Queue[Uint[18], 1]
    async with din as data:
        yield (data[0][0] + data[1], data[0][1])
