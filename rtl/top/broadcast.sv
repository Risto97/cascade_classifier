module broadcast
  #(
    parameter W_DATA = 8
    )(
      input               clk,
      input               rst,

      input               din_valid,
      output              din_ready,
      input [W_DATA-1:0]  din_data,
      input [1:0]         din_eot,

      output              dout1_valid,
      input               dout1_ready,
      output [W_DATA-1:0] dout1_data,
      output [1:0]        dout1_eot,

      output              dout2_valid,
      input               dout2_ready,
      output [W_DATA-1:0] dout2_data,
      output [1:0]        dout2_eot
     );

   logic                  ready_reg1, ready_reg2;
   logic [1:0]            ready_all;

   assign ready_all[0] = dout1_ready | ready_reg1;
   assign ready_all[1] = dout2_ready | ready_reg2;
   assign dout1_valid = din_valid & !ready_reg1;
   assign dout2_valid = din_valid & !ready_reg2;
   assign dout1_data = din_data;
   assign dout2_data = din_data;
   assign dout1_eot = din_eot;
   assign dout2_eot = din_eot;

   assign din_ready = &ready_all;

   always_ff @(posedge clk) begin
      if(rst) begin
         ready_reg1 <= 1'b0;
         ready_reg2 <= 1'b0;
      end
      else begin
         if(din_ready) begin
            ready_reg1 <= 1'b0;
            ready_reg2 <= 1'b0;
         end
         else begin
            ready_reg1 <= ready_reg1 | (dout1_valid & dout1_ready);
            ready_reg2 <= ready_reg2 | (dout2_valid & dout2_ready);
         end
      end
   end

endmodule : broadcast
