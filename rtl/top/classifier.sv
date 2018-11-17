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
   logic signed [35:0]  rect_sum_next, rect_sum_reg;
   logic                rect_sum_valid_next, rect_sum_valid_reg;
   logic                weight_valid, weight_ready;
   logic signed [2:0]   weight_data;
   logic signed [2:0]   weight_data_reg, weight_data_next;
   logic [2:0]          rect_cnt_reg, rect_cnt_next;

   logic signed [36:0]  weighted_sum;
   logic signed [38:0]  accum_weighted_sum_next, accum_weighted_sum_reg;
   logic                accum_weighted_sum_valid;

   assign dot_cnt_next = (dot_cnt_reg < 4) ? dot_cnt_reg + 1 : 1;
   assign sum_valid = rect_sum_valid_reg;
   assign sum_data = rect_sum_reg;

   assign accum_weighted_sum_valid = (rect_cnt_reg == 3) & rect_sum_valid_reg;

   assign weighted_sum = rect_sum_reg * weight_data_reg*4096;

   always_comb
     begin
        if(rect_sum_valid_reg && !accum_weighted_sum_valid)
             accum_weighted_sum_next = accum_weighted_sum_reg + weighted_sum;
        else if(accum_weighted_sum_valid)
          accum_weighted_sum_next = 0;
     end

   always_comb
     begin
        rect_cnt_next = rect_cnt_reg;

        if(rect_sum_valid_reg)
          rect_cnt_next = rect_cnt_reg + 1;
        else if(rect_cnt_reg == 4)
          rect_cnt_next = 1;
     end

   always_comb
     begin
        rect_sum_valid_next = 0;
        rect_sum_next = rect_sum_reg;
        weight_data_next = weight_data_reg;
        weight_ready = 1;   // DANGER !!!!!!!!!!!!!

        case(dot_cnt_reg)
          1: begin
             weight_data_next = 0;
             rect_sum_next = din_data;
          end
          2: begin
             weight_data_next = weight_data;
             rect_sum_next = rect_sum_reg - din_data;
          end
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
           weight_data_reg <= 0;
           accum_weighted_sum_reg <= 0;
           rect_cnt_reg <= 1;
          end else if (din_valid) begin
             rect_cnt_reg <= rect_cnt_next;
             accum_weighted_sum_reg <= accum_weighted_sum_next;
             weight_data_reg <= weight_data_next;
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
         .addr_eot(addr_eot),
         .weight_valid(weight_valid),
         .weight_ready(weight_ready),
         .weight(weight_data)
         );
endmodule: classifier
