from pygears import gear
from pygears.typing import Tuple, Uint

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.common import shred

TRdDin = Uint['w_addr']
outnames = ['rd_data_if']

@gear(outnames=outnames)
def rom_rd_port(rd_addr_if: TRdDin, *, depth) -> b'Uint[16]':
    pass

@gear(
    outnames=outnames, sv_submodules=['rom_mem', 'rom_rd_port'])
def rom(rd_addr_if: TRdDin,
        *,
        w_addr=b'w_addr',
        depth=5) -> b'Uint[16]':
    pass

@gear
def memory(rd_addr_if: TRdDin,
           *,
           w_addr=b'w_addr',
           depth=10):

    dout = rom(rd_addr_if, depth=depth)

    return dout

if __name__ == "__main__":

    wr_seq = []
    for i in range(10):
        wr_seq.append((i+1,i+1))
    print(wr_seq)
    seq = list(range(255))
    memory(
        # wr_addr_data_if=drv(t=Tuple[Uint[8], Uint[16]], seq=wr_seq),
        rd_addr_if=drv(t=Uint[8], seq=seq),
        depth=255,
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])

    pass
