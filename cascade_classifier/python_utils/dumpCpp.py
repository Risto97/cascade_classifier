
def dumpCpp(cascade, fn):
    f = open(fn, "w")

    print(f"#ifndef CASCADE_HPP", file=f)
    print(f"#define CASCADE_HPP\n", file=f)

    print(f"const unsigned int stageNum = {cascade.stageNum};", file=f)
    print(
        f"const unsigned int maxWeakCount = {cascade.maxWeakCount};", file=f)
    print(
        f"const unsigned int FRAME_HEIGHT = {cascade.featureSize[0]+1};",
        file=f)
    print(
        f"const unsigned int FRAME_WIDTH = {cascade.featureSize[1]+1};\n",
        file=f)

    print(
        f"const unsigned int stagesFeatureCount[{cascade.stageNum}]=",
        end='{',
        file=f)

    for stage in cascade.stages:
        if stage.stageIndex < cascade.stageNum - 1:
            print(f"{stage.maxWeakCount}", end=',', file=f)
        else:
            print(f"{stage.maxWeakCount}", end='', file=f)
    print("};\n", file=f)

    print(
        f"const signed int stageThresholds[{cascade.stageNum}]=",
        end='{',
        file=f)
    for stage in cascade.stages:
        if stage.stageIndex < cascade.stageNum - 1:
            print(f"{int(stage.stageThreshold)}", end=',', file=f)
        else:
            print(f"{int(stage.stageThreshold)}", end='', file=f)
    print("};\n", file=f)

    print(
        f"const signed int featureThresholds[{cascade.featuresNum}]=",
        end='{',
        file=f)
    for stage in cascade.stages:
        for feature in stage.features:
            if feature.featureNum == cascade.featuresNum - 1:
                print(f"{feature.threshold}", end='', file=f)
            else:
                print(f"{feature.threshold}", end=',', file=f)
    print("};\n", file=f)

    print(
        f"const signed int passVal[{cascade.featuresNum}]=", end='{', file=f)
    for stage in cascade.stages:
        for feature in stage.features:
            if feature.featureNum == cascade.featuresNum - 1:
                print(f"{feature.passVal}", end='', file=f)
            else:
                print(f"{feature.passVal}", end=',', file=f)
    print("};\n", file=f)

    print(
        f"const signed int failVal[{cascade.featuresNum}]=", end='{', file=f)
    for stage in cascade.stages:
        for feature in stage.features:
            if feature.featureNum == cascade.featuresNum - 1:
                print(f"{feature.failVal}", end='', file=f)
            else:
                print(f"{feature.failVal}", end=',', file=f)
    print("};\n", file=f)

    for i in range(cascade.maxRectCount):
        print(
            f"const signed int weight{i}[{cascade.featuresNum}]=",
            end='{',
            file=f)
        for stage in cascade.stages:
            for feature in stage.features:
                try:
                    if feature.featureNum == cascade.featuresNum - 1:
                        print(f"{feature.rects[i].weight}", end='', file=f)
                    else:
                        print(
                            f"{feature.rects[i].weight}", end=',', file=f)
                except:
                    if feature.featureNum == cascade.featuresNum - 1:
                        print(f"0", end='', file=f)
                    else:
                        print(f"0", end=',', file=f)
        print("};\n", file=f)

    for i in range(cascade.maxRectCount):
        print(
            f"const unsigned int rect{i}[{cascade.featuresNum}][4][2]=",
            end='{',
            file=f)
        for stage in cascade.stages:
            for feature in stage.features:
                try:
                    strA = f"{feature.rects[i].A['x']},{feature.rects[i].A['y']}" + "}"
                    strB = "{" + f"{feature.rects[i].B['x']},{feature.rects[i].B['y']}" + "}"
                    strC = "{" + f"{feature.rects[i].C['x']},{feature.rects[i].C['y']}" + "}"
                    strD = "{" + f"{feature.rects[i].D['x']},{feature.rects[i].D['y']}" + "}"
                    concat = f"{strA},{strB},{strC},{strD}"
                    print("{{", end='', file=f)
                    print(concat, end='', file=f)
                    if feature.featureNum == cascade.featuresNum - 1:
                        print("}", end='', file=f)
                    else:
                        print("}", end=',', file=f)

                except:
                    if feature.featureNum == cascade.featuresNum - 1:
                        print("{{0,0},{0,0},{0,0},{0,0}}", end='', file=f)
                    else:
                        print("{{0,0},{0,0},{0,0},{0,0}}", end=',', file=f)

        print("};\n", file=f)

    print(f"\n#endif", file=f)
