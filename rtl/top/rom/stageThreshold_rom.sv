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
               5'b00000: data1 <= -11'h202;
               5'b00001: data1 <= -11'h1fc;
               5'b00010: data1 <= -11'h1da;
               5'b00011: data1 <= -11'h1c6;
               5'b00100: data1 <= -11'h1bf;
               5'b00101: data1 <= -11'h1a5;
               5'b00110: data1 <= -11'h19a;
               5'b00111: data1 <= -11'h18c;
               5'b01000: data1 <= -11'h187;
               5'b01001: data1 <= -11'h174;
               5'b01010: data1 <= -11'h18a;
               5'b01011: data1 <= -11'h17b;
               5'b01100: data1 <= -11'h16b;
               5'b01101: data1 <= -11'h179;
               5'b01110: data1 <= -11'h15d;
               5'b01111: data1 <= -11'h166;
               5'b10000: data1 <= -11'h16e;
               5'b10001: data1 <= -11'h15a;
               5'b10010: data1 <= -11'h14a;
               5'b10011: data1 <= -11'h147;
               5'b10100: data1 <= -11'h14e;
               5'b10101: data1 <= -11'h152;
               5'b10110: data1 <= -11'h14c;
               5'b10111: data1 <= -11'h157;
               5'b11000: data1 <= -11'h131;
               default: data1 <= 0;
           endcase
        end

endmodule: stageThreshold_rom
