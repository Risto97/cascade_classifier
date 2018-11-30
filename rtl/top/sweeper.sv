module sweeper
  #(
    parameter IMG_WIDTH = 41,
    parameter IMG_HEIGHT = 50,
    parameter SWEEP_X = 25,
    parameter SWEEP_Y = 25,
    parameter STRIDE_Y = 2,
    parameter SCALE_NUM = 2,
    localparam W_X = $clog2(IMG_WIDTH),
    localparam W_Y = $clog2(IMG_HEIGHT)
    )
   (
    input            clk,
    input            rst,

    output           window_pos_valid,
    input            window_pos_ready,
    output           window_pos_eot,
    output [W_Y-1:0] window_pos_y,
    output [W_X-1:0] window_pos_x,

    output           addr_valid,
    input            addr_ready,
    output [W_X-1:0] x,
    output [W_Y-1:0] y
    );

   logic             handshake;
   logic             addr_valid_reg;
   logic             window_eot_reg, window_eot_next;

   logic [$clog2(SWEEP_X)-1:0] x_cnt_reg, x_cnt_next;
   logic [$clog2(SWEEP_Y)-1:0] y_cnt_reg, y_cnt_next;

   logic [W_X-1:0]             hop_x_next, hop_x_reg;
   logic [W_Y-1:0]             hop_y_next, hop_y_reg;

   logic [21:0]                ratio_x[SCALE_NUM-1:0];
   logic [21:0]                ratio_y[SCALE_NUM-1:0];

   logic                       window_pos_valid_reg;
   assign window_pos_x = hop_x_reg;
   assign window_pos_y = hop_y_reg;
   assign window_pos_valid = window_pos_valid_reg;
   assign window_pos_eot = window_eot_reg;

   always_ff @(posedge clk)
     begin
        if(rst)
          window_pos_valid_reg <= 1;
        else begin
           if(window_pos_ready)
             window_pos_valid_reg <= 0;
           else
             window_pos_valid_reg <= 1;
        end
     end


   // generate
   //    genvar                   i;
   //    for(i = 0; i<SCALE_NUM; i++) begin
   //       assign ratio_x[i] = (IMG_WIDTH << 16) / (IMG_WIDTH / (1/0.75)**i) + 1;
   //       assign ratio_y[i] = (IMG_HEIGHT << 16) / (IMG_HEIGHT / (1/0.75)**i) + 1;
   //    end
   // endgenerate
   assign ratio_x[0] = 65537;
   assign ratio_x[1] = 87382;

   assign ratio_y[0] = 65537;
   assign ratio_y[1] = 87382;

   logic [$clog2(IMG_WIDTH)-1:0] boundary_x[SCALE_NUM-1:0];
   logic [$clog2(IMG_HEIGHT)-1:0] boundary_y[SCALE_NUM-1:0];
   assign boundary_x[0] = 20;
   assign boundary_x[1] = 8;
   assign boundary_y[0] = 20;
   assign boundary_y[1] = 8;

   // generate
   //    genvar                     j;
   //    for(j=0; j<SCALE_NUM; j++) begin
   //       assign boundary_x[j] = $floor((IMG_WIDTH / (1/0.75)**j) - SWEEP_X);
   //       assign boundary_y[j] = $floor((IMG_HEIGHT / (1/0.75)**j) - SWEEP_Y);
   //    end
   // endgenerate

   logic [$clog2(SCALE_NUM)-1:0] scale_cnt_reg, scale_cnt_next;

   assign handshake = addr_ready & addr_valid;
   assign addr_valid = addr_valid_reg;

   assign x = ((x_cnt_reg + hop_x_reg ) * ratio_x[scale_cnt_reg]) >> 16;
   assign y = ((y_cnt_reg + hop_y_reg ) * ratio_y[scale_cnt_reg]) >> 16;

   always_comb
     begin
        hop_x_next = hop_x_reg;
        if(x_cnt_reg == SWEEP_X-1 && y_cnt_reg == SWEEP_Y-1)
          begin
             hop_x_next = hop_x_reg + 1;
             if(hop_x_reg == boundary_x[scale_cnt_reg])
               hop_x_next = 0;
          end
     end

   always_comb
     begin
        hop_y_next = hop_y_reg;
        if(x_cnt_reg == SWEEP_X-1 && y_cnt_reg == SWEEP_Y-1 && hop_x_reg == boundary_x[scale_cnt_reg])
          begin
             hop_y_next = hop_y_reg + 1;
             if(hop_y_reg == boundary_y[scale_cnt_reg])
               hop_y_next = 0;
          end
     end

   always_comb
     begin
        scale_cnt_next = scale_cnt_reg;
        window_eot_next = window_eot_reg;
        if(hop_x_reg == boundary_x[scale_cnt_reg] && hop_y_reg == boundary_y[scale_cnt_reg] && x_cnt_reg == SWEEP_X-1 && y_cnt_reg == SWEEP_Y-1) begin
           scale_cnt_next = scale_cnt_reg + 1;
           if(scale_cnt_reg == SCALE_NUM-1)
             window_eot_next = 1;
        end
     end

   always_comb
     begin
        x_cnt_next = x_cnt_reg+1;
        y_cnt_next = y_cnt_reg;

        if(x_cnt_reg == SWEEP_X-1)
          begin
             x_cnt_next = 0;
             y_cnt_next = y_cnt_reg+1;
          end
        if(y_cnt_next == SWEEP_Y)
          begin
             x_cnt_next = 0;
             y_cnt_next = 0;
          end
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          window_eot_reg <= 0;
        else
          window_eot_reg <= window_eot_next;
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
             hop_y_reg <= 0;
             hop_x_reg <= 0;
             scale_cnt_reg <= 0;
          end
        else if(handshake)
          begin
             scale_cnt_reg <= scale_cnt_next;
             hop_y_reg <= hop_y_next;
             hop_x_reg <= hop_x_next;
             x_cnt_reg <= x_cnt_next;
             y_cnt_reg <= y_cnt_next;
          end
     end


endmodule: sweeper
