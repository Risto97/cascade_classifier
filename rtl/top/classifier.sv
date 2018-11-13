module classifier
  #(
    parameter W_DATA = 18,
    parameter W_ADDR = 10
    )
   (
    input               clk,
    input               rst,

    input               din_valid,
    output              din_ready,
    input [W_DATA-1:0]  din_data,

    output              addr_valid,
    input               addr_ready,
    output [W_ADDR-1:0] addr_data
    );

   logic [11:0]         rect0_cnt_next, rect0_cnt_reg;
   logic [1:0]          rect_data_cnt_reg, rect_data_cnt_next;
   logic                rect0_addr_valid, rect0_addr_ready;
   logic                rect0_data_valid, rect0_data_ready;
   logic [4:0]          rect0_data;
   logic [13:0]         rect0_addr_data;


   assign rect0_cnt_next = (rect_data_cnt_reg == 3) ?
                           rect0_cnt_reg+1 :
                           rect0_cnt_reg;

   assign rect_data_cnt_next = rect_data_cnt_reg + 1;


   always_ff @(posedge clk)
     if(rst)
       rect0_cnt_reg <= 0;
     else
       rect0_cnt_reg <= rect0_cnt_next;

   always_ff @(posedge clk)
     if(rst)
       rect_data_cnt_reg <= 0;
     else
       rect_data_cnt_reg <= rect_data_cnt_next;

   rect0 #(.W_DATA(5),
           .W_ADDR(14))
   rect0_mem(
             .clk(clk),
             .rst(rst),
             .addr1_valid(rect0_addr_valid),
             .addr1_ready(rect0_addr_ready),
             .addr1_data(rect0_addr_data),
             .data1_valid(rect0_data_valid),
             .data1_ready(rect0_data_ready),
             .data1(rect0_data)
             );

endmodule: classifier
