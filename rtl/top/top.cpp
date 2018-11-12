#include "Vtop.h"
#include "verilated.h"
#include "verilated_vcd_c.h"
#include <math.h>

#define IMG_WIDTH 41
#define IMG_HEIGHT 50

#define FEATURE_WIDTH 24
#define FEATURE_HEIGHT 24

int main(int argc, char **argv, char **env){
  int i;
  int clk;


  Verilated::commandArgs(argc, argv);

  Vtop* top = new Vtop;

  Verilated::traceEverOn(true);
  VerilatedVcdC* tfp = new VerilatedVcdC;
  top->trace (tfp, 99);
  tfp->open ("top.vcd");

  top->clk = 1;
  top-> rst = 1;
  int cnt = 0;

  for(i=0; i<10000; i++){
    top->rst = (i<2);

    for (clk=0; clk<2; clk++){
      if(i>3 && clk == 1){

        top->ii_dout_ready = 0;
        top->stddev_ready = 1;

        if(top->ii_addr_ready){
          top->ii_addr_valid = 1;
          top->ii_addr_data = cnt;
          cnt++;
          if(cnt == 50)
            top->ii_dout_ready = 1;
        }
      }
      tfp->dump ((2*i+clk)*5);
      top->clk = !top->clk;
      top->eval();
    }
    if(Verilated::gotFinish()) exit(0);
  }
  tfp->close();
  exit(0);
}
