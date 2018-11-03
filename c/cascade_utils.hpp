#ifndef CASCADE_UTILS_HPP
#define CASCADE_UTILS_HPP

#include <stdint.h>
#include "image_utils.hpp"


int detectFrame(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
           int64_t stddev);

int stageRes(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
             int64_t stddev,
             unsigned int feature_start,
             unsigned int stage_num);


int featureRes(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
               int feature_num,
               int64_t stddev);



#endif
