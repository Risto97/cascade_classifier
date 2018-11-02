import xmltodict
from cascade import CascadeClass, StageClass, FeatureClass, RectClass


def createStage(num, doc, cascade):
    stage = StageClass()

    stage.stageIndex = num
    stage.maxWeakCount = int(
        doc['opencv_storage']['cascade']['stages']['_'][num]['maxWeakCount'])
    stage.stageThreshold = 0.4 * 255 * float(
        doc['opencv_storage']['cascade']['stages']['_'][num]['stageThreshold'])

    if num == 0:
        stage.featuresIndex = range(0, stage.maxWeakCount)
    else:
        stage.calcSlice(cascade)

    stage.features = createFeatures(stage, doc)

    return stage


def createFeatures(stage, doc):
    features = []
    for i in stage.featuresIndex:
        feature = FeatureClass()
        feature.featureNum = i
        feature.rectCount = len(
            doc['opencv_storage']['cascade']['features']['_'][i]['rects']['_'])
        relative_index = i - stage.featuresIndex[0]

        leafVal = doc['opencv_storage']['cascade']['stages']['_'][
            stage.stageIndex]['weakClassifiers']['_'][relative_index][
                'leafValues']
        leafVal = leafVal.split(" ")
        leafVal = [256 * float(leafVal[0]), 256 * float(leafVal[1])]
        feature.passVal = int(leafVal[1])
        feature.failVal = int(leafVal[0])
        feature.threshold = doc['opencv_storage']['cascade']['stages']['_'][
            stage.stageIndex]['weakClassifiers']['_'][relative_index][
                'internalNodes']
        feature.threshold = int(4096 * float(feature.threshold.split(" ")[3]))

        feature.rects = createRects(feature, doc)

        features.append(feature)

    return features


def createRects(feature, doc):
    rects = []

    rects_dict = doc['opencv_storage']['cascade']['features']['_'][
        feature.featureNum]['rects']['_']

    for r in rects_dict:
        rect = RectClass()
        if r[-1] == '.':
            r = r[:-1]
        r = r.split(" ")
        r = [int(x) for x in r]

        rect.A = {'x': r[0], 'y': r[1]}
        rect.B = {'x': r[0] + r[2], 'y': r[1]}
        rect.C = {'x': r[0], 'y': r[1] + r[3]}
        rect.D = {'x': r[0] + r[2], 'y': r[1] + r[3]}
        rect.weight = r[4] * 4096
        rects.append(rect)

    return rects


def createCascade(doc):
    cascade = CascadeClass()

    cascade.stageNum = int(doc['opencv_storage']['cascade']['stageNum'])
    cascade.stageType = doc['opencv_storage']['cascade']['stageType']
    cascade.featureType = doc['opencv_storage']['cascade']['featureType']
    cascade.featureSize = (int(doc['opencv_storage']['cascade']['height']),
                           int(doc['opencv_storage']['cascade']['width']))
    cascade.maxWeakCount = int(
        doc['opencv_storage']['cascade']['stageParams']['maxWeakCount'])
    cascade.maxCatCount = int(
        doc['opencv_storage']['cascade']['featureParams']['maxCatCount'])

    for i in range(cascade.stageNum):
        stage = createStage(i, doc, cascade)
        cascade.stages.append(stage)

    return cascade


if __name__ == "__main__":
    xml_file = r"haarcascade_frontalface_default.xml"
    # xml_file = r"models/haarcascade_fullbody.xml"
    with open(xml_file) as fd:
        doc = xmltodict.parse(fd.read())


    cascade = createCascade(doc)
