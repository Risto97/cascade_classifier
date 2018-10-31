class CascadeClass(object):
    def __init__(self):
        self.stageNum = 0
        self.stageType = None
        self.featureType = None
        self.featureSize = (0, 0)
        self.maxWeakCount = 0
        self.maxCatCount = 0
        self.stages = []


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

    def relativeIndex(self):
        relIndex = range(self.featuresIndex[0] - self.featuresIndex[0],
                              self.featuresIndex[-1]+1 - self.featuresIndex[0])

        return relIndex


class FeatureClass(object):
    def __init__(self):
        self.featureNum = 0
        self.rectCount = 0
        self.passVal = 0
        self.failVal = 0
        self.threshold = 0
        self.rects = []


class RectClass(object):
    def __init__(self):
        self.A = {'x': 0, 'y': 0}
        self.B = {'x': 0, 'y': 0}
        self.C = {'x': 0, 'y': 0}
        self.D = {'x': 0, 'y': 0}
        self.weight = 0
