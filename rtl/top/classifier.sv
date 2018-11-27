module classifier
  #(
    parameter W_DATA = 18,
    parameter W_ADDR = 10,
    parameter FEATURE_WIDTH = 25,
    parameter FEATURE_HEIGHT = 25,
    parameter FEATURE_NUM = 2913,
    parameter STAGE_NUM = 25,
    parameter W_FEATURE_THRESHOLD = 13,
    parameter W_STDDEV = 36,
    parameter W_LEAF = 14,
    parameter MAX_WEAKCOUNT = 211,
    parameter W_WEIGHT = 3,
    parameter W_STAGE_THRESHOLD = 11,
    localparam W_RECT_SUM = $clog2(4*2**W_DATA) + W_WEIGHT + $clog2(4096),
    localparam W_ADDR_STAGE = $clog2(STAGE_NUM),
    localparam W_FEATURE_ACCUM = $clog2(MAX_WEAKCOUNT) + W_LEAF,
    localparam W_ADDR_RECT = $clog2(FEATURE_NUM),
    localparam W_ADDR_FEAT = $clog2(FEATURE_NUM),
    localparam W_RECT = $clog2(FEATURE_WIDTH) // should be max(FEATURE_WIDTH, FEATURE_HEIGHT)
    )
   (
    input                clk,
    input                rst,

    input                din_valid,
    output               din_ready,
    input [W_DATA-1:0]   din0_data,
    input [W_DATA-1:0]   din1_data,
    input [W_DATA-1:0]   din2_data,

    output               addr_valid,
    input                addr_ready,
    output [W_ADDR-1:0]  addr0_data,
    output [W_ADDR-1:0]  addr1_data,
    output [W_ADDR-1:0]  addr2_data,

    output               result_valid,
    input                result_ready,
    output               result_data,

    input                stddev_valid,
    output               stddev_ready,
    input [W_STDDEV-1:0] stddev_data
    );
   logic                 rects_addr_valid, rects_addr_ready;
   logic [W_ADDR-1:0]    rect0_addr, rect1_addr, rect2_addr;
   logic [1:0]           rect_addr_eot;

   logic                 weights_valid, weights_ready;
   logic signed [W_WEIGHT-1:0] weight [2:0];
   logic [2:0]                 weight_ready;
   assign weights_ready = &weight_ready;

   logic                       internal_rst, local_rst;

   assign local_rst = internal_rst | rst;

   assign addr0_data = rect0_addr;
   assign addr1_data = rect1_addr;
   assign addr2_data = rect2_addr;
   assign addr_valid = rects_addr_valid;

   assign rects_addr_ready = addr_ready;

   logic [W_DATA-1:0]    din_data [2:0];
   assign din_data[0] = din0_data;
   assign din_data[1] = din1_data;
   assign din_data[2] = din2_data;

   logic [2:0]           rect_sum_din_ready;
   logic [2:0]           rect_sum_valid, rect_sum_eot;
   logic signed [W_RECT_SUM-1:0] rect_sum [2:0];
   logic signed [W_RECT_SUM+1:0] all_rect_sum_reg, all_rect_sum_next;
   logic                         all_rect_sum_valid_reg, all_rect_sum_valid_next;
   logic                         all_rect_sum_ready;

   assign all_rect_sum_next = (&rect_sum_valid) ? rect_sum[0] + rect_sum[1] + rect_sum[2] : all_rect_sum_reg;
   assign all_rect_sum_valid_next = &rect_sum_valid;

   always_ff @(posedge clk) begin
      if(local_rst) begin
         all_rect_sum_reg <= 0;
         all_rect_sum_valid_reg <= 0;
      end
      else begin
         all_rect_sum_reg <= all_rect_sum_next;
         all_rect_sum_valid_reg <= all_rect_sum_valid_next;
      end
   end

   assign din_ready = &rect_sum_din_ready;


   logic leaf_val_valid, leaf_val_ready, leaf_eot;
   logic [W_LEAF-1:0] leaf_val;

   feature_val
     #(
       .W_DIN(W_RECT_SUM+2),
       .W_DOUT(W_LEAF),
       .W_STDDEV(W_STDDEV),
       .FEATURE_NUM(FEATURE_NUM),
       .W_LEAF(W_LEAF),
       .W_FEATURE_THRESHOLD(W_FEATURE_THRESHOLD)
       )
   feature_val_i(
                 .clk(clk),
                 .rst(local_rst),
                 .din_valid(all_rect_sum_valid_reg),
                 .din_ready(all_rect_sum_ready),
                 .din_data(all_rect_sum_reg),
                 .stddev_valid(stddev_valid),
                 .stddev_ready(stddev_ready),
                 .stddev(stddev_data),
                 .dout_valid(leaf_val_valid),
                 .dout_ready(leaf_val_ready),
                 .dout_data(leaf_val),
                 .dout_eot(leaf_eot)
                 );

   stage_sum
     #(
       .W_LEAF(W_LEAF),
       .MAX_WEAKCOUNT(MAX_WEAKCOUNT),
       .STAGE_NUM(STAGE_NUM),
       .W_STAGE_THRESHOLD(W_STAGE_THRESHOLD)
       )
   stage_sum_i(
               .clk(clk),
               .rst(local_rst),
               .din_valid(leaf_val_valid),
               .din_ready(leaf_val_ready),
               .din_data(leaf_val),
               .din_eot(leaf_eot),
               .result_valid(result_valid),
               .result_ready(result_ready),
               .result(result_data)
               );

   assign internal_rst = result_valid ? 1 : 0;

   generate
      genvar              i;
      for(i=0; i<3; i++) begin : rect_sum_i
         rect_sum
            #(
              .W_DATA(W_DATA),
              .W_WEIGHT(W_WEIGHT),
              .W_DOUT(W_RECT_SUM)
              )
         rect0_sum_i(
                     .clk(clk),
                     .rst(local_rst),
                     .din_valid(din_valid),
                     .din_ready(rect_sum_din_ready[i]),
                     .din_data(din_data[i]),
                     .weight_valid(weights_valid),
                     .weight_ready(weight_ready[i]),
                     .weight(weight[i]),
                     .dout_valid(rect_sum_valid[i]),
                     .dout_ready(all_rect_sum_ready),
                     .dout_data(rect_sum[i]),
                     .dout_eot(rect_sum_eot[i])
                     );
      end
   endgenerate

   rects_mem
     #(
       .W_ADDR(W_ADDR),
       .FEATURE_WIDTH(FEATURE_WIDTH),
       .FEATURE_HEIGHT(FEATURE_HEIGHT),
       .FEATURE_NUM(FEATURE_NUM),
       .W_WEIGHT(W_WEIGHT)
       )
   rects(
         .clk(clk),
         .rst(local_rst),
         .addr_valid(rects_addr_valid),
         .addr_ready(rects_addr_ready),
         .addr0_data(rect0_addr),
         .addr1_data(rect1_addr),
         .addr2_data(rect2_addr),
         .addr_eot(rect_addr_eot),
         .weight_valid(weights_valid),
         .weight_ready(weights_ready),
         .weight0(weight[0]),
         .weight1(weight[1]),
         .weight2(weight[2])
         );

endmodule: classifier
