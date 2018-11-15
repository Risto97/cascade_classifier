module rects_mem
  #(
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

    output              addr_valid,
    input               addr_ready,
    output [W_ADDR-1:0] addr_data,
    output [1:0]        addr_eot
    );

   logic                rect0_addr_valid, rect0_addr_ready;
   logic                rect1_addr_valid, rect1_addr_ready;
   logic                rect2_addr_valid, rect2_addr_ready;
   logic [W_ADDR-1:0]   rect0_addr_data, rect1_addr_data, rect2_addr_data;
   logic [1:0]          rect0_eot, rect1_eot, rect2_eot;

   logic [2:0]          rect_cnt_next, rect_cnt_reg;
   logic                addr_valid_s, addr_ready_s;
   logic [W_ADDR-1:0]   addr_data_s;
   logic [1:0]          addr_eot_s;

   assign addr_data = addr_data_s;
   assign addr_eot = addr_eot_s;
   assign addr_valid = addr_valid_s;
   assign addr_ready_s = addr_ready;

   assign rect_cnt_next = (rect_cnt_reg < 2) ? rect_cnt_reg + 1 : 0;

   always_comb
     begin
        rect0_addr_ready = 0;
        rect1_addr_ready = 0;
        rect2_addr_ready = 0;
        addr_valid_s = 0;
        addr_data_s = 0;
        addr_eot_s = 0;

        case(rect_cnt_reg)
          0: begin
             rect0_addr_ready = addr_ready;
             addr_data_s = rect0_addr_data;
             addr_valid_s = rect0_addr_valid;
             addr_eot_s = rect0_addr_eot;
          end
          1: begin
             rect1_addr_ready = addr_ready;
             addr_data_s = rect1_addr_data;
             addr_valid_s = rect1_addr_valid;
             addr_eot_s = rect1_addr_eot;
          end
          2: begin
             rect2_addr_ready = addr_ready;
             addr_data_s = rect2_addr_data;
             addr_valid_s = rect2_addr_valid;
             addr_eot_s = rect2_addr_eot;
          end
        endcase
     end

   always_ff @(posedge clk)
     begin
        if (rst) begin
           rect_cnt_reg <= 0;
        end else if(addr_eot_s[0]) begin
           rect_cnt_reg <= rect_cnt_next;
        end
     end

   rect_addr_gen
     #(
       .W_ADDR(W_ADDR),
       .FEATURE_WIDTH(FEATURE_WIDTH),
       .FEATURE_HEIGHT(FEATURE_HEIGHT),
       .FEATURE_NUM(FEATURE_NUM),
       .RECT_NUM(0)
       )
   rect0(
         .clk(clk),
         .rst(rst),
         .addr_valid(rect0_addr_valid),
         .addr_ready(rect0_addr_ready),
         .addr_data(rect0_addr_data),
         .addr_eot(rect0_addr_eot)
         );

   rect_addr_gen
     #(
       .W_ADDR(W_ADDR),
       .FEATURE_WIDTH(FEATURE_WIDTH),
       .FEATURE_HEIGHT(FEATURE_HEIGHT),
       .FEATURE_NUM(FEATURE_NUM),
       .RECT_NUM(1)
       )
   rect1(
         .clk(clk),
         .rst(rst),
         .addr_valid(rect1_addr_valid),
         .addr_ready(rect1_addr_ready),
         .addr_data(rect1_addr_data),
         .addr_eot(rect1_addr_eot)
         );

   rect_addr_gen
     #(
       .W_ADDR(W_ADDR),
       .FEATURE_WIDTH(FEATURE_WIDTH),
       .FEATURE_HEIGHT(FEATURE_HEIGHT),
       .FEATURE_NUM(FEATURE_NUM),
       .RECT_NUM(2)
       )
   rect2(
         .clk(clk),
         .rst(rst),
         .addr_valid(rect2_addr_valid),
         .addr_ready(rect2_addr_ready),
         .addr_data(rect2_addr_data),
         .addr_eot(rect2_addr_eot)
         );

endmodule: rects_mem
