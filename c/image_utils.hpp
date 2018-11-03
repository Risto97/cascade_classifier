#ifndef IMAGE_UTILS_HPP
#define IMAGE_UTILS_HPP

#include <stdint.h>
// #include "slika.hpp"
const int IMG_HEIGHT = 2048;
const int IMG_WIDTH = 2048;
const int FRAME_WIDTH = 25;
const int FRAME_HEIGHT = 25;

void imageScaler(uint8_t img_orig[IMG_HEIGHT][IMG_WIDTH],
                 uint8_t img_scaled[IMG_HEIGHT][IMG_WIDTH],
                 uint16_t src_height,
                 uint16_t src_width,
                 float factor);

void calcIntegralImages(uint8_t i[IMG_HEIGHT][IMG_WIDTH],
                        int x_start,
                        int y_start,
                        uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
                        uint64_t sii[FRAME_HEIGHT][FRAME_WIDTH]);

int64_t calcStddev(uint64_t sii[FRAME_HEIGHT][FRAME_WIDTH],
                   uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH]);

#endif
