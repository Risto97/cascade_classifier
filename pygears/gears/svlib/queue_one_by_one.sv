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

   logic                active_output_reg;
   logic                eotshake;

   always_comb begin
      eotshake = 0;
      dout0.valid = 0;
      dout1.valid = 0;
      din0.ready = 0;
      din1.ready = 0;
      case(active_output_reg)
        0: begin
           din0.ready = dout0.ready;
           dout0_s = din0_s;
           dout0.valid = din0.valid;
           if(din0_s.eot && din0.valid)
             eotshake = 1;
        end
        1: begin
           din1.ready = dout1.ready;
           dout1_s = din1_s;
           dout1.valid = din1.valid;
           if(din1_s.eot && din1.valid)
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
