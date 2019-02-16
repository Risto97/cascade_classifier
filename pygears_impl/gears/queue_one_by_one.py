from pygears import gear, Intf
from pygears.typing import Queue, Uint, Unit

from pygears.svgen import svgen

@gear
def queue_one_by_one(din0: 'w_din0', din1: 'w_din1') -> ('w_din0', 'w_din1'):
    pass


# queue_one_by_one(din0=Intf(Queue[Uint[8], 1]), din1=Intf(Queue[Uint[16], 4]))
# svgen('/queue_one_by_one', outdir='build/queue_one_by_one', wrapper=True)
