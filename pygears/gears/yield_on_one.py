from pygears import gear
from pygears.typing import Queue, Uint, Unit

@gear
def yield_on_one(din: Queue[Uint[1], 1]) -> Unit:
    pass
