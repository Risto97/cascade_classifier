module featureCount_rom
  #(
     W_DATA = 8,
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
         mem[0] =  8'h09;
         mem[1] =  8'h19;
         mem[2] =  8'h34;
         mem[3] =  8'h54;
         mem[4] =  8'h88;
         mem[5] =  8'hbd;
         mem[6] =  8'hfb;
         mem[7] =  8'h143;
         mem[8] =  8'h196;
         mem[9] =  8'h1f1;
         mem[10] =  8'h254;
         mem[11] =  8'h2c7;
         mem[12] =  8'h346;
         mem[13] =  8'h3cd;
         mem[14] =  8'h455;
         mem[15] =  8'h4de;
         mem[16] =  8'h57d;
         mem[17] =  8'h618;
         mem[18] =  8'h6c1;
         mem[19] =  8'h785;
         mem[20] =  8'h84a;
         mem[21] =  8'h8ff;
         mem[22] =  8'h9c6;
         mem[23] =  8'ha99;
         mem[24] =  8'hb61;
     end

endmodule: featureCount_rom
