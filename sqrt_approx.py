import math

class SqrtClass(object):
    def __init__(self):
        self.w_din = 31
        self.depth = 256

    @property
    def step(self):
        return 2**self.w_din // self.depth

    @property
    def w_data(self):
        return math.ceil(math.log(math.sqrt(2**self.w_din),2))

    @property
    def w_addr(self):
        return math.ceil(math.log(self.depth,2))

    @property
    def lut(self):
        l = []
        for i in range(self.depth):
            num = i*self.step
            l.append(int(math.sqrt(num)))
        return l

    def getSqrt(self, num):
        if(num > 2**self.w_din):
            print(f"Input {num} overflow, max value {2**self.w_din}")
            print(f"Set w_din to {math.ceil(math.log(num,2))} instead")

        sqrt_lut = self.lut[num//self.step]
        if(sqrt_lut == 0):
            sqrt_lut = 1
        error = abs((sqrt_lut - math.sqrt(num)) / sqrt_lut * 100)
        return sqrt_lut, error

    def dumpC(self, fn):
        f = open(fn, "w")
        print(f"#ifndef SQRT_HPP", file=f)
        print(f"#define SQRT_HPP\n", file=f)
        print(f"#include <stdint.h>\n", file=f)

        print(f"uint32_t STEP = {self.step};", file=f)
        print(f"uint16_t DEPTH = {self.depth};", file=f)
        print(f"uint16_t W_DIN = {self.w_din};\n", file=f)

        print(f"uint32_t sqrt_lut[{self.depth}]=", end='{\n', file=f)
        for i in range(len(self.lut)):
            if(i < len(self.lut)-1):
                print(f"{self.lut[i]}", end=',', file=f)
            elif(i == len(self.lut)-1):
                print(f"{self.lut[i]}", end="};\n", file=f)

        print(f"\n#endif", file=f)

    def dumpVerilogROM(self, fn):
        f = open(fn, "w")

        hex_w = self.w_data//4

        print(f"module rom_mem", file=f)
        print(f"  #(", file=f)
        print(f"     W_DATA = {self.w_data},", file=f)
        print(f"     DEPTH = 64,", file=f)
        print(f"     W_ADDR = {self.w_addr}", file=f)
        print(f"     )", file=f)
        print(f"    (", file=f)
        print(f"     input clk,\n     input rst,\n\n     input ena,\n     input [W_ADDR-1:0] addra,\n     output [W_DATA-1:0] doa\n", file=f)
        print(f"     );", file=f)

        # print(f"\n     (* rom_style = \"block\" *)\n", file=f)
        print(f"\n     logic [W_DATA-1:0] mem [DEPTH-1:0];\n", file=f)

        print(f"     always_ff @(posedge clk)\n        begin\n           if(ena)",file=f)
        print(f"              doa = mem[addra];", file=f)
        print(f"        end\n", file=f)


        print(f"     initial begin", file=f)
        for i in range(len(self.lut)):
            str = format(self.lut[i],f'0{hex_w}x')
            print(f"         mem[{i}] = {self.w_data}\'h{str};", file=f)
        print(f"     end\n", file=f)


        # print(f"     always_ff @(posedge clk)\n        begin\n           if(ena)\n             case(addra)",file=f)
        # for i in range(len(self.lut)):
        #     addr = i
        #     addr_str = format(addr,f'0{self.w_addr}b')
        #     str = format(self.lut[i],f'0{hex_w}x')
        #     print(f'               {self.w_addr}\'b{addr_str}: doa <= {self.w_data}\'h{str};', file=f)

        # print(f"               default: doa <= 0;", file=f)
        # print(f"           endcase", file=f)
        # print(f"        end", file=f)

        print(f"\nendmodule: rom_mem", file=f)

        pass


def createSqrtApprox(w_din, depth):
    sqrt = SqrtClass()
    sqrt.w_din = 31
    sqrt.depth = 256

    w_data = math.ceil(math.log(max(sqrt.lut), 2))

    return sqrt.lut, w_data

test = [632423816, 55374038]

sqrt = SqrtClass()
sqrt.w_din = 31
sqrt.depth = 256
# print(sqrt.w_data)
# print(sqrt.w_addr)
# print(sqrt.step)

# print(sqrt.lut)

# sqrt.dumpC("c/sqrt.hpp")
# sqrt.dumpVerilogROM("pygears/gears/svlib/sqrt_rom_mem.sv")
# print(sqrt.getSqrt(test[0]))
