from cascade_classifier.python_utils.frame import FrameClass

from cascade_classifier.pygears_impl.design.ii_gen import ii_gen, sii_gen

from pygears.typing import Queue, Uint
from pygears.lib.verif import directed
from pygears.sim import sim
from pygears.lib.verif import drv
from pygears.sim.modules.verilator import SimVerilated

img_fn = '../../../datasets/proba.pgm'

img = FrameClass(img_fn, (5, 5))

seq = [img.img]
ref_ii = [img.ii.tolist()]
ref_sii = [img.sii.tolist()]

directed(
    drv(t=Queue[Uint[8], 2], seq=seq),
    f=ii_gen(frame_size=img.frame_size, sim_cls=SimVerilated),
    ref=ref_ii)
directed(
    drv(t=Queue[Uint[8], 2], seq=seq),
    f=sii_gen(frame_size=img.frame_size, sim_cls=SimVerilated),
    ref=ref_sii)
sim("build/")
