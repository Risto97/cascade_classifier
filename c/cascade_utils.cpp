#include "cascade.hpp"
#include <iostream>
#include <stdint.h>
#include "image_utils.hpp"
#include "cascade_utils.hpp"
#include "cascade.hpp"


int detect(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
           int64_t stddev){

  unsigned int feature_start = 0;
  int result = 0;

  for(unsigned int stage_num = 0; stage_num < stageNum; stage_num++){
    result = stageRes(ii, stddev, feature_start, stage_num);
    if(result == -1) return -1;

    feature_start += stagesFeatureCount[stage_num];
  }
  return 1;
}

int stageRes(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
             int64_t stddev,
             unsigned int feature_start,
             unsigned int stage_num){
  unsigned int feature_num;
  int64_t sum = 0;

  for(feature_num = feature_start;
      feature_num < feature_start + stagesFeatureCount[stage_num];
      feature_num++){
    sum += featureRes(ii, feature_num, stddev);
  }

  if(sum < stageThresholds[stage_num]) return -1;
  else return 1;
}

int featureRes(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
               int feature_num,
               int64_t stddev){
  int64_t sum1 = 0;
  int64_t sum2 = 0;
  int64_t sum3 = 0;
  int64_t sum = 0;

  sum1 += ii[rect0[feature_num][0][1]][rect0[feature_num][0][0]] +
          ii[rect0[feature_num][3][1]][rect0[feature_num][3][0]] -
          ii[rect0[feature_num][2][1]][rect0[feature_num][2][0]] -
          ii[rect0[feature_num][1][1]][rect0[feature_num][1][0]];
  sum1 *= weight0[feature_num];

  sum2 += ii[rect1[feature_num][0][1]][rect1[feature_num][0][0]] +
          ii[rect1[feature_num][3][1]][rect1[feature_num][3][0]] -
          ii[rect1[feature_num][2][1]][rect1[feature_num][2][0]] -
          ii[rect1[feature_num][1][1]][rect1[feature_num][1][0]];
  sum2 *= weight1[feature_num];

  sum3 += ii[rect2[feature_num][0][1]][rect2[feature_num][0][0]] +
          ii[rect2[feature_num][3][1]][rect2[feature_num][3][0]] -
          ii[rect2[feature_num][2][1]][rect2[feature_num][2][0]] -
          ii[rect2[feature_num][1][1]][rect2[feature_num][1][0]];
  sum3 *= weight1[feature_num];

  sum = sum1 + sum2 + sum3;

  if(sum >= featureThresholds[feature_num] * stddev) return passVal[feature_num];
  else return failVal[feature_num];

  return sum;
}
