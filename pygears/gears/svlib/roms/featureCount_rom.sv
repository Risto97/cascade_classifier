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
         mem[1] =  8'h10;
         mem[2] =  8'h1b;
         mem[3] =  8'h20;
         mem[4] =  8'h34;
         mem[5] =  8'h35;
         mem[6] =  8'h3e;
         mem[7] =  8'h48;
         mem[8] =  8'h53;
         mem[9] =  8'h5b;
         mem[10] =  8'h63;
         mem[11] =  8'h73;
         mem[12] =  8'h7f;
         mem[13] =  8'h87;
         mem[14] =  8'h88;
         mem[15] =  8'h89;
         mem[16] =  8'h9f;
         mem[17] =  8'h9b;
         mem[18] =  8'ha9;
         mem[19] =  8'hc4;
         mem[20] =  8'hc5;
         mem[21] =  8'hb5;
         mem[22] =  8'hc7;
         mem[23] =  8'hd3;
         mem[24] =  8'hc8;
     end

endmodule: featureCount_rom
