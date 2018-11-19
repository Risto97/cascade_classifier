import numpy as np
import cv2
from math import *


class ImageClass(object):
    def __init__(self):
        self.img_size = (0, 0)
        self.img_marked = []
        self.img_scaled = 0
        self.orig_img = []
        self.img = []
        self.scaleFactor = 1
        self.factor = 1
        self.bounding_box_factor = 0

    def imageScaler(self):
        self.img_scaled = 1
        self.factor = self.factor * self.scaleFactor

        src_size = self.orig_img.shape
        self.img_size = (int(src_size[0] / self.factor),
                         int(src_size[1] / self.factor))

        self.bounding_box_factor = src_size[0] / self.img_size[0]
        w1 = int(src_size[1])
        h1 = int(src_size[0])
        w2 = int(self.img_size[1])
        h2 = int(self.img_size[0])
        self.img = np.zeros((h2, w2), dtype=('u2'))

        x_ratio = int((w1 << 16) / w2 + 1)
        y_ratio = int((h1 << 16) / h2 + 1)

        for i in range(h1):
            for j in range(w1):
                if j < w2 and i < h2:
                    self.img[i][j] = self.orig_img[(i * y_ratio)
                                                   >> 16][(j * x_ratio) >> 16]

        return self.img

    def loadImage(self, fn):
        self.orig_img = cv2.imread(fn, 0)
        self.img = self.orig_img
        self.img_marked = cv2.imread(fn)
        self.img_size = self.orig_img.shape
        self.img_scaled = 0
        self.factor = 1

    def dumpArrayC(self, fn):
        f = open(fn, "w")
        WIDTH = img.img_size[1]
        HEIGHT = img.img_size[0]
        print(f"#ifndef SLIKA_HPP", file=f)
        print(f"#define SLIKA_HPP\n", file=f)
        print(f"#include <stdint.h>\n", file=f)
        print(f"const int WIDTH = {WIDTH};", file=f)
        print(f"const int HEIGHT = {HEIGHT};\n", file=f)
        print(f"uint8_t img[{HEIGHT}][{WIDTH}]=", end='', file=f)
        print("{", file=f)

        for y in range(HEIGHT):
            print("{", end='', file=f)
            for x in range(WIDTH):
                if x < WIDTH - 1:
                    print(f"{img.img[y][x]}", end=',', file=f)
                else:
                    print(f"{img.img[y][x]}", end='', file=f)

            if y < HEIGHT - 1:
                print("},", end="\n\n", file=f)
            else:
                print("}\n};", file=f)

        print(f"\n#endif", file=f)

    def dumpVerilogROM(self, fn):
        f = open(fn, "w")

        img_width = self.img_size[1]
        img_height = self.img_size[0]
        addr_w = ceil(log(img_height*img_width, 2))
        data_w = self.img[0][0].nbytes*8
        hex_w = data_w//4

        print(f"module bram_rom", file=f)
        print(f"  #(", file=f)
        print(f"     parameter W_DATA = {data_w},", file=f)
        print(f"     parameter W_ADDR = {addr_w}", file=f)
        print(f"     )", file=f)
        print(f"    (", file=f)
        print(f"     input clk,\n     input rst,\n\n     input en1,\n     input [W_ADDR-1:0] addr1,\n     output reg [W_DATA-1:0] data1\n", file=f)
        # print(f"     input en2,\n     input [W_ADDR-1:0] addr2,\n     output reg [W_DATA-1:0] data2", file=f)
        print(f"     );", file=f)

        print(f"\n     (* rom_style = \"block\" *)\n", file=f)

        for i in range(1,2):
            print(f"     always_ff @(posedge clk)\n        begin\n           if(en{i})\n             case(addr{i})",file=f)

            for y in range(self.img_size[0]):
                for x in range(self.img_size[1]):
                    addr = y*(self.img_size[1]) + x
                    addr_str = format(addr,f'0{addr_w}b')
                    str = format(self.img[y][x],f'0{hex_w}x')
                    print(f'               {addr_w}\'b{addr_str}: data{i} <= {data_w}\'h{str};', file=f)

            print(f"               default: data{i} <= 0;", file=f)
            print(f"           endcase", file=f)
            print(f"        end", file=f)

        print(f"\nendmodule: bram_rom", file=f)

        pass

if __name__ == "__main__":
    img_fn = 'datasets/rtl2.jpg'
    img = ImageClass()
    img.loadImage(img_fn)

    # img.dumpArrayC("c/slika.hpp")
    img.dumpVerilogROM("rtl/top/bram_rom.sv")

    # import time
    # start_time = time.time()
    # slika = np.zeros(img.img_size, dtype='u2')
    # for y in range(img.img_size[0]):
    #     for x in range(img.img_size[1]):
    #         slika[y][x] = img.img[y][x]

    # print("--- Time --------- %s ms ---" %
    #       (time.time() * 1000 - start_time * 1000))

#include <ctime>
