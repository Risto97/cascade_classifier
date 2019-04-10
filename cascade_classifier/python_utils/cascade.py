import xmltodict
import math
from VerilogROM import dumpVerilogROM


class CascadeClass(object):
    def __init__(self, xml_file):
        with open(xml_file) as fd:
            doc = xmltodict.parse(fd.read())

        self.stageNum = int(doc['opencv_storage']['cascade']['stageNum'])
        self.stageType = doc['opencv_storage']['cascade']['stageType']
        self.featureType = doc['opencv_storage']['cascade']['featureType']
        self.featureSize = (int(doc['opencv_storage']['cascade']['height']),
                            int(doc['opencv_storage']['cascade']['width']))
        self.maxWeakCount = int(
            doc['opencv_storage']['cascade']['stageParams']['maxWeakCount'])
        self.maxCatCount = int(
            doc['opencv_storage']['cascade']['featureParams']['maxCatCount'])

        self.stage_slices = self.calc_stage_slices(doc)

        self.stages = []
        for i in range(self.stageNum):
            stage = StageClass(doc, i, self.stage_slices[i])
            self.stages.append(stage)

    def calc_stage_slices(self, doc):
        stage_slices = []
        slice_low = slice_high = 0
        for i in range(self.stageNum):
            stage_WeakCount = len(doc['opencv_storage']['cascade']['stages']
                                  ['_'][i]['weakClassifiers']['_'])
            slice_low = slice_high
            slice_high = slice_low + stage_WeakCount
            stage_slice = range(slice_low, slice_high)
            stage_slices.append(stage_slice)

        return stage_slices

    def detect(self, img, stddev):
        stage_res = 0
        for stage in self.stages:
            stage_res = stage.getResult(img, stddev)

            if stage_res is False:
                return False

        return True

    def getStageThreshold(self):
        threshold = []
        for stage in self.stages:
            threshold.append(stage.stageThreshold)

        max_data = max(abs(max(threshold)), abs(min(threshold)))
        w_data = math.ceil(math.log(max_data, 2)) + 1

        return threshold, w_data

    def getFeatureThresholds(self):
        threshold = []
        for stage in self.stages:
            for feature in stage.features:
                threshold.append(feature.threshold)

        max_data = max(abs(max(threshold)), abs(min(threshold)))
        w_data = math.ceil(math.log(max_data, 2)) + 1

        return threshold, w_data

    def getLeafVals(self, leaf_num):
        leafVal = []
        for stage in self.stages:
            for feature in stage.features:
                if leaf_num == 0:
                    leafVal.append(feature.passVal)
                elif leaf_num == 1:
                    leafVal.append(feature.failVal)

        max_data = max(abs(max(leafVal)), abs(min(leafVal)))
        w_data = math.ceil(math.log(max_data, 2)) + 1

        return leafVal, w_data

    def getRectCoords(self, rect_num):
        max_feature_size = max(self.featureSize)
        w_rect = math.ceil(math.log(max_feature_size, 2))
        r = rect_num

        rect_l = []
        for s, stage in enumerate(self.stages):
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

                rect_ccat = (A[0] + A[1] * (self.featureSize[1] + 1)) << (
                    w_rect * 2
                )  # TODO feature_size should be +1 in cascade class
                rect_ccat |= width << w_rect
                rect_ccat |= height

                rect_l.append(rect_ccat)

        w_data = 4 * w_rect

        return rect_l, w_data

    def getRectWeights(self, rect_num):
        r = rect_num
        w_data = 3

        weights_l = []
        for s, stage in enumerate(self.stages):
            for feature in stage.features:
                try:
                    weight = feature.rects[r].weight // 4096
                except:
                    weight = 0
                weights_l.append(weight)

        return weights_l, w_data

    @property
    def featuresNum(self):
        return self.stages[-1].featuresIndex[-1] + 1

    @property
    def maxRectCount(self):
        max_rect_count = 0
        for stage in self.stages:
            for feature in stage.features:
                if len(feature.rects) > max_rect_count:
                    max_rect_count = len(feature.rects)
        return max_rect_count

    def getFeatureStagesCount(self):
        feature_num = []
        accum = 0
        for stage in self.stages:
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

        return data_l, w_data * 2


class StageClass(object):
    def __init__(self, doc, num, features_slice):

        self.stageIndex = num
        self.maxWeakCount = int(doc['opencv_storage']['cascade']['stages']['_']
                                [num]['maxWeakCount'])
        self.stageThreshold = 0.4 * 255 * float(
            doc['opencv_storage']['cascade']['stages']['_'][num]
            ['stageThreshold'])

        self.featuresIndex = features_slice

        self.features = []
        for i in self.featuresIndex:
            rel_i = i - self.featuresIndex[0]
            feature = FeatureClass(doc, i, rel_i, self.stageIndex)
            self.features.append(feature)

    def getResult(self, img, stddev):
        sum = 0
        for feature in self.features:
            sum += feature.getResult(img, stddev)

        if sum < self.stageThreshold:
            return False
        else:
            return True


class FeatureClass(object):
    def __init__(self, doc, num, relative_index, stage_index):

        self.featureNum = num
        self.rectCount = len(doc['opencv_storage']['cascade']['features']['_']
                             [num]['rects']['_'])

        leafVal = doc['opencv_storage']['cascade']['stages']['_'][stage_index][
            'weakClassifiers']['_'][relative_index]['leafValues']
        leafVal = leafVal.split(" ")
        leafVal = [256 * float(leafVal[0]), 256 * float(leafVal[1])]

        self.passVal = int(leafVal[1])
        self.failVal = int(leafVal[0])

        self.threshold = doc['opencv_storage']['cascade']['stages']['_'][
            stage_index]['weakClassifiers']['_'][relative_index][
                'internalNodes']
        self.threshold = int(4096 * float(self.threshold.split(" ")[3]))

        rects_dict = doc['opencv_storage']['cascade']['features']['_'][
            self.featureNum]['rects']['_']
        self.rects = []
        for rect_dict in rects_dict:
            rect = RectClass(rect_dict)
            self.rects.append(rect)

    def getResult(self, img, stddev):
        sum = 0
        for rect in self.rects:
            sum += rect.calcSum(img)

        if sum >= self.threshold * stddev:
            return self.passVal
        else:
            return self.failVal


class RectClass(object):
    def __init__(self, r):
        if r[-1] == '.':
            r = r[:-1]
        r = r.split(" ")
        r = [int(x) for x in r]

        self.A = {'x': r[0], 'y': r[1]}
        self.B = {'x': r[0] + r[2], 'y': r[1]}
        self.C = {'x': r[0], 'y': r[1] + r[3]}
        self.D = {'x': r[0] + r[2], 'y': r[1] + r[3]}
        self.weight = r[4] * 4096

    def calcSum(self, img):
        img = img.frame_ii
        sum = img[self.A['y']][self.A['x']] + img[self.D['y']][self.D['x']] \
            - img[self.B['y']][self.B['x']] - img[self.C['y']][self.C['x']]

        sum *= self.weight

        return sum


if __name__ == "__main__":
    from dumpCpp import dumpCpp
    from dumpVerilog import *
    xml_file = r"../xml_models/haarcascade_frontalface_default.xml"

    cascade = CascadeClass(xml_file)

    print(cascade.stages[1].features[15].rects[0].__dict__)
    print(cascade.stageNum)

    dumpCpp(cascade, "hed.hpp")
    dumpFeatureCountVerilogROM(cascade, ".")
    dumpStageVerilogROM(cascade, ".")
    dumpParamsVerilog(cascade, "params.sv", (240,320), (25,25), 1/0.75)
