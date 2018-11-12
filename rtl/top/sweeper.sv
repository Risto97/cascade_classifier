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

   logic [$clog2(SWEEP_X)-1:0] x_cnt_reg, x_cnt_next;
   logic [$clog2(SWEEP_Y)-1:0] y_cnt_reg, y_cnt_next;
   logic [W_X-1:0]             x_reg, x_next;
   logic [W_Y-1:0]             y_reg, y_next;
   logic                       config_ready_reg, config_ready_next;
   logic                       addr_valid_reg;
   logic                       handshake;

   assign handshake = cfg_valid & addr_ready;

   assign x_next = x_cnt_reg + x_start;
   assign y_next = y_cnt_reg + y_start;
   assign x = x_reg;
   assign y = y_reg;

   assign cfg_ready = config_ready_reg;

   assign addr_valid = addr_valid_reg;
   // assign addr_valid = cfg_valid;

   always_comb
     begin
        config_ready_next = 0;

        x_cnt_next = x_cnt_reg + 1;
        if(x_cnt_next == SWEEP_X)
          begin
             y_cnt_next = y_cnt_reg + STRIDE_Y;
             x_cnt_next = x_start;
          end
        if(y_cnt_next == SWEEP_Y)
          begin
             y_cnt_next = y_start;
             config_ready_next = 1;
          end
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          begin
             x_cnt_reg <= 0;
             y_cnt_reg <= 0;
             config_ready_reg <= 0;
             addr_valid_reg <= 0;
             x_reg <= 0;
             y_reg <= 0;
          end
        else if(handshake)
          begin
             x_cnt_reg <= x_cnt_next;
             y_cnt_reg <= y_cnt_next;
             config_ready_reg <= config_ready_next;
             addr_valid_reg <= 1'b1;
             x_reg <= x_next;
             y_reg <= y_next;
          end
     end

   // if(SWEEP_Y % STRIDE_Y != 0) $finish;

endmodule: sweeper
