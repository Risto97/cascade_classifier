module rects_mem
  #(
    parameter W_ADDR = 10,
    parameter FEATURE_WIDTH = 25,
    parameter FEATURE_HEIGHT = 25,
    parameter FEATURE_NUM = 2913,
    parameter W_WEIGHT = 3,
    localparam W_ADDR_RECT = $clog2(FEATURE_NUM),
    localparam W_ADDR_FEAT = $clog2(FEATURE_NUM),
    localparam W_RECT = $clog2(FEATURE_WIDTH) // should be max(FEATURE_WIDTH, FEATURE_HEIGHT)
    )
   (
    input                 clk,
    input                 rst,

    output                addr_valid,
    input                 addr_ready,
    output [W_ADDR-1:0]   addr0_data,
    output [W_ADDR-1:0]   addr1_data,
    output [W_ADDR-1:0]   addr2_data,
    output [1:0]          addr_eot,

    output                weight_valid,
    input                 weight_ready,
    output [W_WEIGHT-1:0] weight0,
    output [W_WEIGHT-1:0] weight1,
    output [W_WEIGHT-1:0] weight2
    );

   logic                rect0_addr_valid, rect0_addr_ready;
   logic                rect1_addr_valid, rect1_addr_ready;
   logic                rect2_addr_valid, rect2_addr_ready;
   logic [W_ADDR-1:0]   rect0_addr_data, rect1_addr_data, rect2_addr_data;
   logic [1:0]          rect0_addr_eot, rect1_addr_eot, rect2_addr_eot;

   logic                weight0_addr_valid, weight1_addr_valid, weight2_addr_valid;
   logic                weight0_addr_ready, weight1_addr_ready, weight2_addr_ready;
   logic [11:0]         weight0_addr_data, weight1_addr_data, weight2_addr_data;

   logic                weight0_data_valid, weight1_data_valid, weight2_data_valid;
   logic                weight0_data_ready, weight1_data_ready, weight2_data_ready;
   logic [W_WEIGHT-1:0] weight0_data, weight1_data, weight2_data;


   logic [W_ADDR_FEAT-1:0] feature_cnt_reg, feature_cnt_next;

   assign feature_cnt_next = feature_cnt_reg + 1;

   assign weight0_data_ready = weight_ready;
   assign weight1_data_ready = weight_ready;
   assign weight2_data_ready = weight_ready;

   assign weight_valid = weight0_data_valid & weight1_data_valid & weight2_data_valid;

   assign weight0_addr_data = feature_cnt_reg;
   assign weight1_addr_data = feature_cnt_reg;
   assign weight2_addr_data = feature_cnt_reg;

   assign weight0_addr_valid = 1;
   assign weight1_addr_valid = 1;
   assign weight2_addr_valid = 1;

   assign weight0 = weight0_data;
   assign weight1 = weight1_data;
   assign weight2 = weight2_data;

   assign rect0_addr_ready = addr_ready;
   assign rect1_addr_ready = addr_ready;
   assign rect2_addr_ready = addr_ready;

   assign addr0_data = rect0_addr_data;
   assign addr1_data = rect1_addr_data;
   assign addr2_data = rect2_addr_data;

   assign addr_valid = rect0_addr_valid & rect1_addr_valid & rect2_addr_valid;
   assign addr_eot[0] = rect0_addr_eot[0] & rect1_addr_eot[0] & rect2_addr_eot[0];

   logic                   stage_eot;
   assign addr_eot[1] = stage_eot;

   always_comb
     begin
        stage_eot = 0;
        if(feature_cnt_next== 9||feature_cnt_next== 25||feature_cnt_next== 52||feature_cnt_next== 84||feature_cnt_next== 136||feature_cnt_next== 189||feature_cnt_next== 251||feature_cnt_next== 323||feature_cnt_next== 406||feature_cnt_next== 497||feature_cnt_next== 596||feature_cnt_next== 711||feature_cnt_next== 838||feature_cnt_next== 973||feature_cnt_next== 1109||feature_cnt_next== 1246||feature_cnt_next== 1405||feature_cnt_next== 1560||feature_cnt_next== 1729||feature_cnt_next== 1925||feature_cnt_next== 2122||feature_cnt_next== 2303||feature_cnt_next== 2502||feature_cnt_next== 2713||feature_cnt_next== 2913) begin
           stage_eot = 1;
        end
     end

   always_ff @(posedge clk)
     begin
        if (rst) begin
           feature_cnt_reg <= 0;
        end else if(addr_eot[0]) begin
           feature_cnt_reg <= feature_cnt_next;
        end
     end


   weight
     #(
       .W_DATA(W_WEIGHT),
       .W_ADDR(12),
       .WEIGHT_NUM(0)
       )
   weight0_mem(
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
       .W_DATA(W_WEIGHT),
       .W_ADDR(12),
       .WEIGHT_NUM(1)
       )
   weight1_mem(
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
       .W_DATA(W_WEIGHT),
       .W_ADDR(12),
       .WEIGHT_NUM(2)
       )
   weight2_mem(
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
