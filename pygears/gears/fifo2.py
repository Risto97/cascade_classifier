from pygears import gear, module, GearDone
from pygears.sim import delta, clk


@gear
async def fifo2(din, *, depth=2, threshold=0, preload=0, regout=False) -> b'din':
    '''For this implementation depth must be a power of 2'''
