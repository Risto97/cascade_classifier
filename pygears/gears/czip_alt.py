from pygears import gear
from pygears.typing import Queue, Uint

from pygears.sim import sim
from pygears.sim.modules import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears_view import PyGearsView
from functools import partial

from pygears.common import ccat, flatten, shred

din_t = Queue[Uint[8], 1]


@gear
def czip_alt2(din0, din1):

    zip_eot = ccat(din0[1], din1[1]) | Uint[2]
    zip_data = ccat(din0[0], din1[0])

    zip_sync = ccat(zip_data, zip_eot) | Queue[zip_data.dtype, 2] | flatten

    return zip_sync

@gear
def czip_alt3(din0, din1, din2):

    zip_eot = ccat(din0[1], din1[1], din2[1]) | Uint[3]
    zip_data = ccat(din0[0], din1[0], din2[0])

    zip_sync = ccat(zip_data, zip_eot) | Queue[zip_data.dtype, 3] | flatten(lvl=2)

    return zip_sync



if __name__ == "__main__":
    rd_seq0 = [list(range(30))]
    rd_seq1 = [list(range(30))]
    rd_seq2 = [list(range(30))]

    czip_alt3(
        din0=drv(t=din_t, seq=rd_seq0),
        din1=drv(t=din_t, seq=rd_seq1),
        din2=drv(t=din_t, seq=rd_seq2),
        sim_cls=SimVerilated) | shred

    sim(outdir='build',
        check_activity=True,
        extens=[partial(PyGearsView, live=True, reload=True)])
