module fifo2
  #(
	  parameter DEPTH = 64,
    parameter THRESHOLD = 0,
    parameter DIN = 16,
    parameter PRELOAD = 0,
    parameter REGOUT = 0
	  )
	 (
	  input logic clk,
	  input logic rst,
	  dti.consumer din,
	  dti.producer dout
	  ) ;

   typedef struct packed
                  {
                     logic eot;
                     logic [$size(din.data)-2:0] data;
                  } data_t;

   data_t din_s;
   data_t dout_s;

   assign din_s = din.data;
   assign dout.data = dout_s;

	 localparam CW = $clog2(DEPTH);
	 localparam WIDTH = DIN;

	 logic [WIDTH-1:0] ram [0:DEPTH-1];
	 logic [CW:0]      raddr_reg;
	 logic [CW:0]      raddr_next;
	 logic [CW:0]      waddr_reg;
	 logic [CW:0]      waddr_next;

   logic [CW:0]      fifo_load_tmp;
   logic [CW-1:0]    fifo_load;
   logic             fifo_valid;
   logic             out_ready;
   logic             out_valid;
   logic             out_handshake;

	 logic             we;
	 wire              dv = waddr_reg != raddr_reg;

   logic [WIDTH-1:0]  out_buff;

	 wire              eq_cnt = waddr_reg[CW-1:0] == raddr_reg[CW-1:0];
	 wire              eq_msb = waddr_reg[CW] == raddr_reg[CW];
	 wire              full = eq_cnt & ~eq_msb;
	 wire              empty = eq_cnt & eq_msb;

	 logic [WIDTH-1:0] in_buff;

   logic             thr_reached;

   assign fifo_load_tmp = waddr_reg - raddr_reg;
   assign fifo_load = fifo_load_tmp[CW-1 : 0];

   assign thr_reached = fifo_load > (THRESHOLD - 1);

   if ( THRESHOLD ) begin
      assign fifo_valid = ~empty && thr_reached;
   end else begin
      assign fifo_valid = ~empty;
   end

   assign in_buff = din_s.data;
	 assign dout_s = out_buff[WIDTH-1:0];
   assign dout.valid = out_valid;

   assign out_handshake = fifo_valid && out_ready;

   if (REGOUT) begin
      always_ff @(posedge clk)
        begin
            if(rst) begin
              out_valid <= '0;
            end else if (out_ready) begin
              out_valid <= fifo_valid;
            end
        end

      assign out_ready = (!out_valid) | dout.ready;

      always_ff @(posedge clk) begin
         if(rst | din_s.eot) begin
            out_buff <= 0;
         end
         else if (out_ready) begin
            out_buff <= ram[raddr_reg[CW-1:0]];
         end
      end

   end else begin

      assign out_buff = ram[raddr_reg[CW-1:0]];
      assign out_valid = fifo_valid;
      assign out_ready = dout.ready;

   end


	 always @(posedge clk) begin
      if(rst | din_s.eot) begin
         ram <= '{default:0};
      end
	    else if (we == 1'b1) begin
		    ram[waddr_reg[CW-1:0]] <= in_buff;
     end
   end



	 always_ff @(posedge clk)
	   if (rst | din_s.eot)
		   begin
			    raddr_reg <= '0;
			    waddr_reg <= PRELOAD;
		   end
	   else
		   begin
			    raddr_reg <= raddr_next;
			    waddr_reg <= waddr_next;
		   end


	 wire ready = out_ready | ~full;
	 assign din.ready = ready;

	 always_comb // Write logic
	   if (din.valid & ready)
		   begin
			    we = 1'b1;
			    waddr_next = waddr_reg + 1'b1;
		   end
	   else
		   begin
			    we = 1'b0;
			    waddr_next = waddr_reg;
		   end

	 always_comb // Read logic
	   if (out_handshake) begin
			  raddr_next = raddr_reg + 1'b1;
		 end else begin
		   raddr_next = raddr_reg;
     end
endmodule
