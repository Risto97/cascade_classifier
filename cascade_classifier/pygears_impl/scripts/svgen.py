from cascade_classifier.pygears_impl.design import cascade_classifier
from cascade_classifier.python_utils.cascade_hw import CascadeHW

from pygears.typing import Queue, Uint
from pygears.lib import shred
from pygears.sim.modules import drv
from pygears.svgen import svgen
from pygears.conf.registry import bind

from cascade_classifier.pygears_impl.scripts.svlib_utils import copy_svlib, sed_intf


def svgen_cascade(xml_file, img_size, outdir):
    cascade_hw = CascadeHW(xml_file, img_size=img_size)
    din_t = Queue[Uint[8], 1]
    detected_addr, interrupt = cascade_classifier(
        din=drv(t=din_t, seq=[]), casc_hw=cascade_hw)

    detected_addr | shred
    interrupt | shred

    bind('hdl/debug_intfs', [])
    svgen('/cascade_classifier', outdir=outdir, wrapper=True)

    print("Copying svlib files to project")
    copy_svlib()
    print("Replacing producer, consumer strings with master, slave")
    sed_intf(producer='master', consumer='slave')
