import os

def ip_pack_tcl_gen(name, part, board, outdir):
    f = open("ip_pack.tcl", "w")

    ip_name = name + "_ip"
    ip_loc = os.path.abspath(f"{outdir}/")
    ip_repo_loc = os.path.abspath(os.path.join(ip_loc, ".."))
    part_name = part
    top_name = "wrap_" + name

    f.write(f"create_project {ip_name} {ip_loc} -part {part_name}"+"\n\n")
    f.write(f"set_property board_part {board} [current_project]"+"\n\n")
    f.write(f"add_files {outdir}/src/"+"\n\n")
    f.write(f"set_property top {top_name} [current_fileset]"+"\n\n")
    f.write(f"update_compile_order -fileset sources_1" + "\n\n")
    f.write(f"ipx::package_project -root_dir {ip_loc} -vendor user.org -library user -taxonomy /UserIP"+ "\n\n")

    img_in_intf = """
ipx::add_bus_interface img_in [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:axis_rtl:1.0 [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:axis:1.0 [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]
ipx::add_port_map TREADY [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]
set_property physical_name din_ready [ipx::get_port_maps TREADY -of_objects [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]]
ipx::add_port_map TVALID [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]
set_property physical_name din_valid [ipx::get_port_maps TVALID -of_objects [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]]
ipx::add_port_map TDATA [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]
set_property physical_name din_data [ipx::get_port_maps TDATA -of_objects [ipx::get_bus_interfaces img_in -of_objects [ipx::current_core]]]
ipx::associate_bus_interfaces -busif img_in -clock clk [ipx::current_core]
"""
    detected_addr_intf = """
ipx::add_bus_interface detected_addr [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:axis_rtl:1.0 [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:axis:1.0 [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]
ipx::add_port_map TDATA [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]
set_property physical_name detected_addr_data [ipx::get_port_maps TDATA -of_objects [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]]
ipx::add_port_map TVALID [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]
set_property physical_name detected_addr_valid [ipx::get_port_maps TVALID -of_objects [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]]
ipx::add_port_map TREADY [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]
set_property physical_name detected_addr_ready [ipx::get_port_maps TREADY -of_objects [ipx::get_bus_interfaces detected_addr -of_objects [ipx::current_core]]]
ipx::associate_bus_interfaces -busif detected_addr -clock clk [ipx::current_core]
"""

    irq_intf = """
ipx::add_bus_interface irq [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:axis_rtl:1.0 [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:axis:1.0 [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]
ipx::add_port_map TREADY [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]
set_property physical_name interrupt_ready [ipx::get_port_maps TREADY -of_objects [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]]
ipx::add_port_map TVALID [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]
set_property physical_name interrupt_valid [ipx::get_port_maps TVALID -of_objects [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]]
ipx::add_port_map TDATA [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]
set_property physical_name interrupt_data [ipx::get_port_maps TDATA -of_objects [ipx::get_bus_interfaces irq -of_objects [ipx::current_core]]]
ipx::associate_bus_interfaces -busif irq -clock clk [ipx::current_core]
"""

    f.write(f"{img_in_intf}"+"\n\n")
    f.write(f"{detected_addr_intf}"+"\n\n")
    f.write(f"{irq_intf}"+"\n\n")

    ## RST active high
    f.write(f"ipx::add_bus_parameter POLARITY [ipx::get_bus_interfaces rst -of_objects [ipx::current_core]]"+"\n\n")

    pkg_ip = f"""
set_property core_revision 2 [ipx::current_core]
ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::save_core [ipx::current_core]
set_property  ip_repo_paths  {ip_loc} [current_project]
update_ip_catalog
"""

    f.write(f"{pkg_ip}"+"\n\n")
