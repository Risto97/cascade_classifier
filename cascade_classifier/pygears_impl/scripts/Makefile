ip:
	python create_ip.py
	vivado -mode batch -source ip_pack.tcl
	rm -rf *.log *.jou .Xil/

run_sim:
	gearbox run_sim.py

clean:
	rm -rf *.log *.jou .Xil/
