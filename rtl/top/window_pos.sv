module window_pos
  #(
    parameter IMG_WIDTH = 45,
    parameter IMG_HEIGHT = 45,
    localparam W_X = $clog2(IMG_WIDTH),
    localparam W_Y = $clog2(IMG_HEIGHT)
    )
   (
    input            clk,
    input            rst,

    input            window_pos_valid,
    output           window_pos_ready,
    input [W_X-1:0]  window_pos_x,
    input [W_Y-1:0]  window_pos_y,

    input            result_valid,
    output           result_ready,
    input            result,

    output           detect_pos_valid,
    input            detect_pos_ready,
    output [W_Y-1:0] detect_pos_y,
    output [W_X-1:0] detect_pos_x
    );

   logic [W_X-1:0]  pos_x_reg;
   logic [W_Y-1:0]  pos_y_reg;

   assign window_pos_ready = result_valid & detect_pos_ready;
   assign result_ready = window_pos_valid;

   assign detect_pos_y = pos_y_reg;
   assign detect_pos_x = pos_x_reg;

   assign detect_pos_valid = (result_valid && result);

   always_ff @(posedge clk)
     begin
        if(rst) begin
           pos_x_reg <= 0;
           pos_y_reg <= 0;
        end else if(result_valid) begin
           pos_x_reg <= window_pos_x;
           pos_y_reg <= window_pos_y;
        end
     end

endmodule : window_pos
