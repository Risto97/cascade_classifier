default:
	python dump_rtl_verilog.py
sim: default
	./verilate.sh
	obj_dir/Vtop
run: sim
	gtkwave top.vcd top.sav &

ip:default
	python create_ip.py
	vivado -mode batch -source ip_pack.tcl
	rm -rf *.log *.jou .Xil/

ip_synth:ip
	vivado -mode batch -source run_synth.tcl
	rm -rf *.log *.jou .Xil/

clean:
	rm -rf top/params.sv img.hpp top/rom/*
	rm -rf obj_dir
	rm -f top.vcd
