module stageThreshold_rom
  #(
     W_DATA = 11,
     DEPTH = 25,
     W_ADDR = 5
     )
    (
     input clk,
     input rst,

     input ena,
     input [W_ADDR-1:0] addra,
     output [W_DATA-1:0] doa
    );

     logic [W_DATA-1:0] mem [DEPTH-1:0];

     always_ff @(posedge clk)
        begin
           if(ena)
              doa = mem[addra];
        end

     initial begin
         mem[0] = -11'h202;
         mem[1] = -11'h1fc;
         mem[2] = -11'h1da;
         mem[3] = -11'h1c6;
         mem[4] = -11'h1bf;
         mem[5] = -11'h1a5;
         mem[6] = -11'h19a;
         mem[7] = -11'h18c;
         mem[8] = -11'h187;
         mem[9] = -11'h174;
         mem[10] = -11'h18a;
         mem[11] = -11'h17b;
         mem[12] = -11'h16b;
         mem[13] = -11'h179;
         mem[14] = -11'h15d;
         mem[15] = -11'h166;
         mem[16] = -11'h16e;
         mem[17] = -11'h15a;
         mem[18] = -11'h14a;
         mem[19] = -11'h147;
         mem[20] = -11'h14e;
         mem[21] = -11'h152;
         mem[22] = -11'h14c;
         mem[23] = -11'h157;
         mem[24] = -11'h131;
     end

endmodule: stageThreshold_rom
