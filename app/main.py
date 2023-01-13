import streamlit as st
import fe_fun
import trimesh
import os

st.set_page_config(page_title="File Uploader", page_icon=":clipboard:", layout="wide")

with st.form(key='columns_in_form'):
    c1, c2, c3, c4,c5 = st.columns(5)
    with c1:
        length = st.number_input("Length in mm")
    with c2:
        width = st.number_input("Width in mm")
    with c3:
        height = st.number_input("Height in mm")
    with c4:
        volume = st.number_input("Part Volume in mm^3")
    with c5:
        surface_area = st.number_input("Surface Area in mm^2")

    uploaded_file = st.file_uploader("Choose a Cad Feture File", type=["clt"])

    # cad_file = st.file_uploader("Choose a Cad file", type=["step","iges","stp","igs"])

    submitButton = st.form_submit_button(label = 'Calculate')

if uploaded_file is not None:
    mchn_vol = fe_fun.get_machined_vol(length,width,height,volume)
    output = fe_fun.feture_ectration_fun(uploaded_file)
    name = str(uploaded_file.name).split(".")[0]
    data = [length,width,height,volume,surface_area,mchn_vol,output[name]]
    st.write(data)

st.snow()

# if cad_file is not None:
#     with open(cad_file.name,"wb") as f:
#         f.write(cad_file.getvalue())
#     filepath = os.getcwd()+cad_file.name
#     cad = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(file_name=filepath))
#     valu =cad.volume
#     st.write("done",valu)
