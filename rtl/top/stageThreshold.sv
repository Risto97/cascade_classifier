module stageThreshold
  #(
    parameter W_DATA = 11,
    parameter W_ADDR = 5
    )
   (
    input                      clk,
    input                      rst,

    input                      addr1_valid,
    output                     addr1_ready,
    input [W_ADDR-1:0]         addr1_data,

    output                     data1_valid,
    input                      data1_ready,
    output signed [W_DATA-1:0] data1
    );

   logic                       ena;
   logic [W_ADDR-1:0]          addra;
   logic signed [W_DATA-1:0]   doa;

   logic                       dreg_valid, dreg_ready;
   logic signed [W_DATA-1:0]   dreg_data;

   dreg #(.W_DATA(W_DATA))
   dreg_i(
          .clk(clk),
          .rst(rst),
          .din_valid(dreg_valid),
          .din_ready(dreg_ready),
          .din_data(dreg_data),
          .dout_valid(data1_valid),
          .dout_ready(data1_ready),
          .dout_data(data1)
          );


   bram_rd_port #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
   rd_port (
            .clk(clk),
            .rst(rst),
            .addr1_valid(addr1_valid),
            .addr1_ready(addr1_ready),
            .addr1_data(addr1_data),
            .data1_valid(dreg_valid),
            .data1_ready(dreg_ready),
            .data1(dreg_data),
            .ena(ena),
            .addra(addra),
            .doa(doa)
            );

   stageThreshold_rom #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
   stageThreshold_i(
                    .clk(clk),
                    .rst(rst),
                    .ena(ena),
                    .addra(addra),
                    .doa(doa)
                    );

endmodule: stageThreshold
