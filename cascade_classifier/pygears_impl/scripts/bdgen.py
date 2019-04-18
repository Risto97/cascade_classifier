import os

f = open("bd_gen.tcl", "w")

prj_name = "cascade_classifier_hdmi"
prj_loc = os.path.abspath(f"../build/{prj_name}/")
ip_repo_loc = os.path.abspath(os.path.join(prj_loc, "..", "ip_repo"))
part_name = "xc7z020clg400-1"
bd_name = "design_1"


print(ip_repo_loc)

tcl_string = f"""
create_project {prj_name} {prj_loc} -part {part_name}
set_property board_part myir.com:mys-7z020:part0:2.1 [current_project]
create_bd_design "{bd_name}"
update_compile_order -fileset sources_1
set_property  ip_repo_paths {ip_repo_loc} [current_project]
update_ip_catalog

open_bd_design {prj_loc}/{prj_name}.srcs/sources_1/bd/{bd_name}/{bd_name}.bd

startgroup
create_bd_cell -type ip -vlnv user.org:user:wrap_cascade_classifier:1.0 wrap_cascade_classif_0
endgroup
save_bd_design
"""

f.write(f"{tcl_string}")
