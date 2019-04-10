module ii_gen
  #(
    parameter W_DATA = 8,
    parameter W_DATA_ACCUM = 26,
    parameter FEATURE_WIDTH = 24)
   (
    input                     clk,
    input                     rst,

    input                     din_valid,
    output                    din_ready,
    input [W_DATA-1:0]        din_data,
    input [1:0]               din_eot,

    output                    dout_valid,
    input                     dout_ready,
    output [W_DATA_ACCUM-1:0] dout_data,
    output [1:0]              dout_eot
    );

   logic                      accum_dout_valid;
   logic                      accum_dout_ready;
   logic [1:0]                accum_dout_eot;
   logic [W_DATA_ACCUM-1:0]   accum_dout_data;

   logic                      add_dout_valid;
   logic                      add_dout_ready;
   logic [1:0]                add_dout_eot;
   logic [W_DATA_ACCUM-1:0]   add_dout_data;

   logic                      add_din2_valid;
   logic                      add_din2_ready;
   logic [W_DATA_ACCUM-1:0]   add_din2_data;

   logic                      fifo_din_valid;
   logic                      fifo_din_ready;
   logic [W_DATA_ACCUM-1:0]   fifo_din_data;
   logic [1:0]                fifo_din_eot;


   accum #(.W_DATA_IN(W_DATA),
           .W_DATA_OUT(W_DATA_ACCUM))
   accum_i (
            .clk(clk),
            .rst(rst),
            .din_valid(din_valid),
            .din_ready(din_ready),
            .din_data(din_data),
            .din_eot(din_eot),
            .dout_valid(accum_dout_valid),
            .dout_ready(accum_dout_ready),
            .dout_data(accum_dout_data),
            .dout_eot(accum_dout_eot)
            );


   add #(.W_DATA(W_DATA_ACCUM))
   add_i(
         .clk(clk),
         .rst(rst),
         .din1_valid(accum_dout_valid),
         .din1_ready(accum_dout_ready),
         .din1_data(accum_dout_data),
         .din1_eot(accum_dout_eot),
         .din2_valid(add_din2_valid),
         .din2_ready(add_din2_ready),
         .din2_data(add_din2_data),
         .dout_valid(add_dout_valid),
         .dout_ready(add_dout_ready),
         .dout_data(add_dout_data),
         .dout_eot(add_dout_eot)
         );

   broadcast #(.W_DATA(W_DATA_ACCUM))
   bc(
      .clk(clk),
      .rst(rst),
      .din_valid(add_dout_valid),
      .din_ready(add_dout_ready),
      .din_data(add_dout_data),
      .din_eot(add_dout_eot),
      .dout1_valid(dout_valid),
      .dout1_ready(dout_ready),
      .dout1_data(dout_data),
      .dout1_eot(dout_eot),
      .dout2_valid(fifo_din_valid),
      .dout2_ready(fifo_din_ready),
      .dout2_data(fifo_din_data),
      .dout2_eot(fifo_din_eot)
      );

   fifo #(.W_DATA(W_DATA_ACCUM),
          .DEPTH(32),
          .PRELOAD(FEATURE_WIDTH))
   fifo_i(
          .clk(clk),
          .rst(rst),
          .din_valid(fifo_din_valid),
          .din_ready(fifo_din_ready),
          .din_data(fifo_din_data),
          .din_eot(fifo_din_eot),
          .dout_data(add_din2_data),
          .dout_valid(add_din2_valid),
          .dout_ready(add_din2_ready)
          );

endmodule : ii_gen
