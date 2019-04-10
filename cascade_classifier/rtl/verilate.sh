verilator -Wall --cc --trace top/top.sv -Itop -Itop/rom --exe top.cpp
make -j -C obj_dir/ -f Vtop.mk Vtop
