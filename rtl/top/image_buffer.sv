module image_buffer

  #(
    parameter W_DATA = 8,
    parameter IMG_WIDTH = 45,
    parameter IMG_HEIGHT = 45,
    localparam DEPTH = IMG_HEIGHT*IMG_WIDTH,
    localparam W_ADDR = $clog2(DEPTH)
    )
   (
    input               clk,
    input               rst,

    input               din_valid,
    output              din_ready,
    input [W_DATA-1:0]  din_data,
    input               din_eot,

    input               addr_valid,
    output              addr_ready,
    input [W_ADDR-1:0]  addr_data,

    output              dout_valid,
    input               dout_ready,
    output [W_DATA-1:0] dout_data
    );

   logic [W_DATA-1:0]   mem [DEPTH-1:0];

   logic [W_ADDR-1:0]   wr_cnt_next, wr_cnt_reg;
   logic                full, full_next;
   logic [W_DATA-1:0]   dout_buff;
   logic                dout_valid_reg, addr_ready_reg;
   logic                handshake_reg;

   assign dout_data = dout_buff;

   assign dout_valid = dout_valid_reg & handshake_reg & full;
   assign addr_ready = full & dout_ready;

   assign wr_cnt_next = (!din_eot & !full) ? (wr_cnt_reg+1):
                        0;

   assign din_ready = !full;

   assign full_next = ((din_eot & din_valid) | full)  ? 1 : 0;

   always_ff @(posedge clk)
     begin
        if(full & addr_valid & dout_ready)
          begin
             dout_buff <= mem[addr_data];
             dout_valid_reg <= addr_valid & full;
          end
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          begin
             full <= 0;
             handshake_reg <= 0;
          end
        else
          begin
             handshake_reg <= addr_valid & !din_ready;
             full <= full_next;
             addr_ready_reg <= full;
          end
     end


   always_ff @(posedge clk)
     begin
        if(din_valid)
          mem[wr_cnt_reg] <= din_data;
     end

   always_ff @(posedge clk)
     begin
        if(rst)
          begin
             wr_cnt_reg <= 0;
          end
        else if(din_valid)
          begin
             wr_cnt_reg <= wr_cnt_next;
          end
     end

endmodule: image_buffer
