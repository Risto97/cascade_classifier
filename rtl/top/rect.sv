module rect
  #(
    parameter W_DATA = 20,
    parameter W_ADDR = 14,
    parameter RECT_NUM = 0
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

   generate
      if(RECT_NUM == 0)
        rect0_rom #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
        rect_i(
               .clk(clk),
               .rst(rst),
               .ena(ena),
               .addra(addra),
               .doa(doa)
               );
      else if(RECT_NUM == 1)
        rect1_rom #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
        rect_i(
               .clk(clk),
               .rst(rst),
               .ena(ena),
               .addra(addra),
               .doa(doa)
               );
      else if(RECT_NUM == 2)
        rect2_rom #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
        rect_i(
               .clk(clk),
               .rst(rst),
               .ena(ena),
               .addra(addra),
               .doa(doa)
               );
   endgenerate

endmodule: rect
