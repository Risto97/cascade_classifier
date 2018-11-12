import math

class SqrtClass(object):
    def __init__(self):
        self.w_din = 31
        self.depth = 255

    @property
    def step(self):
        return 2**self.w_din // self.depth

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
        print(math.sqrt(num))
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

test = [632423816, 55374038]

sqrt = SqrtClass()
sqrt.w_din = 31
sqrt.depth = 256

sqrt.dumpC("c/sqrt.hpp")
print(sqrt.getSqrt(test[0]))
