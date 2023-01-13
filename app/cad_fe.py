import trimesh

def volume_calculation_cad(filepath):
    try:
        if ".stl" in filepath or ".STL" in filepath or ".Stl" in filepath or ".obj" in filepath or ".OBJ" in filepath or ".Obj" in filepath:
            cad = trimesh.load(filepath)
            return cad
        else:
            cad = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(file_name=filepath))
            return cad
    except:
        cad = None
def get_boundBox(cad):
    if cad != None:
        box = list(cad.extents)
        reBox = {
            "length": 0,
            "width": 0,
            "heigth": 0
        }
        if len(box) == 3:
            return {
                "length": box[0],
                "width": box[1],
                "heigth": box[2]
            }
        return reBox

def get_volume(cad):
    if cad != None:
        return cad.volume
    
def get_premitive(cad):
    if cad != None:
        return str(cad.bounding_primitive).split(".")[-1].replace(">","")
    
def get_surfacearea(cad):
    if cad != None:
        return cad.area
    
def cad_fe(file_name):
    cnd_feature_data = {}
    cad = volume_calculation_cad(file_name)
    lbh = get_boundBox(cad)
    surface_area = get_surfacearea(cad)
    volume = get_volume(cad)
    cnd_feature_data['item_name'] = str(file_name).split("\\")[-1]
    cnd_feature_data['L'] = lbh['length']
    cnd_feature_data['width'] = lbh['width']
    cnd_feature_data['heigth'] = lbh['heigth']
    cnd_feature_data['premitive'] = get_premitive(cad)
    cnd_feature_data['surface_area'] = surface_area
    cnd_feature_data['volume'] = volume
    return cnd_feature_data