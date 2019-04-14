from cascade_classifier.python_utils.cascade import CascadeClass
from cascade_classifier.python_utils.sqrt_approx import SqrtClass
import math


class CascadeHW(object):
    def __init__(self, xml_file, img_size):
        self.sw_model = CascadeClass(xml_file)

        self.img_size = img_size
        self.scale_factor = 1 / 0.75
        self.sqrt_mem_depth = 256

    @property
    def frame_size(self):
        '''frame_size: dimensions of frame'''
        return (self.sw_model.featureSize[0] + 1,
                self.sw_model.featureSize[1] + 1)

    @property
    def stage_num(self):
        '''stage_num: number of all stages in model'''
        return self.sw_model.stageNum

    @property
    def feature_num(self):
        '''feature_num: number of all features in model'''
        return self.sw_model.featuresNum

    @property
    def rect_num(self):
        '''max number of rects in feature'''  #TODO extract it from model
        return 3

    @property
    def w_img_addr(self):
        '''w_img_addr: width of address for img_ram'''
        return math.ceil(math.log(self.img_size[0] * self.img_size[1], 2))

    @property
    def w_rect_coord_rel(self):
        '''width of relative rect coord address'''
        return math.ceil(math.log(max(self.frame_size), 2))

    @property
    def w_rect_data(self):
        '''rect_rom location width'''
        return 4 * self.w_rect_coord_rel

    @property
    def rects_mem(self):
        """
        Returns list of all packed rect mem.
        A (linear coord) | width | height
        """
        rects_l = []
        for r in range(self.rect_num):
            rects_l.append(self.getRectMem(r))

        return rects_l

    def getRectMem(self, rect_num):
        """
        Returns list of packed rect mem.
        A (linear coord) | width | height
        """
        w_rect_rel = self.w_rect_coord_rel
        r = rect_num

        rect_l = []
        for s, stage in enumerate(self.sw_model.stages):
            for feature in stage.features:
                try:
                    A = [feature.rects[r].A['x'], feature.rects[r].A['y']]
                    D = [feature.rects[r].D['x'], feature.rects[r].D['y']]
                    if (A[0] > D[0] | A[1] > D[1]):
                        print(
                            "A is not top left corner, or D is not bottom right corner"
                        )
                except:
                    A = [0, 0]
                    D = [0, 0]

                width = D[0] - A[0]
                height = D[1] - A[1]

                rect_ccat = (A[0] + A[1] * self.frame_size[1]) << (
                    w_rect_rel * 2)
                rect_ccat |= width << w_rect_rel
                rect_ccat |= height

                rect_l.append(rect_ccat)

        return rect_l

    @property
    def w_weight(self):
        '''width of weight data'''  #TODO extract it from model
        return 3

    @property
    def weights_mem(self):
        """
        Returns list of all rect weights.
        Signed data
        """
        weights_l = []
        for r in range(self.rect_num):
            weights_l.append(self.getRectWeights(r))

        return weights_l

    def getRectWeights(self, rect_num):
        """
        Returns list of rect weights.
        Signed data
        """
        r = rect_num
        weights_l = []
        for s, stage in enumerate(self.sw_model.stages):
            for feature in stage.features:
                try:
                    weight = feature.rects[r].weight // 4096
                except:
                    weight = 0
                weights_l.append(weight)

        return weights_l

    @property
    def w_features_stage_count(self):
        '''width of feature stage count limits mem'''
        feature_num = []
        accum = 0
        for stage in self.sw_model.stages:
            accum += stage.maxWeakCount
            feature_num.append(accum)

        return math.ceil(math.log(max(feature_num), 2)) * 2

    @property
    def features_stage_count_mem(self):
        """
        Returns concatenated lower and upper features stage count limits,
        calculates data_w for ROM memory.
        used for PyGears implementation feature_cnt ROM memory
        """
        feature_num = []
        accum = 0
        for stage in self.sw_model.stages:
            accum += stage.maxWeakCount
            feature_num.append(accum)

        w_data = math.ceil(math.log(max(feature_num), 2))

        data_l = []
        for i in range(len(feature_num)):
            if i == 0:
                temp = (0 << w_data) | feature_num[i]
            else:
                temp = (feature_num[i - 1] << w_data) | feature_num[i]

            data_l.append(temp)

        return data_l

    @property
    def w_stage_threshold(self):
        '''width of stage_threshold_mem data'''
        threshold = self.stage_threshold_mem
        max_data = max(abs(max(threshold)), abs(min(threshold)))
        return math.ceil(math.log(max_data, 2)) + 1

    @property
    def stage_threshold_mem(self):
        '''stage_threshold_mem data'''
        threshold = []
        for stage in self.sw_model.stages:
            threshold.append(stage.stageThreshold)
        return threshold

    @property
    def w_feature_threshold(self):
        '''width of feature_threshold_mem data'''
        threshold = self.feature_threshold_mem
        max_data = max(abs(max(threshold)), abs(min(threshold)))
        return math.ceil(math.log(max_data, 2)) + 1

    @property
    def feature_threshold_mem(self):
        '''feature_threshold_mem data'''
        threshold = []
        for stage in self.sw_model.stages:
            for feature in stage.features:
                threshold.append(feature.threshold)
        return threshold

    @property
    def w_leaf_vals(self):
        '''width of leaf vals'''
        leaf_vals = self.leaf_vals_mem
        max_data0 = max(abs(max(leaf_vals[0])), abs(min(leaf_vals[0])))
        max_data1 = max(abs(max(leaf_vals[1])), abs(min(leaf_vals[1])))
        max_data = max(max_data0, max_data1)
        return math.ceil(math.log(max_data, 2)) + 1

    @property
    def leaf_vals_mem(self):
        '''leaf_vals_mem data'''
        leaf_vals = []
        for i in range(2):
            leaf_vals.append(self.getLeafVals(i))
        return leaf_vals

    def getLeafVals(self, leaf_num):
        # TODO fix passVal and failVal name
        leafVal = []
        for stage in self.sw_model.stages:
            for feature in stage.features:
                if leaf_num == 0:
                    leafVal.append(feature.passVal)
                elif leaf_num == 1:
                    leafVal.append(feature.failVal)

        return leafVal

    @property
    def scale_num(self):
        '''scaleNum: scale image scaleNum times'''
        return self.calc_scale_params()['scaleNum']

    @property
    def w_ratio(self):
        '''width of ratio parameter'''
        return max(
            math.ceil(math.log(max(self.x_ratio), 2)),
            math.ceil(math.log(max(self.y_ratio), 2)))

    @property
    def x_ratio(self):
        '''x_ratio, y_ratio: ratio for fixed point addr scaling'''
        return self.calc_scale_params()['x_ratio']

    @property
    def y_ratio(self):
        '''x_ratio, y_ratio: ratio for fixed point addr scaling'''
        return self.calc_scale_params()['y_ratio']

    @property
    def w_boundary(self):
        '''width of boundary parameter'''
        return max(
            math.ceil(math.log(max(self.boundary_x), 2)),
            math.ceil(math.log(max(self.boundary_y), 2))) + 1

    @property
    def boundary_x(self):
        '''boundary_x, boundary_y: boundaries for hopper'''
        return self.calc_scale_params()['boundary_x']

    @property
    def boundary_y(self):
        '''boundary_x, boundary_y: boundaries for hopper'''
        return self.calc_scale_params()['boundary_y']

    def calc_scale_params(self):
        """ Calculate all scale params for rd_addrgen
        scaleNum: scale image scaleNum times
        x_ratio, y_ratio: ratio for fixed point addr scaling
        boundary_x, boundary_y: boundaries for hopper
        """
        scale_num = 0
        frame, img_size = self.frame_size, self.img_size
        height, width = self.img_size[0], self.img_size[1]
        factor = self.scale_factor

        x_ratio, y_ratio, boundary_x, boundary_y = [], [], [], []
        boundary_x.append(img_size[1] - frame[1])
        boundary_y.append(img_size[0] - frame[0])
        while (height > frame[0] and width > frame[1]):
            x_ratio_tmp = int((img_size[1] << 16) / width) + 1
            boundary_x_tmp = int(width / factor - frame[1])
            x_ratio.append(x_ratio_tmp)
            boundary_x.append(boundary_x_tmp)

            y_ratio_tmp = int((img_size[0] << 16) / height) + 1
            boundary_y_tmp = int(height / factor - frame[0])
            y_ratio.append(y_ratio_tmp)
            boundary_y.append(boundary_y_tmp)

            height = int(height / factor)
            width = int(width / factor)
            scale_num += 1

        return {
            'scaleNum': scale_num,
            'x_ratio': x_ratio,
            'y_ratio': y_ratio,
            "boundary_x": boundary_x[:-1],
            "boundary_y": boundary_y[:-1]
        }

    ### TODO SQRT needs reconsidering ###
    ### probably delete sqrt_approx file and place it here ####

    @property
    def w_sqrt_din(self):
        '''TODO I forgot what this is'''
        return 31

    @property
    def sqrt_step(self):
        '''sqrt resolution'''
        return 2**self.w_sqrt_din // self.sqrt_mem_depth

    @property
    def sqrt_shift(self):
        '''sqrt shift din data to fit sqrt_mem depth'''
        return math.ceil(math.log(self.sqrt_step, 2))

    @property
    def w_sqrt(self):
        return math.ceil(math.log(max(self.sqrt_mem), 2))

    @property
    def sqrt_mem(self):
        sqrt = SqrtClass(w_din=self.w_sqrt_din, depth=self.sqrt_mem_depth).lut
        return sqrt


# xml_file = r"../xml_models/haarcascade_frontalface_default.xml"
# cascade_hw = CascadeHW(xml_file, img_size=(240, 320))
# print(cascade_hw.features_stage_count_mem)
# print(cascade_hw.w_features_stage_count)
# print(cascade_hw.w_img_addr)
# print(cascade_hw.feature_num)
# print(cascade_hw.stage_num)
# print(cascade_hw.frame_size)
# print(len(cascade_hw.rects_mem))
# print(len(cascade_hw.weights_mem))
# print(cascade_hw.w_rect_data)
# print(cascade_hw.w_stage_threshold)
# print(cascade_hw.stage_threshold_mem)
# print(len(cascade_hw.feature_threshold_mem))
# print(cascade_hw.w_feature_threshold)
# print(cascade_hw.w_leaf_vals)
# print(len(cascade_hw.leaf_vals_mem[0]))
# print(cascade_hw.x_ratio)
# print(cascade_hw.y_ratio)
# print(cascade_hw.scale_num)
# print(cascade_hw.boundary_x)
# print(cascade_hw.boundary_y)
# print(cascade_hw.w_boundary)
# print(cascade_hw.w_ratio)
# print(cascade_hw.sqrt_mem)
# print(cascade_hw.w_sqrt)
# print(cascade_hw.sqrt_step)
# print(cascade_hw.w_sqrt_din)
# print(cascade_hw.sqrt_shift)
