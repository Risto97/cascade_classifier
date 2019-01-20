module yield_on_one
  (
   input clk,
   input rst,
   dti.consumer din, // [u1] (2)
   dti.producer dout // () (0)

   );
   typedef struct packed { // [u1]
      logic [0:0] eot; // u1
      logic [0:0] data; // u1
   } din_t;

   typedef logic [0:0] dout_t;
   din_t din_s;
   dout_t dout_s;
   assign din_s = din.data;


   // Comb block for: dout
   always_comb begin
      dout.valid = 0;
      if (din.valid) begin
         if (din_s.data == 0 || (din_s.eot == 1 && din_s.data == 1)) begin
            dout.valid = 1;
         end
      end
   end

   // Comb block for: din
   always_comb begin
      din.ready = 0;
      if (din.valid) begin
         din.ready = 1;
         if (din_s.data == 0 || (din_s.eot == 1 && din_s.data == 1)) begin
            din.ready = dout.ready;
         end
      end
   end


endmodule
