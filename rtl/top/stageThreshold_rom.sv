module stageThreshold_rom
  #(
     parameter W_DATA = 11,
     parameter W_ADDR = 5
     )
    (
     input clk,
     input rst,

     input en1,
     input [W_ADDR-1:0] addr1,
     output reg [W_DATA-1:0] data1

     );
     always_ff @(posedge clk)
        begin
           if(en1)
             case(addr1)
               5'b00000: data1 <= -11'h0202;
               5'b00001: data1 <= -11'h01fc;
               5'b00010: data1 <= -11'h01da;
               5'b00011: data1 <= -11'h01c6;
               5'b00100: data1 <= -11'h01bf;
               5'b00101: data1 <= -11'h01a5;
               5'b00110: data1 <= -11'h019a;
               5'b00111: data1 <= -11'h018c;
               5'b01000: data1 <= -11'h0187;
               5'b01001: data1 <= -11'h0174;
               5'b01010: data1 <= -11'h018a;
               5'b01011: data1 <= -11'h017b;
               5'b01100: data1 <= -11'h016b;
               5'b01101: data1 <= -11'h0179;
               5'b01110: data1 <= -11'h015d;
               5'b01111: data1 <= -11'h0166;
               5'b10000: data1 <= -11'h016e;
               5'b10001: data1 <= -11'h015a;
               5'b10010: data1 <= -11'h014a;
               5'b10011: data1 <= -11'h0147;
               5'b10100: data1 <= -11'h014e;
               5'b10101: data1 <= -11'h0152;
               5'b10110: data1 <= -11'h014c;
               5'b10111: data1 <= -11'h0157;
               5'b11000: data1 <= -11'h0131;
               default: data1 <= 0;
           endcase
        end

endmodule: stageThreshold_rom
