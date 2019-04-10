//(* use_dsp = "yes" *)
module add
  #(
    parameter W_DATA = 32)
   (
    input               clk,
    input               rst,

    input               din1_valid,
    output              din1_ready,
    input [W_DATA-1:0]  din1_data,
    input [1:0]         din1_eot,

    input               din2_valid,
    output              din2_ready,
    input [W_DATA-1:0]  din2_data,

    output              dout_valid,
    input               dout_ready,
    output [W_DATA-1:0] dout_data,
    output [1:0]        dout_eot
    );

   logic                valid_inputs;


   assign valid_inputs = din1_valid && din2_valid;

   assign din1_ready = dout_valid && dout_ready;
   assign din2_ready = dout_valid && dout_ready;

   assign dout_data = din1_data + din2_data;
   assign dout_valid = valid_inputs;
   assign dout_eot = din1_eot;




endmodule : add
