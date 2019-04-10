module eot_gen
  #(
    parameter FEATURE_WIDTH = 24,
    parameter FEATURE_HEIGHT = 24,
    parameter W_DATA = 8
    )
   (
   input               clk,
   input               rst,

   input               din_valid,
   output              din_ready,
   input [W_DATA-1:0]  din_data,

   output              dout_valid,
   input               dout_ready,
   output [W_DATA-1:0] dout_data,
   output [1:0]        dout_eot
    );

   logic [$clog2(FEATURE_WIDTH )-1:0] x_cnt_reg, x_cnt_next;
   logic [$clog2(FEATURE_HEIGHT)-1:0] y_cnt_reg, y_cnt_next;

   logic                              handshake;
   logic [1:0]                        eot_o;

   assign dout_valid = din_valid;
   assign handshake = din_valid & dout_ready;
   assign din_ready = dout_ready;
   assign dout_data = din_data;
   assign dout_eot = eot_o;

   always_comb
     begin
        x_cnt_next = x_cnt_reg + 1;
        y_cnt_next = y_cnt_reg;
        eot_o = 0;

        if(x_cnt_next == FEATURE_WIDTH)
          begin
             x_cnt_next = 0;
             eot_o[0] = 1;
             y_cnt_next = y_cnt_reg + 1;
          end
        if(y_cnt_next == FEATURE_HEIGHT)
          begin
             eot_o[1] = 1;
             y_cnt_next = 0;
          end
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          begin
             x_cnt_reg <= 0;
             y_cnt_reg <= 0;
          end
        else if(handshake)
          begin
             x_cnt_reg <= x_cnt_next;
             y_cnt_reg <= y_cnt_next;
          end
     end

endmodule: eot_gen
