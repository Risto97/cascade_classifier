module rect_addr_gen
  #(
    parameter W_ADDR = 10,
    parameter FEATURE_WIDTH = 25,
    parameter FEATURE_HEIGHT = 25,
    parameter FEATURE_NUM = 2913,
    parameter RECT_NUM = 0,
    localparam W_ADDR_RECT = $clog2(FEATURE_NUM),
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
   logic [4*W_RECT-1:0]   rect_data;

   logic [W_ADDR_RECT-1:0] rect_addr_data, rect_addr_next;
   logic                   rect_addr_valid, rect_addr_ready;
   logic                   fifo_din_eot, fifo_din_valid, fifo_din_ready;
   logic [W_ADDR-1:0]      fifo_din_data;

   logic [3:0]             state_reg, state_next;

   logic [W_ADDR-1:0]      A,B,C,D;
   logic [W_RECT-1:0]      width, height;

   assign A = rect_data[$left(rect_data):$left(rect_data)-2*W_RECT+1];
   assign width = rect_data[$left(rect_data)-2*W_RECT+1:W_RECT];
   assign height = rect_data[2*W_RECT-1:0];
   assign B = A + width;
   assign D = B + (FEATURE_WIDTH * height);
   assign C = D - width;

   always_comb
     begin
        state_next = 0;
        rect_addr_next = rect_addr_data;

        case(state_reg)
          0: begin
             if(fifo_din_ready == 1)
               state_next = 1;
             else
               state_next = 0;
          end
          1: begin
             if(fifo_din_ready == 1)
               state_next = 2;
             else
               state_next = 1;
          end
          2: begin
             if(fifo_din_ready)
               state_next = 3;
             else
               state_next = 2;
          end
          3: begin
             if(fifo_din_ready) begin
                state_next = 4;
                rect_addr_next = rect_addr_data+1;
             end
             else
               state_next = 3;
          end
          4: begin
             if(fifo_din_ready) begin
                state_next = 1;
             end
             else
               state_next = 4;
          end
        endcase
     end

   always_comb
     begin
        rect_data_ready = 0;
        rect_addr_valid = 0;
        fifo_din_valid = 0;
        fifo_din_data = 0;
        fifo_din_eot = 0;

        case(state_reg)
          0: begin
             rect_data_ready = 1;
             rect_addr_valid = 1;
          end
          1: begin
             fifo_din_data = A;
             fifo_din_valid = 1;
          end
          2: begin
             fifo_din_data = B;
             fifo_din_valid = 1;
          end
          3: begin
             fifo_din_data = D;
             fifo_din_valid = 1;
          end
          4: begin
             fifo_din_data = C;
             fifo_din_valid = 1;
             rect_data_ready = 1;
             rect_addr_valid = 1;
             fifo_din_eot = 1;
          end
        endcase
     end

   always_ff @(posedge clk)
     begin
        if(rst) begin
           state_reg <= 0;
           rect_addr_data <= 0;
        end else begin
           state_reg <= state_next;
           rect_addr_data <= rect_addr_next;
        end
     end

   fifo #(
          .W_DATA(W_ADDR),
          .DEPTH(4),
          .PRELOAD(0)
          )
   rect0_fifo(
              .clk(clk),
              .rst(rst),
              .din_valid(fifo_din_valid),
              .din_ready(fifo_din_ready),
              .din_data(fifo_din_data),
              .din_eot(fifo_din_eot),
              .dout_data(addr_data),
              .dout_valid(addr_valid),
              .dout_ready(addr_ready),
              .dout_eot(addr_eot)
              );


   rect #(.W_DATA(4*W_RECT),
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
