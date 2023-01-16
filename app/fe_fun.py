import regex as re
from io import StringIO
from PyPDF2 import PdfReader



def feture_extration_fun(file_name):
    features = {}
    stringio = StringIO(file_name.getvalue().decode("utf-8"))
    feature = []
    for line in stringio:
        if "OPFEATEND/" in line:
            line = re.sub(r'\d',"", line) # remove any int the string
            feature.append(line.split("/")[-1].replace("Rough ","").replace("Contour ","").replace("Center ","").replace(" [Drill] [Sub]","").replace(" [MSH(mm)] [Sub]","").replace(" Group","").replace("\n","").replace("\r",''))
        else:
            pass
    features[file_name.name.split(".")[0]] = set(feature) # taking only unique fetures

    return features

def get_lbh_from_file(file_name):
    stringio = StringIO(file_name.getvalue().decode("utf-8"))
    lbh = {}
    for line in stringio:
        if "BOX/" in line:
            lbh["Length"] = line.replace(" \n","").split(",")[3]
            lbh["Width"] = line.replace(" \n","").split(",")[4]
            lbh["Height"] = line.replace(" \n","").split(",")[-1].replace(" \r\n",'')
        else:
            pass

    return lbh

    

def get_besic_prop(file):
    reader = PdfReader(file)
    page = reader.pages[0]
    data = page.extract_text().split("\n")
    dim = {}
    for i in data:
        if "Surface area" in i:
            dim["Surface area"]= i.split("=")[-1].split(".")[0].lstrip().replace("1 ","")
            
        elif "V olume" in i:
            dim["Volume"] = i.split("=")[-1].split(".")[0].lstrip().replace("1 ","")
        else:
            pass
    return dim

ref_feat = {'Countersink-Counterbore Hole': 0,
 'Countersink-Countersink Hole': 0,
 'Drill-Counterbore Hole': 0,
 'Drill-Countersink Hole': 0,
 'Drill-Hole': 0,
 'Drill-MS Hole': 0,
 'Face Mill-Face Feature': 0,
 'Mill-Circular Pocket': 0,
 'Mill-Counterbore Hole': 0,
 'Mill-Irregular Pocket': 0,
 'Mill-Irregular Slot': 0,
 'Mill-Open Pocket': 0,
 'Mill-Obround Pocket':0,
 'Mill-Perimeter-Open Pocket': 0,
 'Mill-Rectangular Pocket': 0,
 'Mill-Rectangular Slot': 0}

def feature_list_for_ml(ref_feat,extract_cad_feat):
    actual_fetaure_list = {}
    for item,val in extract_cad_feat.items():
        temp_fet_val = ref_feat.copy()
        for i in extract_cad_feat[item]:
            try:
                temp_fet_val[i] = 1
            except:
                pass
        actual_fetaure_list[item] = temp_fet_val
    return actual_fetaure_list

def get_machined_vol(l,b,h,vol):
    machine_vol = float(l)*float(b)*float(h) - float(vol)
    return machine_vol
