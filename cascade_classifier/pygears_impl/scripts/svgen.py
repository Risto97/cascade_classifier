from cascade_classifier.pygears_impl.design import cascade_classifier
from cascade_classifier.python_utils.cascade_hw import CascadeHW

from pygears.typing import Queue, Uint
from pygears.lib import shred
from pygears.lib import drv
from pygears.hdl.hdlgen import hdlgen
from pygears.conf.registry import bind

from pygears.synth import list_hdl_files

from cascade_classifier.pygears_impl.scripts.svlib_utils import copy_svlib, sed_intf


def svgen_cascade(xml_file, img_size, outdir):
    cascade_hw = CascadeHW(xml_file, img_size=img_size)
    din_t = Queue[Uint[8], 1]
    detected_addr, interrupt = cascade_classifier(
        din=drv(t=din_t, seq=[]), casc_hw=cascade_hw)

    detected_addr | shred
    interrupt | shred

    bind('debug/trace', [])
    hdlgen('/cascade_classifier', outdir=outdir, wrapper=True, copy_files=True)
    # print(list_hdl_files('/cascade_classifier', outdir='/tools/tmp/', language='sv'))

    # print("Copying svlib files to project")
    # copy_svlib()
    print("Replacing producer, consumer strings with master, slave")
    sed_intf(producer='master', consumer='slave')

# xml_file = r"../../xml_models/haarcascade_frontalface_default.xml"
# ip_loc = '../build/ip_repo/cascade_classifier_ip/'
# sv_outdir = ip_loc + 'src'
# svgen_cascade(xml_file, img_size=(240,320), outdir=sv_outdir)
