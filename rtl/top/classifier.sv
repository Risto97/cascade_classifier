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
    localparam W_ADDR_STAGE = $clog2(STAGE_NUM),
    localparam W_FEATURE_ACCUM = $clog2(MAX_WEAKCOUNT) + W_LEAF,
    localparam W_ADDR_RECT = $clog2(FEATURE_NUM*4),
    localparam W_ADDR_FEAT = $clog2(FEATURE_NUM),
    localparam W_RECT = $clog2(FEATURE_WIDTH) // should be max(FEATURE_WIDTH, FEATURE_HEIGHT)
    )
   (
    input                clk,
    input                rst,

    input                din_valid,
    output               din_ready,
    input [W_DATA-1:0]   din_data,

    output               addr_valid,
    input                addr_ready,
    output [W_ADDR-1:0]  addr_data,

    output               result_valid,
    input                result_ready,
    output               result_data,

    input                stddev_valid,
    output               stddev_ready,
    input [W_STDDEV-1:0] stddev_data
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

   logic                stage_sum_valid_next, stage_sum_valid_reg;
   logic signed [W_FEATURE_ACCUM-1:0] stage_sum_reg, stage_sum_next;

   logic signed [W_STDDEV+W_FEATURE_THRESHOLD-1:0] thresh_stddev;

   logic [W_ADDR_FEAT-1:0] feature_cnt_reg, feature_cnt_next;
   logic [W_ADDR_STAGE-1:0] stage_cnt_reg, stage_cnt_next;

   logic signed [W_FEATURE_ACCUM-1:0] feature_accum_reg, feature_accum_next;

   logic                              din_ready_o;
   logic                              local_rst, internal_rst_reg, internal_rst_next;

   logic                              result_valid_o, result_data_o;

   assign result_valid = result_valid_o;
   assign result_data = result_data_o;

   assign local_rst = internal_rst_reg | rst;

   assign din_ready = din_ready_o;

   assign stddev_ready = 1;

   assign dot_cnt_next = (dot_cnt_reg < 4) ? dot_cnt_reg + 1 : 1;

   assign accum_weighted_sum_valid = (rect_cnt_reg == 3) & rect_sum_valid_reg;

   assign weighted_sum = rect_sum_reg * weight_data_reg*4096;

   assign feature_cnt_next = (accum_weighted_sum_valid) ? feature_cnt_reg + 1 : feature_cnt_reg;

   assign thresh_stddev = featureThreshold * $signed(stddev_data);


   always_comb
     begin
        din_ready_o = 0;
        internal_rst_next = 0;
        result_valid_o = 0;
        result_data_o = 0;

        if(stage_sum_valid_reg) begin
           if(stage_sum_reg < stageThreshold) begin
              din_ready_o = 1;
              internal_rst_next = 1;
           end
           if(stage_cnt_reg == 25) begin
              din_ready_o = 1;
              internal_rst_next = 1;
              result_valid_o = 1;
              result_data_o = 1;
           end
        end
     end

   always_comb
     begin
        feature_accum_next = feature_accum_reg;
        stage_cnt_next = stage_cnt_reg;
        stage_sum_valid_next = 0;
        stage_sum_next = stage_sum_reg;

        if(leaf_valid) begin
           if(feature_cnt_reg== 9||feature_cnt_reg== 25||feature_cnt_reg== 52||feature_cnt_reg== 84||feature_cnt_reg== 136||feature_cnt_reg== 189||feature_cnt_reg== 251||feature_cnt_reg== 323||feature_cnt_reg== 406||feature_cnt_reg== 497||feature_cnt_reg== 596||feature_cnt_reg== 711||feature_cnt_reg== 838||feature_cnt_reg== 973||feature_cnt_reg== 1109||feature_cnt_reg== 1246||feature_cnt_reg== 1405||feature_cnt_reg== 1560||feature_cnt_reg== 1729||feature_cnt_reg== 1925||feature_cnt_reg== 2122||feature_cnt_reg== 2303||feature_cnt_reg== 2502||feature_cnt_reg== 2713||feature_cnt_reg== 2913) begin
              stage_sum_next = feature_accum_reg;
              stage_sum_valid_next = 1;
              stage_cnt_next = stage_cnt_reg + 1;
              feature_accum_next = leafVal_data;
           end
           else
             feature_accum_next = feature_accum_reg + leafVal_data;
        end
     end

   always_comb
     begin
        accum_weighted_sum_next = accum_weighted_sum_reg;
        if(rect_sum_valid_reg) begin
           accum_weighted_sum_next = accum_weighted_sum_reg + weighted_sum;

           if(rect_cnt_reg == 1)
             accum_weighted_sum_next = weighted_sum;
        end



        // else if(accum_weighted_sum_valid && rect_sum_valid_reg)
        //   accum_weighted_sum_next = 0;
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
        if(local_rst) begin
           dot_cnt_reg <= 1;
           rect_sum_reg <= 0;
           rect_sum_valid_reg <= 0;
           weight_data_reg <= 0;
           accum_weighted_sum_reg <= 0;
           feature_cnt_reg <= 0;
           rect_cnt_reg <= 1;
           stage_cnt_reg <= 0;
           feature_accum_reg <= 0;
           stage_sum_valid_reg <= 0;
           stage_sum_reg <= 0;
          end else if (din_valid) begin
             stage_sum_reg <= stage_sum_next;
             stage_sum_valid_reg <= stage_sum_valid_next;
             stage_cnt_reg <= stage_cnt_next;
             feature_accum_reg <= feature_accum_next;
             feature_cnt_reg <= feature_cnt_next;
             rect_cnt_reg <= rect_cnt_next;
             accum_weighted_sum_reg <= accum_weighted_sum_next;
             weight_data_reg <= weight_data_next;
             rect_sum_valid_reg <= rect_sum_valid_next;
             rect_sum_reg <= rect_sum_next;
             dot_cnt_reg <= dot_cnt_next;
          end
     end

   always_ff @(posedge clk)
     begin
        if(local_rst)
          internal_rst_reg <= 0;
        else
          internal_rst_reg <= internal_rst_next;
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
         .rst(local_rst),
         .addr_valid(addr_valid),
         .addr_ready(addr_ready),
         .addr_data(addr_data),
         .addr_eot(addr_eot),
         .weight_valid(weight_valid),
         .weight_ready(weight_ready),
         .weight(weight_data)
         );


   logic featureThreshold_addr_valid, featureThreshold_addr_ready, featureThreshold_valid, featureThreshold_ready;
   logic [W_ADDR_FEAT-1:0] featureThreshold_addr;
   logic signed [W_FEATURE_THRESHOLD-1:0] featureThreshold;

   assign featureThreshold_addr = feature_cnt_reg;
   assign featureThreshold_addr_valid = 1;
   assign featureThreshold_ready = 1;

   featureThreshold
     #(
       .W_DATA(W_FEATURE_THRESHOLD),
       .W_ADDR(W_ADDR_FEAT)
       )
   featureThreshold_i(
                      .clk(clk),
                      .rst(local_rst),
                      .addr1_valid(featureThreshold_addr_valid),
                      .addr1_ready(featureThreshold_addr_ready),
                      .addr1_data(featureThreshold_addr),
                      .data1_valid(featureThreshold_valid),
                      .data1_ready(featureThreshold_ready),
                      .data1(featureThreshold)
                      );


   logic                                  leafNum;
   logic                                  leaf_valid_tmp, leaf_valid, leaf_ready, leaf_addr_ready, leaf_addr_valid;
   logic signed [W_LEAF:0]                leafVal_data;

   assign leafNum = (accum_weighted_sum_next >= thresh_stddev) ? 0 : 1;
   assign leaf_ready = 1;
   assign leaf_addr_valid = featureThreshold_addr_valid;
   assign leaf_valid = leaf_valid_tmp & accum_weighted_sum_valid;

   leafVal
     #(
       .W_LEAF(W_LEAF),
       .FEATURE_NUM(FEATURE_NUM)
       )
   leafVal_i(
             .clk(clk),
             .rst(local_rst),
             .addr_valid(leaf_addr_valid), // !!!!!!!!!!1
             .addr_ready(leaf_addr_ready),
             .addr_data(feature_cnt_reg),
             .leaf_num(leafNum),
             .data_valid(leaf_valid_tmp),
             .data_ready(leaf_ready),
             .data(leafVal_data)
             );

   logic                                  stageThreshold_valid, stageThreshold_ready;
   logic                                  stageThreshold_addr_valid, stageThreshold_addr_ready;
   logic [W_ADDR_STAGE-1:0]               stageThreshold_addr;
   logic signed [10:0]                    stageThreshold;

   assign stageThreshold_ready = 1;
   assign stageThreshold_addr_valid = 1;
   assign stageThreshold_addr = stage_cnt_reg;

   stageThreshold
     #(
       .W_DATA(11),
       .W_ADDR(W_ADDR_STAGE)
       )
   stageThreshold_i(
                    .clk(clk),
                    .rst(local_rst),
                    .addr1_valid(stageThreshold_addr_valid),
                    .addr1_ready(stageThreshold_addr_ready),
                    .addr1_data(stageThreshold_addr),
                    .data1_valid(stageThreshold_valid),
                    .data1_ready(stageThreshold_ready),
                    .data1(stageThreshold)
                    );

endmodule: classifier
