module rect_addr_gen
  #(
    parameter W_ADDR = 10,
    parameter FEATURE_WIDTH = 25,
    parameter FEATURE_HEIGHT = 25,
    parameter FEATURE_NUM = 2913,
    parameter RECT_NUM = 0,
    localparam W_ADDR_RECT = $clog2(FEATURE_NUM*4),
    localparam W_RECT = $clog2(FEATURE_WIDTH) // should be max(FEATURE_WIDTH, FEATURE_HEIGHT)
    )
   (
    input               clk,
    input               rst,

    output              addr_valid,
    input               addr_ready,
    output [W_ADDR-1:0] addr_data,
    output              addr_eot
    );

   logic                rect_data_valid, rect_data_ready;
   logic [W_RECT-1:0]   rect_data;

   logic [W_ADDR_RECT-1:0] rect_addr_data;
   logic                   rect_addr_valid, rect_addr_ready;

   logic [1:0]             cnt_data_reg, cnt_data_next, cnt_data_inc;
   logic [W_ADDR_RECT-1:0] cnt_eot_reg, cnt_eot_next;
   logic [W_ADDR-1:0]      addr_data_reg, addr_data_next;
   logic [W_ADDR_RECT-1:0] width_next, width_reg, mult;

   logic                   addr_eot_o, addr_valid_o;

   logic [4:0]             state_reg, state_next;

   assign rect_addr_data = cnt_data_reg + (cnt_eot_reg << 2);
   assign cnt_data_inc = (cnt_data_reg < 3) ? cnt_data_reg + 1: 0;

   assign mult = rect_data * FEATURE_WIDTH;

   fifo #(
          .W_DATA(W_ADDR),
          .DEPTH(4),
          .PRELOAD(0)
          )
   rect0_fifo(
              .clk(clk),
              .rst(rst),
              .din_valid(addr_valid_o),
              .din_ready(fifo_addr_ready),
              .din_data(addr_data_reg),
              .din_eot(addr_eot_o),
              .dout_data(addr_data),
              .dout_valid(addr_valid),
              .dout_ready(addr_ready),
              .dout_eot(addr_eot)
              );


   always_comb
     begin
        state_next = 0;
        cnt_data_next = cnt_data_reg;
        cnt_eot_next = cnt_eot_reg;
        addr_data_next = addr_data_reg;
        addr_eot_o = 0;
        width_next = width_reg;

        case(state_reg)
          0: begin
             if(fifo_addr_ready)
               state_next = 1;
          end
          1: begin
             if(fifo_addr_ready)
               state_next = 2;
             cnt_data_next = cnt_data_inc;
          end
          2: begin
             if(fifo_addr_ready)
               state_next = 3;
             cnt_data_next = cnt_data_inc;
             addr_data_next = rect_data;
          end
          3: begin
             if(fifo_addr_ready)
               state_next = 4;
             cnt_data_next = cnt_data_inc;
             addr_data_next = addr_data_reg + mult;
          end
          4: begin
             if(fifo_addr_ready)
               state_next = 5;
             cnt_data_next = cnt_data_inc;
             cnt_eot_next = cnt_eot_reg + 1;
             width_next = rect_data;
             addr_data_next = addr_data_reg + rect_data;
          end
          5: begin
             if(fifo_addr_ready)
               state_next = 6;
             addr_data_next = addr_data_reg + mult;
          end
          6: begin
             if(fifo_addr_ready)
               state_next = 7;
             addr_data_next = addr_data_reg - width_reg;
          end
          7: begin
             if(fifo_addr_ready)
               state_next = 0;
             else
               state_next = 7;
             addr_eot_o = 1;
          end


        endcase
     end

   always @(state_reg)
     begin
        rect_data_ready = 0;
        rect_addr_valid = 0;
        addr_valid_o = 0;

        case(state_reg)
          0: begin
             rect_data_ready = 1;
          end
          1: begin
             rect_addr_valid = 1;
             rect_data_ready = 1;
          end
          2: begin
             rect_addr_valid = 1;
             rect_data_ready = 1;
          end
          3: begin
             rect_addr_valid = 1;
             rect_data_ready = 1;
          end
          4: begin
             addr_valid_o = 1;
             rect_addr_valid = 1;
             rect_data_ready = 1;
          end
          5: begin
             addr_valid_o = 1;
             rect_addr_valid = 0;
             rect_data_ready = 0;
          end
          6: begin
             addr_valid_o = 1;
             rect_addr_valid = 0;
             rect_data_ready = 0;
          end
          7: begin
             addr_valid_o = 1;
             rect_addr_valid = 0;
             rect_data_ready = 0;
          end

        endcase
     end

   always_ff @(posedge clk)
     begin
        if(rst) begin
           cnt_data_reg <= 0;
           cnt_eot_reg <= 0;
           state_reg <= 0;
           addr_data_reg <= 0;
           width_reg <= 0;
        end else begin
           width_reg <= width_next;
           addr_data_reg <= addr_data_next;
           cnt_eot_reg <= cnt_eot_next;
           cnt_data_reg <= cnt_data_next;
           state_reg <= state_next;
        end

     end

   rect #(.W_DATA(W_RECT),
          .W_ADDR(W_ADDR_RECT),
          .RECT_NUM(RECT_NUM))
   rect0_mem(
             .clk(clk),
             .rst(rst),
             .addr1_valid(rect_addr_valid),
             .addr1_ready(rect_addr_ready),
             .addr1_data(rect_addr_data),
             .data1_valid(rect_data_valid),
             .data1_ready(rect_data_ready),
             .data1(rect_data)
             );


endmodule: rect_addr_gen
