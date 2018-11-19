module window_sum
  #(
    parameter W_DATA = 26,
    parameter WINDOW_HEIGHT = 24,
    parameter WINDOW_WIDTH = 24
    )
   (
    input               clk,
    input               rst,

    input               din_valid,
    output              din_ready,
    input [W_DATA-1:0]  din_data,
    input [1:0]         din_eot,

    output              window_sum_valid,
    input               window_sum_ready,
    output [W_DATA+1:0] window_sum_data
    );

   logic [$clog2(WINDOW_HEIGHT)-1:0] eot_cnt_reg, eot_cnt_next;
   logic                             din_ready_reg;
   logic [$clog2(WINDOW_WIDTH)-1:0]  data_cnt_reg, data_cnt_next;
   logic [W_DATA+1:0]                din_accum_reg, din_accum_next;
   logic                             window_sum_valid_reg, window_sum_valid_next;


   assign din_ready = din_ready_reg;
   assign window_sum_data = din_accum_reg;
   assign window_sum_valid_next = (din_eot == 2'b11) ? 1: 0;
   assign window_sum_valid = window_sum_valid_reg;

   always_comb
     begin
        data_cnt_next = data_cnt_reg+1;
        eot_cnt_next = eot_cnt_reg +1;
        din_accum_next = din_accum_reg;

        if(data_cnt_reg == WINDOW_WIDTH)
          begin
             data_cnt_next = 1;
          end
        if(eot_cnt_reg == WINDOW_HEIGHT-1)
           begin
              eot_cnt_next = 0;
           end

         if(data_cnt_reg  == 1 && eot_cnt_reg == 0)
          begin
             din_accum_next = din_data;
          end

        if(data_cnt_reg == WINDOW_WIDTH & eot_cnt_reg == WINDOW_WIDTH-1)
          begin
             din_accum_next = din_accum_reg + din_data;
          end

        if((data_cnt_reg == WINDOW_WIDTH & eot_cnt_reg == 0) | (data_cnt_reg == 1 & eot_cnt_reg == WINDOW_HEIGHT-1))
          begin
             din_accum_next = din_accum_reg - din_data;
          end
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          window_sum_valid_reg <= 0;
        else
          window_sum_valid_reg <= window_sum_valid_next;
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          eot_cnt_reg <= 0;
        else if(din_eot[0])
          eot_cnt_reg <= eot_cnt_next;
     end
   always_ff @(posedge clk)
     begin
        if(rst)
          din_accum_reg <= 0;
        else if(din_valid)
          din_accum_reg <= din_accum_next;
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          begin
             din_ready_reg <= 0;
             data_cnt_reg <= 0;
          end
        else if(din_valid)
          begin
             data_cnt_reg <= data_cnt_next;
             din_ready_reg <= din_valid;
          end
     end

endmodule: window_sum
