''' Source Vivado before running this script'''

from svgen import svgen_cascade
from ip_pack import ip_pack_tcl_gen
import shutil

xml_file = r"../../xml_models/haarcascade_frontalface_default.xml"
ip_loc = '../build/ip_repo/cascade_classifier_ip/'
sv_outdir = ip_loc + 'src'

print(f"Deleting ip_core at: {ip_loc}")
shutil.rmtree(ip_loc, ignore_errors=True)

print(f"PyGears svgen for xml: {xml_file} \nAt location: {sv_outdir}")
svgen_cascade(xml_file=xml_file, img_size=(240, 320), outdir=sv_outdir)

print(f"Generating ip_pack vivado tcl script")
ip_pack_tcl_gen(
    name="cascade_classifier",
    part="xc7z020clg400-1",
    board="myir.com:mys-7z020:part0:2.1",
    outdir=ip_loc)
