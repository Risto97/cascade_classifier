module queue_one_by_one
  #(
    W_DIN0 = 16,
    W_DIN1 = 16
    )
   (
    input clk,
    input rst,
    dti.consumer din0,
    dti.consumer din1,
    dti.producer dout0,
    dti.producer dout1
    );

   typedef struct packed {
      logic       eot;
      logic [W_DIN0-2:0] data;
   } data0_t;

   typedef struct       packed {
      logic             eot;
      logic [W_DIN1-2:0] data;
   } data1_t;

   data0_t din0_s;
   data0_t dout0_s;
   data1_t din1_s;
   data1_t dout1_s;

   assign din0_s = din0.data;
   assign din1_s = din1.data;
   assign dout0_s = din0_s;
   assign dout1_s = din1_s;
   assign dout0.data = dout0_s;
   assign dout1.data = dout1_s;

   logic                active_output_reg, active_output_next;
   logic                handshake0;
   logic                handshake1;
   logic                eotshake;

   logic                dout1_valid_reg;
   assign dout1.valid = dout1_valid_reg;

   // assign din0.ready = dout0.ready;
   // assign din1.ready = dout1.ready;
   assign handshake0 = din0.valid && dout0.ready;
   assign handshake1 = din1.valid && dout1.ready;

   // assign eotshake = (din0_s.eot == 1 && handshake0) ? 1 : 0;

   // assign dout0.valid = active_output_reg == 1 ? din0.valid : 0;
   // assign dout1.valid = active_output_reg == 0 ? 0 : din1.valid;

   always_comb begin
      eotshake = 0;
      dout0.valid = 0;
      dout1.valid = 0;
      din0.ready = 0;
      din1.ready = 0;
      case(active_output_reg)
        0: begin
           dout0.valid = din0.valid;
           din0.ready = dout0.ready;
           if(handshake0 && &din0_s.eot)
             eotshake = 1;
        end
        1: begin
           dout1.valid = din1.valid;
           din1.ready = dout1.ready;
           if(handshake1 && &din1_s.eot)
             eotshake = 1;
        end
      endcase
   end

   always_ff @(posedge clk) begin
      if(rst) begin
         active_output_reg <= 0;
      end else if (eotshake) begin
         active_output_reg <= !active_output_reg;
      end
   end

endmodule : queue_one_by_one
