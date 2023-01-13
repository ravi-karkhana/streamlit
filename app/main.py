import streamlit as st
import fe_fun
import trimesh
import os
import sheet_metal_fe
import sheet_metal_bc

st.set_page_config(page_title="File Uploader", page_icon=":clipboard:", layout="wide")

tab1, tab2 = st.tabs(["CNC","sheet metal"])

with tab1:
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

with tab2:
    with st.form(key='sheet metal file'):

        dxf_file = st.file_uploader("Choose a dxf File", type=["dxf"])

        c1, c2, c3, c4,c5 = st.columns(5)
        with c1:
            sub_process = st.selectbox("Select sub Process",("Laser Cutting","Laser Cutting & Bending"))
        with c2:
            surface_finish = st.selectbox("Surface finish",(None,"Buffing - Matte", "Buffing - Glossy", "Powder Coating", "Zinc Plating", "Anodising"))  
        with c3:
            thk = st.number_input("sheet thickenss in mm",2) 
        with c4:
            nos = st.number_input("Quantity",1)
            color = st.text_input("Color")
        with c5:
            no_of_bend = st.number_input("No of Bend",0)
            rm_rate = st.number_input("Raw matreial Rate in INR/Kg.",125)
        
        if "visibility" not in st.session_state:
            st.session_state.visibility = "visible"
            st.session_state.disabled = False

        st.checkbox("Edit Database", key="disabled")

        c1, c2, c3, c4,c5 = st.columns(5)
        with c1:
            rejection_percent = st.slider("Rejection Percentage in %",0,10,3,label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,)
            fright_percent = st.slider("fright Percentage in %",0,40,10,label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,)
        with c2:
            c_mf = st.number_input("cutting factor",0.012)
            mf_bend = st.number_input("Bend Factor",10)
        with c3:
            density = st.number_input("Density in gm/cc",8.0)
        with c4:
            pp_rate = st.number_input("Post Process rate",0.014)
        with c5:
            ns_mf = st.number_input("no of start factor",1.0)
        submitButton = st.form_submit_button(label = 'Calculate')

    if dxf_file is not None:
        with open(dxf_file.name,"wb") as f:
            f.write(dxf_file.getvalue())
        filepath = os.getcwd()+"\\"+dxf_file.name
        # s_perimeter = sheet_metal_fe.get_dxf_perimeter(filepath)
        cal_data = {
        "perimeter":sheet_metal_fe.get_dxf_perimeter(filepath),
        "no_of_start":sheet_metal_fe.get_no_of_start(filepath),
        "box_size":sheet_metal_fe.get_blank_size(filepath),
        "sheet_size": (1250,2500),
        "density": float(density),  # in gm/cc,db
        "c_mf": c_mf,  # cutting factor, db
        "ns_mf": float(ns_mf),  # no of start factor, db
        "rm_rate": rm_rate,  # rate card, db
        "fright_percent": float(fright_percent),  # db
        "rejection_percent": float(rejection_percent), # db
        "mf_bend": mf_bend,  # db
        "thk": thk,  # user input
        "nos": nos,  # qty , user input
        "no_of_bend" : no_of_bend,   # user input
        "sub_process":sub_process ,  # user input
        "surface_finish": surface_finish,  # user input
        "color": color,  # user input
        "pp_rate" :pp_rate # rate per squre inch, db
    }

        a = sheet_metal_bc.Sheetmetal_buildCosting_cal().sheet_maetal_cost(cal_data)
        os.remove(filepath)
        st.write(a)


