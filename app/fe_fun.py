import regex as re
from io import StringIO



def feture_ectration_fun(file_name):
    features = {}
    stringio = StringIO(file_name.getvalue().decode("utf-8"))
    feature = []
    for line in stringio:
        if "OPFEATEND/" in line:
            line = re.sub(r'\d',"", line) # remove any int the string
            feature.append(line.split("/")[-1].replace("Rough ","").replace("Contour ","").replace("Center ","").replace("\n",""))
        else:
            pass
    features[file_name.name.split(".")[0]] = set(feature) # taking only unique fetures

    return features


def get_machined_vol(l,b,h,vol):
    machine_vol = l*b*h - vol
    return machine_vol
