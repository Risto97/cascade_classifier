#include "Vtop.h"
// #include "Vtop_top.h"
#include "verilated.h"
#include "verilated_vcd_c.h"
#include <math.h>
#include <iostream>
#include "img.hpp"

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
  int img_done = 0;
  int x = 0;
  int y = 0;

  top->img_eot = 0;

  for(i=0; i<900000; i++){
    top->rst = (i<2);

    for (clk=0; clk<2; clk++){
      if(i>3 && clk == 1){
        top->detect_pos_ready = 1;

        if(img_done == 1){
          top->img_eot = 0;
        }
        if(img_done == 0){
          top->img_valid = 1;
          top->img_data = img[y][x];
          x++;
          if(x == WIDTH){
            x = 0;
            y++;
            if(y == HEIGHT){
              y = 0;
              top->img_eot = 1;
              img_done = 1;
            }
          }
        }
      }
      tfp->dump ((2*i+clk)*2.5);
      top->clk = !top->clk;
      top->eval();
    }
    if(Verilated::gotFinish()) exit(0);
  }
  tfp->close();
  exit(0);
}
