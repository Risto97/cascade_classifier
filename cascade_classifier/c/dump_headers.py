from cascade_classifier.python_utils.sqrt_approx import SqrtClass
from cascade_classifier.python_utils.dumpCpp import dumpCpp as cascade_dump
from cascade_classifier.python_utils.cascade import CascadeClass

xml_file = r"../xml_models/haarcascade_frontalface_default.xml"

cascade = CascadeClass("../xml_models/haarcascade_frontalface_default.xml")

sqrt = SqrtClass()
sqrt.dumpC("./sqrt.hpp")
cascade_dump(cascade, "cascade.hpp")
