import shutil
import os
from cascade_classifier.scripts.ip_pack import ip_pack_tcl_gen
from cascade_classifier.scripts.run_synth import run_synth

name="cascade_classifier"
ip_loc = 'build/ip_repo/cascade_classifier_rtl_ip/'
sv_outdir = os.path.join(ip_loc, 'src')
print(ip_loc)

print(f"Deleting ip_core at: {ip_loc}")
shutil.rmtree("top/obj_dir", ignore_errors=True)
shutil.rmtree("build", ignore_errors=True)
shutil.copytree("top", sv_outdir)

ip_pack_tcl_gen(
    name=name,
    part="xc7z020clg400-1",
    board="myir.com:mys-7z020:part0:2.1",
    outdir=ip_loc)

ip_prj_fn = os.path.join(ip_loc, name) + "_ip"
run_synth(ip_prj_fn)
