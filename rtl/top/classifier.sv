module classifier
  #(
    parameter W_DATA = 18,
    parameter W_ADDR = 10,
    parameter FEATURE_WIDTH = 25,
    parameter FEATURE_HEIGHT = 25,
    parameter FEATURE_NUM = 2913,
    localparam W_ADDR_RECT = $clog2(FEATURE_NUM*4),
    localparam W_RECT = $clog2(FEATURE_WIDTH) // should be max(FEATURE_WIDTH, FEATURE_HEIGHT)
    )
   (
    input               clk,
    input               rst,

    input               din_valid,
    output              din_ready,
    input [W_DATA-1:0]  din_data,

    output              addr_valid,
    input               addr_ready,
    output [W_ADDR-1:0] addr_data,

    output              sum_valid,
    input               sum_ready,
    output [W_DATA:0]   sum_data
    );
   logic                rect0_addr_ready, rect0_addr_valid, rect0_addr_eot;
   logic [W_ADDR-1:0]   rect0_addr_data;

   logic [2:0]          dot_cnt_reg, dot_cnt_next;
   logic [W_DATA:0]     rect_sum_next, rect_sum_reg;
   logic                rect_sum_valid_next, rect_sum_valid_reg;

   assign dot_cnt_next = (dot_cnt_reg < 4) ? dot_cnt_reg + 1 : 1;
   assign sum_valid = rect_sum_valid_reg;
   assign sum_data = rect_sum_reg;

   always_comb
     begin
        rect_sum_valid_next = 0;
        rect_sum_next = rect_sum_reg;

        case(dot_cnt_reg)
          1: rect_sum_next = din_data;
          2: rect_sum_next = rect_sum_reg - din_data;
          3: rect_sum_next = rect_sum_reg + din_data;
          4: begin
             rect_sum_valid_next = 1;
             rect_sum_next = rect_sum_reg - din_data;
          end
        endcase
     end

   always_ff @(posedge clk)
     begin
        if(rst) begin
           dot_cnt_reg <= 1;
           rect_sum_reg <= 0;
           rect_sum_valid_reg <= 0;
          end else if (din_valid) begin
             rect_sum_valid_reg <= rect_sum_valid_next;
             rect_sum_reg <= rect_sum_next;
             dot_cnt_reg <= dot_cnt_next;
          end
     end

   rects_mem
     #(
       .W_ADDR(W_ADDR),
       .FEATURE_WIDTH(FEATURE_WIDTH),
       .FEATURE_HEIGHT(FEATURE_HEIGHT),
       .FEATURE_NUM(FEATURE_NUM)
        )
   rects(
         .clk(clk),
         .rst(rst),
         .addr_valid(addr_valid),
         .addr_ready(addr_ready),
         .addr_data(addr_data),
         .addr_eot(addr_eot)
         );
endmodule: classifier
