module feature_val
  #(
    parameter W_DIN = 23,
    parameter W_DOUT = 20,
    parameter W_STDDEV = 36,
    parameter FEATURE_NUM = 2913,
    parameter W_FEATURE_THRESHOLD = 13,
    parameter W_LEAF = 14,
    localparam W_ADDR_FEAT = $clog2(FEATURE_NUM)
    )
   (
    input                    clk,
    input                    rst,

    input                    din_valid,
    output                   din_ready,
    input signed [W_DIN-1:0] din_data,

    input                    stddev_valid,
    output                   stddev_ready,
    input [W_STDDEV-1:0]     stddev,

    output                   dout_valid,
    input                    dout_ready,
    output [W_DOUT-1:0]      dout_data,
    output                   dout_eot
    );

   logic [W_ADDR_FEAT-1:0] feature_cnt_reg;
   logic                   featureThreshold_ready, featureThreshold_valid;
   logic signed [W_FEATURE_THRESHOLD-1:0] featureThreshold;
   logic                                  featureThreshold_addr_valid, featureThreshold_addr_ready;

   logic                                  leaf_addr_valid, leaf_addr_ready, leaf_num;
   logic                                  leaf_valid, leaf_ready;
   logic [W_LEAF-1:0]                     leaf_data;

   logic [W_LEAF-1:0]                     dout_reg, dout_next;
   logic                                  dout_valid_reg, dout_valid_next;
   logic                                  dout_eot_o;
   assign dout_eot = dout_eot_o & dout_valid;

   logic signed [W_STDDEV+W_FEATURE_THRESHOLD-1:0] stddev_threshold;

   assign stddev_threshold = $signed(stddev) * featureThreshold;

   assign featureThreshold_ready = 1;
   assign leaf_ready = 1;
   assign stddev_ready = 1;
   assign featureThreshold_addr_valid = din_valid;
   assign leaf_addr_valid = din_valid;

   assign leafNum = (din_data >= stddev_threshold) ? 0 : 1;
   assign dout_data = dout_reg;
   assign dout_valid = dout_valid_reg;
   assign dout_next = leaf_data;
   assign dout_valid_next = leaf_valid;
   assign din_ready = dout_ready;

   always_ff @(posedge clk) begin
      if(rst) begin
         dout_reg <= 0;
         dout_valid_reg <= 0;
      end else begin
         dout_reg <= dout_next;
         dout_valid_reg <= dout_valid_next;
      end
   end

   always_ff @(posedge clk) begin
      if(rst) begin
         feature_cnt_reg <= 0;
      end else if(din_valid) begin
         feature_cnt_reg <= feature_cnt_reg+1;
      end
   end

   always_comb
     begin
        dout_eot_o = 0;
        if(feature_cnt_reg== 9||feature_cnt_reg== 25||feature_cnt_reg== 52||feature_cnt_reg== 84||feature_cnt_reg== 136||feature_cnt_reg== 189||feature_cnt_reg== 251||feature_cnt_reg== 323||feature_cnt_reg== 406||feature_cnt_reg== 497||feature_cnt_reg== 596||feature_cnt_reg== 711||feature_cnt_reg== 838||feature_cnt_reg== 973||feature_cnt_reg== 1109||feature_cnt_reg== 1246||feature_cnt_reg== 1405||feature_cnt_reg== 1560||feature_cnt_reg== 1729||feature_cnt_reg== 1925||feature_cnt_reg== 2122||feature_cnt_reg== 2303||feature_cnt_reg== 2502||feature_cnt_reg== 2713||feature_cnt_reg== 2913) begin
           dout_eot_o = 1;
        end
     end

   featureThreshold
     #(
       .W_DATA(W_FEATURE_THRESHOLD),
       .W_ADDR(W_ADDR_FEAT)
       )
   featureThreshold_i(
                      .clk(clk),
                      .rst(rst),
                      .addr1_valid(featureThreshold_addr_valid),
                      .addr1_ready(featureThreshold_addr_ready),
                      .addr1_data(feature_cnt_reg),
                      .data1_valid(featureThreshold_valid),
                      .data1_ready(featureThreshold_ready),
                      .data1(featureThreshold)
                      );
   leafVal
     #(
       .W_LEAF(W_LEAF),
       .FEATURE_NUM(FEATURE_NUM)
       )
   leafVal_i(
             .clk(clk),
             .rst(rst),
             .addr_valid(leaf_addr_valid), // !!!!!!!!!!1
             .addr_ready(leaf_addr_ready),
             .addr_data(feature_cnt_reg),
             .leaf_num(leafNum),
             .data_valid(leaf_valid),
             .data_ready(leaf_ready),
             .data(leaf_data)
             );

endmodule : feature_val
