(* use_dsp = "yes" *)
module ii_sii_gen
  #(
    parameter W_DATA = 8,
    parameter FEATURE_WIDTH = 24)
   (
    input              clk,
    input              rst,

    input              din_valid,
    output             din_ready,
    input [W_DATA-1:0] din_data,
    input [1:0]        din_eot,

    output             ii_valid,
    input              ii_ready,
    output [17:0]      ii_data,
    output [1:0]       ii_eot,

    output             sii_valid,
    input              sii_ready,
    output [25:0]      sii_data,
    output [1:0]       sii_eot
    );

   logic [16:0]        squared_data;

   logic [W_DATA-1:0]  ii_din_data;
   logic               ii_din_valid;
   logic               ii_din_ready;
   logic [1:0]         ii_din_eot;

   logic               sii_din_valid;
   logic               sii_din_ready;
   logic [1:0]         sii_din_eot;

   logic [W_DATA-1:0]  dout2_bc_data;

   logic [W_DATA-1:0]  din_data_reg;
   logic               din_valid_reg;
   logic               din_ready_reg;
   logic [1:0]         din_eot_reg;


   assign squared_data = dout2_bc_data * dout2_bc_data;

   // dreg #(.W_DATA(8))
   // dreg_i(
   //        .clk(clk),
   //        .rst(rst),
   //        .din_valid(din_valid),
   //        .din_ready(din_ready),
   //        .din_data(din_data),
   //        .din_eot(din_eot),
   //        .dout_valid(din_valid_reg),
   //        .dout_ready(din_ready_reg),
   //        .dout_data(din_data_reg),
   //        .dout_eot(din_eot_reg)
   //        );

   broadcast #(.W_DATA(W_DATA))
   bc(
      .clk(clk),
      .rst(rst),
      .din_valid(din_valid),
      .din_ready(din_ready),
      .din_data(din_data),
      .din_eot(din_eot),
      .dout1_valid(ii_din_valid),
      .dout1_ready(ii_din_ready),
      .dout1_data(ii_din_data),
      .dout1_eot(ii_din_eot),
      .dout2_valid(sii_din_valid),
      .dout2_ready(sii_din_ready),
      .dout2_data(dout2_bc_data),
      .dout2_eot(sii_din_eot)
      );

   ii_gen #(.W_DATA(16),
            .W_DATA_ACCUM(26),
            .FEATURE_WIDTH(FEATURE_WIDTH))
   sii_gen (
            .clk(clk),
            .rst(rst),
            .din_valid(sii_din_valid),
            .din_ready(sii_din_ready),
            .din_data(squared_data),
            .din_eot(sii_din_eot),
            .dout_valid(sii_valid),
            .dout_ready(sii_ready),
            .dout_data(sii_data),
            .dout_eot(sii_eot)
            );

   ii_gen #(.W_DATA(8),
            .W_DATA_ACCUM(18),
            .FEATURE_WIDTH(FEATURE_WIDTH))
   ii_gen_i (
             .clk(clk),
             .rst(rst),
             .din_valid(ii_din_valid),
             .din_ready(ii_din_ready),
             .din_data(ii_din_data),
             .din_eot(ii_din_eot),
             .dout_valid(ii_valid),
             .dout_ready(ii_ready),
             .dout_data(ii_data),
             .dout_eot(ii_eot)
             );


endmodule : ii_sii_gen
