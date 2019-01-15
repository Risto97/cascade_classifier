import math
from VerilogROM import dumpVerilogROM


class CascadeClass(object):
    def __init__(self):
        self.stageNum = 0
        self.stageType = None
        self.featureType = None
        self.featureSize = (0, 0)
        self.maxWeakCount = 0
        self.maxCatCount = 0
        self.stages = []

    def detect(self, img, stddev):
        stage_res = 0
        for stage in self.stages:
            stage_res = stage.getResult(img, stddev)

            if stage_res is False:
                return False

        return True

    def dumpCpp(self, fn):
        f = open(fn, "w")

        print(f"#ifndef CASCADE_HPP", file=f)
        print(f"#define CASCADE_HPP\n", file=f)

        print(f"const unsigned int stageNum = {self.stageNum};", file=f)
        print(
            f"const unsigned int maxWeakCount = {self.maxWeakCount};", file=f)
        print(
            f"const unsigned int FRAME_HEIGHT = {self.featureSize[0]+1};",
            file=f)
        print(
            f"const unsigned int FRAME_WIDTH = {self.featureSize[1]+1};\n",
            file=f)

        print(
            f"const unsigned int stagesFeatureCount[{self.stageNum}]=",
            end='{',
            file=f)

        for stage in self.stages:
            if stage.stageIndex < self.stageNum - 1:
                print(f"{stage.maxWeakCount}", end=',', file=f)
            else:
                print(f"{stage.maxWeakCount}", end='', file=f)
        print("};\n", file=f)

        print(
            f"const signed int stageThresholds[{self.stageNum}]=",
            end='{',
            file=f)
        for stage in self.stages:
            if stage.stageIndex < self.stageNum - 1:
                print(f"{int(stage.stageThreshold)}", end=',', file=f)
            else:
                print(f"{int(stage.stageThreshold)}", end='', file=f)
        print("};\n", file=f)

        print(
            f"const signed int featureThresholds[{self.featuresNum}]=",
            end='{',
            file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum - 1:
                    print(f"{feature.threshold}", end='', file=f)
                else:
                    print(f"{feature.threshold}", end=',', file=f)
        print("};\n", file=f)

        print(
            f"const signed int passVal[{self.featuresNum}]=", end='{', file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum - 1:
                    print(f"{feature.passVal}", end='', file=f)
                else:
                    print(f"{feature.passVal}", end=',', file=f)
        print("};\n", file=f)

        print(
            f"const signed int failVal[{self.featuresNum}]=", end='{', file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum - 1:
                    print(f"{feature.failVal}", end='', file=f)
                else:
                    print(f"{feature.failVal}", end=',', file=f)
        print("};\n", file=f)

        for i in range(self.maxRectCount):
            print(
                f"const signed int weight{i}[{self.featuresNum}]=",
                end='{',
                file=f)
            for stage in self.stages:
                for feature in stage.features:
                    try:
                        if feature.featureNum == self.featuresNum - 1:
                            print(f"{feature.rects[i].weight}", end='', file=f)
                        else:
                            print(
                                f"{feature.rects[i].weight}", end=',', file=f)
                    except:
                        if feature.featureNum == self.featuresNum - 1:
                            print(f"0", end='', file=f)
                        else:
                            print(f"0", end=',', file=f)
            print("};\n", file=f)

        for i in range(self.maxRectCount):
            print(
                f"const unsigned int rect{i}[{self.featuresNum}][4][2]=",
                end='{',
                file=f)
            for stage in self.stages:
                for feature in stage.features:
                    try:
                        strA = f"{feature.rects[i].A['x']},{feature.rects[i].A['y']}" + "}"
                        strB = "{" + f"{feature.rects[i].B['x']},{feature.rects[i].B['y']}" + "}"
                        strC = "{" + f"{feature.rects[i].C['x']},{feature.rects[i].C['y']}" + "}"
                        strD = "{" + f"{feature.rects[i].D['x']},{feature.rects[i].D['y']}" + "}"
                        concat = f"{strA},{strB},{strC},{strD}"
                        print("{{", end='', file=f)
                        print(concat, end='', file=f)
                        if feature.featureNum == self.featuresNum - 1:
                            print("}", end='', file=f)
                        else:
                            print("}", end=',', file=f)

                    except:
                        if feature.featureNum == self.featuresNum - 1:
                            print("{{0,0},{0,0},{0,0},{0,0}}", end='', file=f)
                        else:
                            print("{{0,0},{0,0},{0,0},{0,0}}", end=',', file=f)

            print("};\n", file=f)

        print(f"\n#endif", file=f)

    def dumpFeatureCountVerilogROM(self,
                                   directory,
                                   dual_port=False,
                                   block_ram=False):
        names = ["featureCount"]
        if (directory[-1] != '/'):
            directory = directory + '/'

        feature_num = []
        accum = 0
        for stage in self.stages:
            accum += stage.maxWeakCount
            feature_num.append(accum)

        data_l = [feature_num]
        w_data_l = [math.ceil(math.log(self.maxWeakCount, 2))]
        w_addr_l = [math.ceil(math.log(len(feature_num), 2))]

        dumpVerilogROM(
            data_l,
            w_addr_l,
            w_data_l,
            names,
            directory,
            dual_port=dual_port,
            block_ram=block_ram)

    def getStageThreshold(self):
        threshold = []
        for stage in self.stages:
            threshold.append(stage.stageThreshold)

        max_data = max(abs(max(threshold)), abs(min(threshold)))
        w_data = math.ceil(math.log(max_data, 2)) + 1

        return threshold, w_data

    def dumpStageVerilogROM(self, directory, dual_port=False, block_ram=False):
        names = ["stageThreshold"]
        if (directory[-1] != '/'):
            directory = directory + '/'
        if dual_port is True:
            ports = 2
        else:
            ports = 1

        threshold = []
        for stage in self.stages:
            threshold.append(int(stage.stageThreshold))
        data_l = [threshold]

        max_threshold = max(abs(max(threshold)), abs(min(threshold)))
        w_data_l = [math.ceil(math.log(max_threshold, 2) + 1)]
        w_addr_l = [math.ceil(math.log(self.stageNum, 2))]
        w_hex_l = [math.ceil(math.log(w_data_l[0], 2))]

        dumpVerilogROM(
            data_l,
            w_addr_l,
            w_data_l,
            names,
            directory,
            dual_port=dual_port,
            block_ram=block_ram)

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

    def dumpFeatureVerilogROM(self, directory, dual_port=False,
                              block_ram=True):
        names = ["leafVal0", "leafVal1", "featureThreshold"]
        leafVal1 = []
        leafVal0 = []
        threshold = []
        for stage in self.stages:
            for feature in stage.features:
                leafVal1.append(feature.failVal)
                leafVal0.append(feature.passVal)
                threshold.append(feature.threshold)

        data_l = [leafVal0, leafVal1, threshold]

        max_leafVal = max(
            max(abs(max(leafVal1)), abs(min(leafVal1))),
            max(abs(max(leafVal0)), abs(min(leafVal0))))
        max_threshold = max(abs(max(threshold)), abs(min(threshold)))
        w_data_l = [
            math.ceil(math.log(max_leafVal, 2)) + 1,
            math.ceil(math.log(max_leafVal, 2)) + 1,
            math.ceil(math.log(max_threshold, 2) + 1)
        ]
        w_addr_l = [math.ceil(math.log(len(data_l[0]), 2))] * 3

        dumpVerilogROM(
            data_l,
            w_addr_l,
            w_data_l,
            names,
            directory,
            dual_port=dual_port,
            block_ram=block_ram)

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

                rect_ccat = (A[0] + A[1] *
                             (self.featureSize[1] + 1)) << (w_rect * 2) # TODO feature_size should be +1 in cascade class
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

    ## Dumped format for rect is {A, width, height} = Tuple[Uint[2*w_rect], Uint[w_rect], Uint[w_rect]]
    def dumpRectVerilogROM(self, directory, dual_port=False, block_ram=False):
        for r in range(3):
            names = [f"rect{r}", f"weights{r}"]
            rect_l = []
            weight_l = []
            max_feature_size = max(self.featureSize)
            w_rect = math.ceil(math.log(max_feature_size, 2))
            w_data_l = [4 * w_rect, 3]

            for s, stage in enumerate(self.stages):
                for feature in stage.features:
                    try:
                        A = [feature.rects[r].A['x'], feature.rects[r].A['y']]
                        D = [feature.rects[r].D['x'], feature.rects[r].D['y']]
                        weight = feature.rects[r].weight // 4096
                        if (A[0] > D[0] | A[1] > D[1]):
                            print(
                                "A is not top left corner, or D is not bottom right corner"
                            )
                    except:
                        weight = 0
                        A = [0, 0]
                        D = [0, 0]

                    width = D[0] - A[0]
                    height = D[1] - A[1]

                    rect_ccat = (A[0] + A[1] *
                                 (self.featureSize[1] + 1)) << (w_rect * 2)
                    rect_ccat |= width << w_rect
                    rect_ccat |= height
                    # rect_l.extend((A[0], A[1], width, height))
                    rect_l.append(rect_ccat)
                    weight_l.append(weight)

                data_l = [rect_l, weight_l]
                w_addr_l = [
                    math.ceil(math.log(len(rect_l), 2)),
                    math.ceil(math.log(len(weight_l), 2))
                ]

            dumpVerilogROM(
                data_l,
                w_addr_l,
                w_data_l,
                names,
                directory,
                dual_port=dual_port,
                block_ram=block_ram)

    def dumpParamsVerilog(self, fn, img, scaleNum, x_ratio, y_ratio,
                          boundary_x, boundary_y):
        f = open(fn, "w")
        parallel_rows = 1
        ratio_max = max(max(x_ratio), max(y_ratio))
        w_ratio = math.ceil(math.log(ratio_max, 2))
        w_ratio = 24  #### ????????????????
        w_boundary = math.ceil(
            math.log(max(img.img.shape[0], img.img.shape[1]), 2))

        print(f"`ifndef PARAMS_SV", file=f)
        print(f"`define PARAMS_SV", file=f)
        print(f"package params;\n", file=f)
        print(f"parameter W_DATA = 8;", file=f)
        print(f"parameter IMG_WIDTH = {img.img.shape[1]};", file=f)
        print(f"parameter IMG_HEIGHT = {img.img.shape[0]};", file=f)
        print(f"parameter PARALLEL_ROWS = {parallel_rows};", file=f)
        print(f"parameter SCALE_NUM = {scaleNum};\n", file=f)

        print(f"parameter W_RATIO = {w_ratio};", file=f)
        print(f"parameter W_BOUNDARY = {w_boundary};\n", file=f)

        print(f"parameter [SCALE_NUM*W_RATIO-1:0] X_RATIO =", end='{', file=f)
        for enum, val in enumerate(reversed(x_ratio)):
            if (enum < len(x_ratio) - 1):
                print(f"{w_ratio}'d{val}", end=',', file=f)
            else:
                print(f"{w_ratio}'d{val}", end='};\n', file=f)

        print(f"parameter [SCALE_NUM*W_RATIO-1:0] Y_RATIO =", end='{', file=f)
        for enum, val in enumerate(reversed(y_ratio)):
            if (enum < len(y_ratio) - 1):
                print(f"{w_ratio}'d{val}", end=',', file=f)
            else:
                print(f"{w_ratio}'d{val}", end='};\n', file=f)

        print(
            f"\nparameter [SCALE_NUM*W_BOUNDARY-1:0] X_BOUNDARY =",
            end='{',
            file=f)
        for enum, val in enumerate(reversed(boundary_x)):
            if (enum < len(boundary_x) - 1):
                print(f"{w_boundary}'d{val}", end=',', file=f)
            else:
                print(f"{w_boundary}'d{val}", end='};', file=f)

        print(
            f"\nparameter [SCALE_NUM*W_BOUNDARY-1:0] Y_BOUNDARY =",
            end='{',
            file=f)
        for enum, val in enumerate(reversed(boundary_y)):
            if (enum < len(boundary_y) - 1):
                print(f"{w_boundary}'d{val}", end=',', file=f)
            else:
                print(f"{w_boundary}'d{val}", end='};\n', file=f)

        print(f"\nendpackage: params", file=f)
        print(f"`endif", file=f)
        pass

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
    def __init__(self):
        self.stageIndex = 0
        self.maxWeakCount = 0
        self.stageThreshold = 0
        self.featuresIndex = range(0, self.maxWeakCount)
        self.features = []

    def calcSlice(self, cascade):
        slice_low = 0
        stage = cascade.stages[self.stageIndex - 1]
        slice_low += stage.featuresIndex[-1] + 1
        slice_high = slice_low + self.maxWeakCount

        self.featuresIndex = range(slice_low, slice_high)

    def getResult(self, img, stddev):
        sum = 0
        for feature in self.features:
            sum += feature.getResult(img, stddev)

        if sum < self.stageThreshold:
            return False
        else:
            return True


class FeatureClass(object):
    def __init__(self):
        self.featureNum = 0
        self.rectCount = 0
        self.passVal = 0
        self.failVal = 0
        self.threshold = 0
        self.rects = []

    def getResult(self, img, stddev):
        sum = 0
        for rect in self.rects:
            sum += rect.calcSum(img)

        if sum >= self.threshold * stddev:
            return self.passVal
        else:
            return self.failVal


class RectClass(object):
    def __init__(self):
        self.A = {'x': 0, 'y': 0}
        self.B = {'x': 0, 'y': 0}
        self.C = {'x': 0, 'y': 0}
        self.D = {'x': 0, 'y': 0}
        self.weight = 0

    def calcSum(self, img):
        img = img.frame_ii
        sum = img[self.A['y']][self.A['x']] + img[self.D['y']][self.D['x']] \
            - img[self.B['y']][self.B['x']] - img[self.C['y']][self.C['x']]

        sum *= self.weight

        return sum


def create_cascade(xml_file):
    from create_cascade import createCascade
    import xmltodict

    with open(xml_file) as fd:
        doc = xmltodict.parse(fd.read())
    cascade = createCascade(doc)

    return cascade


if __name__ == "__main__":
    from create_cascade import createCascade
    import xmltodict

    fn = 'c/cascade.hpp'
    xml_file = r"models/haarcascade_frontalface_default.xml"
    with open(xml_file) as fd:
        doc = xmltodict.parse(fd.read())

    cascade = createCascade(doc)

    cnt = 0
    for stage in cascade.stages[:1]:
        print("##########################")
        for feature in stage.features:
            print(cnt)
            Ax = feature.rects[0].A['x']
            Ay = feature.rects[0].A['y']
            Bx = feature.rects[0].B['x']
            By = feature.rects[0].B['y']
            Cx = feature.rects[0].C['x']
            Cy = feature.rects[0].C['y']
            Dx = feature.rects[0].D['x']
            Dy = feature.rects[0].D['y']
            A = Ax + Ay * 25
            B = Bx + By * 25
            C = Cx + Cy * 25
            D = Dx + Dy * 25
            weight = feature.rects[0].weight // 4096
            # print(Ax, Ay)
            # print(Bx, By)
            # print(Cx, Cy)
            # print(Dx, Dy)
            # print( Ax + Ay*25, Dx-Ax, Dy-Ay)
            print("A ", A, "B ", B, "C ", C, "D ", D, weight)

            #         # print(feature.rects[0].__dict__)
            # print(A,B,D,C, weight)
            Ax = feature.rects[1].A['x']
            Ay = feature.rects[1].A['y']
            Bx = feature.rects[1].B['x']
            By = feature.rects[1].B['y']
            Cx = feature.rects[1].C['x']
            Cy = feature.rects[1].C['y']
            Dx = feature.rects[1].D['x']
            Dy = feature.rects[1].D['y']
            A = Ax + Ay * 25
            B = Bx + By * 25
            C = Cx + Cy * 25
            D = Dx + Dy * 25
            weight = feature.rects[1].weight // 4096
            print("A ", A, "B ", B, "C ", C, "D ", D, weight)

            #         # print(feature.rects[0].__dict__)
            #         print(A,B,D,C, weight)
            try:
                Ax = feature.rects[2].A['x']
                Ay = feature.rects[2].A['y']
                Bx = feature.rects[2].B['x']
                By = feature.rects[2].B['y']
                Cx = feature.rects[2].C['x']
                Cy = feature.rects[2].C['y']
                Dx = feature.rects[2].D['x']
                Dy = feature.rects[2].D['y']
                A = Ax + Ay * 25
                B = Bx + By * 25
                C = Cx + Cy * 25
                D = Dx + Dy * 25
                weight = feature.rects[2].weight // 4096
            except:
                A = 0
                B = 0
                C = 0
                D = 0
                weight = 0
            print("A ", A, "B ", B, "C ", C, "D ", D, weight)

            # print(feature.rects[0].__dict__)
            print("----------------")
            cnt += 1

    # cascade.dumpParamsVerilog("rtl/top/params.sv")

    # cascade.dumpFeatureVerilogROM("rtl/top/rom/")
    # cascade.dumpRectVerilogROM("rtl/top/rom/")
    # cascade.dumpStageVerilogROM("rtl/top/rom/")

    # cascade.dumpCpp(fn)
