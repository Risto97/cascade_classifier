module stage_sum
  #(
    parameter W_LEAF = 13,
    parameter MAX_WEAKCOUNT = 211,
    parameter STAGE_NUM = 25,
    parameter W_STAGE_THRESHOLD = 11,
    localparam W_ADDR_STAGE = $clog2(STAGE_NUM),
    localparam W_LEAF_ACCUM = $clog2(2**W_LEAF) + $clog2(MAX_WEAKCOUNT)
    )
   (
    input                     clk,
    input                     rst,

    input                     din_valid,
    output                    din_ready,
    input signed [W_LEAF-1:0] din_data,
    input                     din_eot,

    output                    result_valid,
    input                     result_ready,
    output                    result
    );

   logic [W_ADDR_STAGE-1:0] stage_cnt_reg, stage_cnt_next;
   assign stage_cnt_next = stage_cnt_reg + 1;

   logic signed [W_LEAF_ACCUM-1:0] leaf_accum_next, leaf_accum_reg;

   logic                           result_o, result_valid_o, din_ready_o;
   assign result = result_o;
   assign result_valid = result_valid_o;
   assign din_ready = din_ready_o;

   always_comb
     begin
        result_valid_o = 0;
        result_o = 0;
        din_ready_o = 0;

        if(stage_valid_reg && stageThreshold_valid) begin
          if(leaf_accum_reg < stageThreshold) begin
             result_o = 0;
             result_valid_o = 1;
             din_ready_o = 1;
          end
          else if(stage_cnt_reg == STAGE_NUM) begin
             result_o = 1;
             result_valid_o = 1;
             din_ready_o = 1;
          end
        end
     end

   always_ff @(posedge clk) begin
      if(rst) begin
         stage_cnt_reg <= 0;
      end else if(din_eot) begin
         stage_cnt_reg <= stage_cnt_next;
      end
   end

   logic stage_valid_reg, stage_valid_next;

   assign stage_valid_next = din_eot;
   assign leaf_accum_next = (stage_valid_reg && din_valid) ? din_data : leaf_accum_reg + din_data;

   always_ff @(posedge clk) begin
      if(rst) begin
         leaf_accum_reg <= 0;
         stage_valid_reg <= 0;
      end else if(din_valid) begin
         stage_valid_reg <= stage_valid_next;
         leaf_accum_reg <= leaf_accum_next;
      end
   end

   logic stageThreshold_addr_valid, stageThreshold_addr_ready;
   logic stageThreshold_valid, stageThreshold_ready;
   logic signed [W_STAGE_THRESHOLD-1:0] stageThreshold;

   assign stageThreshold_addr_valid = 1 & !stage_valid_reg;
   assign stageThreshold_ready = 1;

   stageThreshold
     #(
       .W_DATA(W_STAGE_THRESHOLD),
       .W_ADDR(W_ADDR_STAGE)
       )
   stageThreshold_i(
                    .clk(clk),
                    .rst(rst),
                    .addr1_valid(stageThreshold_addr_valid),
                    .addr1_ready(stageThreshold_addr_ready),
                    .addr1_data(stage_cnt_reg),
                    .data1_valid(stageThreshold_valid),
                    .data1_ready(stageThreshold_ready),
                    .data1(stageThreshold)
                    );


endmodule : stage_sum
