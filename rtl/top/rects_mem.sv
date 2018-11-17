module rects_mem
  #(
    parameter W_ADDR = 10,
    parameter FEATURE_WIDTH = 25,
    parameter FEATURE_HEIGHT = 25,
    parameter FEATURE_NUM = 2913,
    localparam W_ADDR_RECT = $clog2(FEATURE_NUM*4),
    localparam W_ADDR_FEAT = $clog2(FEATURE_NUM),
    localparam W_RECT = $clog2(FEATURE_WIDTH) // should be max(FEATURE_WIDTH, FEATURE_HEIGHT)
    )
   (
    input               clk,
    input               rst,

    output              addr_valid,
    input               addr_ready,
    output [W_ADDR-1:0] addr_data,
    output [1:0]        addr_eot,

    output              weight_valid,
    input               weight_ready,
    output [2:0]        weight
    );

   logic                rect0_addr_valid, rect0_addr_ready;
   logic                rect1_addr_valid, rect1_addr_ready;
   logic                rect2_addr_valid, rect2_addr_ready;
   logic [W_ADDR-1:0]   rect0_addr_data, rect1_addr_data, rect2_addr_data;
   logic [1:0]          rect0_eot, rect1_eot, rect2_eot;

   logic                weight0_addr_valid, weight1_addr_valid, weight2_addr_valid;
   logic                weight0_addr_ready, weight1_addr_ready, weight2_addr_ready;
   logic [11:0]         weight0_addr_data, weight1_addr_data, weight2_addr_data;

   logic                weight0_data_valid, weight1_data_valid, weight2_data_valid;
   logic                weight0_data_ready, weight1_data_ready, weight2_data_ready;
   logic [2:0]          weight0_data, weight1_data, weight2_data;

   logic                weight_data_valid, weight_data_ready;
   logic [2:0]          weight_data;

   logic [2:0]          rect_cnt_next, rect_cnt_reg;
   logic                addr_valid_s, addr_ready_s;
   logic [W_ADDR-1:0]   addr_data_s;
   logic [1:0]          addr_eot_s;

   logic [W_ADDR_FEAT-1:0] feature_cnt_reg, feature_cnt_next;

   assign addr_data = addr_data_s;
   assign addr_eot = addr_eot_s;
   assign addr_valid = addr_valid_s;
   assign addr_ready_s = addr_ready;

   assign rect_cnt_next = (rect_cnt_reg < 2) ? rect_cnt_reg + 1 : 0;
   assign feature_cnt_next = (rect_cnt_reg == 2 && addr_eot_s) ? feature_cnt_reg + 1: feature_cnt_reg;

   assign weight_data_ready = weight_ready;
   assign weight = weight_data;
   assign weight_valid = weight_data_valid;

   always_comb
     begin
        rect0_addr_ready = 0;
        rect1_addr_ready = 0;
        rect2_addr_ready = 0;
        addr_valid_s = 0;
        addr_data_s = 0;
        addr_eot_s = 0;
        weight0_data_ready = weight_data_ready;
        weight1_data_ready = weight_data_ready;
        weight2_data_ready = weight_data_ready;
        weight0_addr_valid = 0;
        weight1_addr_valid = 0;
        weight2_addr_valid = 0;
        weight0_addr_data = feature_cnt_reg;
        weight1_addr_data = feature_cnt_reg;
        weight2_addr_data = feature_cnt_reg;
        weight_data = 0;
        weight_data_valid = 0;

        case(rect_cnt_reg)
          0: begin
             weight0_addr_valid = 1;
             weight_data = weight0_data;
             weight_data_valid = weight0_data_valid;
             rect0_addr_ready = addr_ready;
             addr_data_s = rect0_addr_data;
             addr_valid_s = rect0_addr_valid;
             addr_eot_s = rect0_addr_eot;
          end
          1: begin
             weight_data_valid = weight1_data_valid;
             weight1_addr_valid = 1;
             weight_data = weight1_data;
             rect1_addr_ready = addr_ready;
             addr_data_s = rect1_addr_data;
             addr_valid_s = rect1_addr_valid;
             addr_eot_s = rect1_addr_eot;
          end
          2: begin
             weight_data_valid = weight2_data_valid;
             weight_data = weight2_data;
             weight2_addr_valid = 1;
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
           feature_cnt_reg <= 0;
           rect_cnt_reg <= 0;
        end else if(addr_eot_s[0]) begin
           feature_cnt_reg <= feature_cnt_next;
           rect_cnt_reg <= rect_cnt_next;
        end
     end


   weight
     #(
       .W_DATA(3),
       .W_ADDR(12),
       .WEIGHT_NUM(0)
       )
   weight0(
           .clk(clk),
           .rst(rst),
           .addr1_valid(weight0_addr_valid),
           .addr1_ready(weight0_addr_ready),
           .addr1_data(weight0_addr_data),
           .data1_valid(weight0_data_valid),
           .data1_ready(weight0_data_ready),
           .data1(weight0_data)
           );
   weight
     #(
       .W_DATA(3),
       .W_ADDR(12),
       .WEIGHT_NUM(1)
       )
   weight1(
           .clk(clk),
           .rst(rst),
           .addr1_valid(weight1_addr_valid),
           .addr1_ready(weight1_addr_ready),
           .addr1_data(weight1_addr_data),
           .data1_valid(weight1_data_valid),
           .data1_ready(weight1_data_ready),
           .data1(weight1_data)
           );

   weight
     #(
       .W_DATA(3),
       .W_ADDR(12),
       .WEIGHT_NUM(2)
       )
   weight2(
           .clk(clk),
           .rst(rst),
           .addr1_valid(weight2_addr_valid),
           .addr1_ready(weight2_addr_ready),
           .addr1_data(weight2_addr_data),
           .data1_valid(weight2_data_valid),
           .data1_ready(weight2_data_ready),
           .data1(weight2_data)
           );

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
