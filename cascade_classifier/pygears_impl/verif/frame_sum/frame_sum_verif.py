from cascade_classifier.python_utils.frame import FrameClass

from cascade_classifier.pygears_impl.design.ii_gen import ii_gen, sii_gen
from cascade_classifier.pygears_impl.design.frame_sum import frame_sum

from pygears.typing import Queue, Uint
from pygears.lib.verif import directed
from pygears.sim import sim
from pygears.lib.verif import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears.lib import shred

img_fn = '../../../datasets/proba.pgm'

img = FrameClass(img_fn, (5, 5))

seq_ii = [img.ii]
seq_sii = [img.sii]
ref_ii = [[[img.ii_sum]]]
ref_sii = [[[img.sii_sum]]]

directed(
    drv(t=Queue[Uint[32], 2], seq=seq_ii),
    f=frame_sum( sim_cls=SimVerilated),
    ref=ref_ii)
directed(
    drv(t=Queue[Uint[32], 2], seq=seq_sii),
    f=frame_sum( sim_cls=SimVerilated),
    ref=ref_sii)
sim(outdir="build")

# frame_sum(din=drv(t=Queue[Uint[32], 2], seq=seq_ii), sim_cls=SimVerilated) | shred
