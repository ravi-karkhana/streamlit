import regex as re
from io import StringIO
from PyPDF2 import PdfReader
from util import *
from collections import Counter


# from clt Extract all the features
def feture_extration_fun(file_name):
    features = {}
    stringio = StringIO(file_name.getvalue().decode("utf-8"))
    feature = []
    for line in stringio:
        if "OPFEATEND/" in line:
            line = re.sub(r'\d',"", line) # remove any int the string
            feature.append(line.split("/")[-1].replace("Rough ","").replace("Contour ","").replace("Center ","").replace(" [Drill] [Sub]","").replace(" [MSH(mm)] [Sub]","").replace(" Group","").replace("\n","").replace("[Thread] [.x. MC Tap-Cutting] [Sub]","").replace("MS ","").replace("Hole ","Hole"))
        else:
            pass
    # features[file_name.name.split(".")[0]] = set(feature) # taking only unique fetures
    features[file_name.name.split(".")[0].replace(" (1)","")] = feature # taking all fetures
    return features

# from pdf file extract the Box dimension
def get_lbh_from_file(file_name):
    stringio = StringIO(file_name.getvalue().decode("utf-8"))
    lbh = {}
    for line in stringio:
        if "BOX/" in line:
            lbh["Length"] = float(line.replace(" \n","").split(",")[3])
            lbh["Width"] = float(line.replace(" \n","").split(",")[4])
            lbh["Height"] = float(line.replace(" \n","").split(",")[-1].replace(" \r\n",''))
        else:
            pass
    def get_sort_lbh(box_dim):
        v = list(box_dim.values())
        v.sort()
        box_dim["Length"] = max(v)
        box_dim["Width"] = v[1]
        box_dim["Height"] = min(v)
        v = list(box_dim.values())
        return box_dim
    
    return get_sort_lbh(lbh)

# from extracted feature from clt file get the frequncy of all unique feature 
def get_fequncy_of_fetaure(feature_lst):
    actual_fetaure_list = {}
    for i,j in feature_lst.items():
        c = Counter( sorted(j))
        actual_fetaure_list[i] = c
    return actual_fetaure_list
 
 # get the surface area and volume of cad model from the pdf
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


def feature_list_for_ml(ref_feat,extract_cad_feat):
    actual_fetaure_list = {}
    fetaure_data_with_frequncy = get_fequncy_of_fetaure(extract_cad_feat)
    for item,val in fetaure_data_with_frequncy.items():
        temp_fet_val = ref_feat.copy()
        for i in fetaure_data_with_frequncy[item]:
            temp_fet_val[i.replace("\r","")] = fetaure_data_with_frequncy[item][i]
        actual_fetaure_list[item] = temp_fet_val
    return actual_fetaure_list

def get_machined_vol(l,b,h,vol):
    machine_vol = float(l)*float(b)*float(h) - float(vol)
    return machine_vol

def get_raw_material_wt(dim,density):
    extra_mtrl = float(4)
    vol = (float(dim["Length"]) + extra_mtrl ) * (float(dim["Width"]) + extra_mtrl ) * (float(dim["Height"]) + extra_mtrl )
    wt = vol * density / 1000000
    return float(wt)

def get_rm_cost(wt,rate,qty):
    if qty > 100:
        rm_cost = wt * rate
        return rm_cost
    else:
        first_case = wt * rate
        a = rate/qty
        b = rate/2.5
        second_case = min(a,b)
        third_case = 30
        return  round(max(first_case,second_case,third_case),0)

def get_value_of_group(val,grade,group):
    group_copy = group.copy()
    grp_val = 'group_' + grade[val]
    group_copy[grp_val] = 1
    return group_copy

def get_df_with_grade(df,grade_data):
    for key in grade_data.keys():
        df[key] = grade_data[key]
    return df

def get_process_cost(vol, sur_area,density, cost_kg = 0, cost_sqr_inch = 0):
    Post_cost_kg = float(vol) * float(density) * float(cost_kg  / 1000000)
    post_cost_sqr_inch = float(sur_area )* 0.00155 * float(cost_sqr_inch)
    return round(max( Post_cost_kg,post_cost_sqr_inch),0)
