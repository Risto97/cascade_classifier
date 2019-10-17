module rect_sum
  #(
    parameter W_DATA = 18,
    parameter W_WEIGHT = 3,
    parameter W_DOUT = $clog2(4*2**W_DATA) + W_WEIGHT + $clog2(4096)
    )
   (
    input                       clk,
    input                       rst,

    input                       din_valid,
    output                      din_ready,
    input [W_DATA-1:0]          din_data,

    input                       weight_valid,
    output                      weight_ready,
    input signed [W_WEIGHT-1:0] weight,

    output                      dout_valid,
    input                       dout_ready,
    output signed [W_DOUT-1:0]      dout_data,
    output                      dout_eot
    );

   logic [1:0]                 dot_cnt_reg;
   logic signed [W_DATA+6:0]   data_accum_reg, data_accum_next;
   logic                       dout_eot_reg, dout_eot_next;
   logic signed [W_DOUT-1:0]   dout_o;


   assign din_ready = dout_ready;
   // assign weight_ready = dout_ready;
   assign dout_eot_next = (dot_cnt_reg == 3) ? 1 : 0;
   assign dout_eot = dout_eot_reg;
   assign dout_valid = dout_eot_reg;

   assign dout_o = (dout_eot_reg) ? (weight * data_accum_reg) : 0; // DELETE THIS CONDITIONAL ASSIGNMENT AFTER TEST
   assign weight_ready = (weight_valid && dout_eot_next) ? 1 : 0;

   assign dout_data = dout_o * 4096;

   always_comb
     begin
        data_accum_next = data_accum_reg;

        case(dot_cnt_reg)
          0: data_accum_next = din_data;
          1: data_accum_next = data_accum_reg - din_data;
          2: data_accum_next = data_accum_reg + din_data;
          3: data_accum_next = data_accum_reg - din_data;
        endcase
     end

   always_ff @(posedge clk)
     begin
        if(rst) begin
           dot_cnt_reg <= 0;
           data_accum_reg <= 0;
           dout_eot_reg <= 0;
        end else if(din_valid) begin
           data_accum_reg <= data_accum_next;
           dot_cnt_reg <= dot_cnt_reg + 1;
           dout_eot_reg <= dout_eot_next;
        end
     end

endmodule: rect_sum
