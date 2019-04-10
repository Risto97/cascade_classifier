default:
	python dump_rtl_verilog.py
sim: default
	./verilate.sh
	obj_dir/Vtop
run: sim
	gtkwave top.vcd top.sav &

clean:
	rm -rf top/params.sv img.hpp top/rom/*
	rm -rf obj_dir
	rm -f top.vcd
