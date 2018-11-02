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
        print(f"const unsigned int feature_h = {self.featureSize[0]};", file=f)
        print(
            f"const unsigned int feature_w = {self.featureSize[1]};\n", file=f)

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


        print(f"const signed int featureThresholds[{self.featuresNum}]=", end='{', file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum-1:
                    print(f"{feature.threshold}", end = '', file=f)
                else:
                    print(f"{feature.threshold}", end = ',', file=f)
        print("};\n", file=f)

        print(
            f"const signed int passVal[{self.featuresNum}]=",
            end='{', file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum-1:
                    print(f"{feature.passVal}", end='', file=f)
                else:
                    print(f"{feature.passVal}", end=',', file=f)
        print("};\n", file=f)

        print(
            f"const signed int failVal[{self.featuresNum}]=",
            end='{', file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum-1:
                    print(f"{feature.failVal}", end='', file=f)
                else:
                    print(f"{feature.failVal}", end=',', file=f)
        print("};\n", file=f)

        for i in range(self.maxRectCount):
            print(f"const signed int weight{i}[{self.featuresNum}]=", end='{', file=f)
            for stage in self.stages:
                for feature in stage.features:
                    try:
                        if feature.featureNum == self.featuresNum-1:
                            print(f"{feature.rects[i].weight}", end='', file=f)
                        else:
                            print(f"{feature.rects[i].weight}", end=',', file=f)
                    except:
                        if feature.featureNum == self.featuresNum-1:
                            print(f"0", end='', file=f)
                        else:
                            print(f"0", end=',', file=f)
            print("};\n", file=f)

        for i in range(self.maxRectCount):
            print(f"const unsigned int rect{i}[{self.featuresNum}][4][2]=", end='{', file=f)
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
                        if feature.featureNum == self.featuresNum-1:
                            print("}", end='', file=f)
                        else:
                            print("}", end=',', file=f)

                    except:
                        if feature.featureNum == self.featuresNum-1:
                            print("{{0,0},{0,0},{0,0},{0,0}}", end='', file=f)
                        else:
                            print("{{0,0},{0,0},{0,0},{0,0}}", end=',', file=f)

            print("};\n", file=f)

        print(f"\n#endif", file=f)


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


if __name__ == "__main__":
    from create_cascade import createCascade
    import xmltodict

    fn = 'c/cascade.hpp'
    xml_file = r"haarcascade_frontalface_default.xml"
    with open(xml_file) as fd:
        doc = xmltodict.parse(fd.read())

    cascade = createCascade(doc)

    cascade.dumpCpp(fn)
