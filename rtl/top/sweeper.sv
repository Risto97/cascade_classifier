module sweeper
  #(
    parameter IMG_WIDTH = 41,
    parameter IMG_HEIGHT = 50,
    parameter SWEEP_X = 24,
    parameter SWEEP_Y = 24,
    parameter STRIDE_Y = 2,
    localparam W_X = $clog2(IMG_WIDTH),
    localparam W_Y = $clog2(IMG_HEIGHT)
    )
   (
    input            clk,
    input            rst,

    input            cfg_valid,
    output           cfg_ready,
    input [W_X-1:0]  x_start,
    input [W_Y-1:0]  y_start,

    output           addr_valid,
    input            addr_ready,
    output [W_X-1:0] x,
    output [W_Y-1:0] y
    );

   logic             handshake;
   logic             addr_valid_reg, addr_valid_next;
   logic             cfg_ready_reg, cfg_ready_next;

   logic [$clog2(SWEEP_X)-1:0] x_cnt_reg, x_cnt_next;
   logic [$clog2(SWEEP_Y)-1:0] y_cnt_reg, y_cnt_next;

   assign handshake = cfg_valid & addr_ready & addr_valid;
   assign addr_valid = addr_valid_reg;

   assign x = x_cnt_reg + x_start;
   assign y = y_cnt_reg + y_start;
   assign cfg_ready = cfg_ready_reg;

   always_comb
     begin
        x_cnt_next = x_cnt_reg+1;
        y_cnt_next = y_cnt_reg;
        cfg_ready_next = 1'b0;

        if(x_cnt_reg == SWEEP_X-1)
          begin
             x_cnt_next = 0;
             y_cnt_next = y_cnt_reg+1;
          end
        if(y_cnt_reg == SWEEP_Y-1 && x_cnt_reg == SWEEP_X-2)
          begin
             cfg_ready_next = 1'b1;
          end
        if(y_cnt_next == SWEEP_Y)
          begin
             x_cnt_next = 0;
             y_cnt_next = 0;
          end
     end

   always_ff @(posedge clk)
     if(rst)
       addr_valid_reg <= 0;
     else
       addr_valid_reg <= 1;

   always_ff @(posedge clk)
     begin
        if(rst)
          begin
             x_cnt_reg <= 0;
             y_cnt_reg <= 0;
             cfg_ready_reg <= 0;
          end
        else if(handshake)
          begin
             cfg_ready_reg <= cfg_ready_next;
             x_cnt_reg <= x_cnt_next;
             y_cnt_reg <= y_cnt_next;
          end
     end


endmodule: sweeper
