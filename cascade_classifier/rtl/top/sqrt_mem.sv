module sqrt_mem
  #(
    parameter W_DATA = 16,
    parameter W_ADDR = 8
    )
   (
    input               clk,
    input               rst,

    input               addr1_valid,
    output              addr1_ready,
    input [W_ADDR-1:0]  addr1_data,

    output              data1_valid,
    input               data1_ready,
    output [W_DATA-1:0] data1
    );

   logic                ena;
   logic [W_ADDR-1:0]   addra;
   logic [W_DATA-1:0]   doa;

   bram_rd_port #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
   rd_port (
            .clk(clk),
            .rst(rst),
            .addr1_valid(addr1_valid),
            .addr1_ready(addr1_ready),
            .addr1_data(addr1_data),
            .data1_valid(data1_valid),
            .data1_ready(data1_ready),
            .data1(data1),
            .ena(ena),
            .addra(addra),
            .doa(doa)
            );

   sqrt_rom #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
   sqrt_rom_i(
              .clk(clk),
              .rst(rst),
              .en1(ena),
              .addr1(addra),
              .data1(doa)
              );

endmodule: sqrt_mem
