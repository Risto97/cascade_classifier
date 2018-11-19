#cleanup
rm -rf obj_dir
rm -f top.vcd

verilator -Wall --cc --trace top.sv rom/*  --exe top.cpp

make -j -C obj_dir/ -f Vtop.mk Vtop

obj_dir/Vtop

gtkwave top.vcd top.sav &
