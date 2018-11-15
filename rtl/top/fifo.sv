
module fifo
  #(
    parameter W_DATA = 8,
    parameter DEPTH = 32,
    parameter PRELOAD = 4)
   (
    input               clk,
    input               rst,

    input               din_valid,
    output              din_ready,
    input [W_DATA-1:0]  din_data,
    input [1:0]         din_eot,

    output [W_DATA-1:0] dout_data,
    output              dout_valid,
    input               dout_ready,
    output [1:0]        dout_eot

 );

   localparam AW = $clog2(DEPTH);
   localparam DW = $clog2(DEPTH);

   logic [W_DATA-1:0]   mem [DEPTH-1:0];
   logic [1:0]          mem_eot[DEPTH-1:0];

   logic [AW:0]         wr_pointer_next, wr_pointer_reg;
   logic [AW:0]         rd_pointer_next, rd_pointer_reg;

   logic                full_or_empty;
   logic                eq_msb;
   logic                we;
   logic                wr_ready;
   logic                full, empty;



   assign full_or_empty = wr_pointer_reg[AW-1:0] == rd_pointer_reg[AW-1:0];
   assign eq_msb = wr_pointer_reg[AW] == rd_pointer_reg[AW];

   assign empty = eq_msb & full_or_empty;
   assign full  = ~eq_msb & full_or_empty;

   assign dout_data = mem[rd_pointer_reg[AW-1:0]];
   assign dout_eot = mem_eot[rd_pointer_reg[AW-1:0]];

   assign dout_valid = ~empty;
   assign din_ready = dout_ready | ~full;


   always_ff @(posedge clk)
     begin
        if(rst | din_eot[1]) begin
           mem <= '{default:0};
           mem_eot <= '{default:0};
        end
        else if(we == 1'b1) begin
           mem[wr_pointer_reg[AW-1:0]] <= din_data;
           mem_eot[wr_pointer_reg[AW-1:0]] <= din_eot;
        end
     end

   always_ff @(posedge clk)
     begin
        if(rst | din_eot[1]) begin
           wr_pointer_reg <= PRELOAD;
           rd_pointer_reg <= '0;
        end
        else
          begin
             wr_pointer_reg <= wr_pointer_next;
             rd_pointer_reg <= rd_pointer_next;
          end
     end

   assign wr_ready = din_ready;
   always_comb //write
     begin
        if (din_valid & wr_ready) begin
           wr_pointer_next = wr_pointer_reg + 1;
           we = 1'b1;
        end
        else begin
           we = 0;
           wr_pointer_next = wr_pointer_reg;
        end
     end

   always_comb // read
     if ( ~empty & dout_ready) begin
        rd_pointer_next = rd_pointer_reg + 1;
     end
     else begin
        rd_pointer_next = rd_pointer_reg;
     end




endmodule : fifo
