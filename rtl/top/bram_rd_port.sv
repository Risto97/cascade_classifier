module bram_rd_port
  #(
    parameter W_DATA = 8,
    parameter W_ADDR = 12
    )
   (
    input               clk,
    input               rst,

    input               addr1_valid,
    output              addr1_ready,
    input [W_ADDR-1:0]  addr1_data,

    output              data1_valid,
    input               data1_ready,
    output [W_DATA-1:0] data1,

    output              en1,
    output [W_ADDR-1:0] addr1,
    input [W_DATA-1:0]  data1_i
    );

   logic                data1_valid_reg;

   assign en1 = addr1_valid & data1_ready;
   assign addr1 = addr1_data;
   assign addr1_ready = data1_ready;
   assign data1_valid = data1_valid_reg;

   assign data1 = data1_i;

   always_ff @(posedge clk)begin
      if(rst)
         data1_valid_reg <= 1'b0;
      else
        data1_valid_reg <= addr1_valid;
   end

endmodule: bram_rd_port
