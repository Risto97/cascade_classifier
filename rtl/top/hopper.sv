module hopper
  #(
    parameter IMG_WIDTH = 41,
    parameter IMG_HEIGHT = 50,
    parameter SWEEP_X = 24,
    parameter SWEEP_Y = 24,

    localparam X_BOUNDARY = IMG_WIDTH - SWEEP_X,
    localparam Y_BOUNDARY = IMG_HEIGHT - SWEEP_Y,
    localparam W_X = $clog2(IMG_WIDTH),
    localparam W_Y = $clog2(IMG_HEIGHT)
   )
   (
    input            clk,
    input            rst,

    output           hop_valid,
    input            hop_ready,
    output [W_X-1:0] x_hop,
    output [W_Y-1:0] y_hop
    );

   logic [$clog2(IMG_WIDTH )-1:0] x_cnt_reg, x_cnt_next;
   logic [$clog2(IMG_HEIGHT)-1:0] y_cnt_reg, y_cnt_next;
   logic                          hop_valid_reg, hop_valid_next;


   assign x_hop = x_cnt_reg;
   assign y_hop = y_cnt_reg;

   assign hop_valid = hop_valid_reg;
   assign hop_valid_next = !hop_ready;

   always_comb
     begin
        x_cnt_next = x_cnt_reg + 1;

        if(x_cnt_next == X_BOUNDARY)
          begin
             y_cnt_next = y_cnt_reg + 1;
             x_cnt_next = 0;
          end
        if(y_cnt_next == Y_BOUNDARY)
          begin
             y_cnt_next = 0;
          end
     end

   always_ff @(posedge clk)
     if(rst)
       hop_valid_reg <= 0;
     else
       hop_valid_reg <= hop_valid_next;

   always_ff @(posedge clk)
     begin
        if(rst)
          begin
             x_cnt_reg <= 0;
             y_cnt_reg <= 0;
          end
        else if(hop_ready)
          begin
             x_cnt_reg <= x_cnt_next;
             y_cnt_reg <= y_cnt_next;
          end
     end

endmodule: hopper
