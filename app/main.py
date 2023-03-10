import streamlit as st
import fe_fun
import os
import sheet_metal_fe
import sheet_metal_bc
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import datetime
from mysql_query import *
from pytz import timezone

st.set_page_config(page_title="File Uploader", page_icon=":clipboard:", layout="wide")

tab1, tab2 = st.tabs(["CNC","sheet metal"])

with tab1:
    with st.form(key='columns_in_form'):
        c1, c2 = st.columns(2)
        with c1:
            volume = st.number_input("Part Volume in mm^3",0)
            rm_rate = st.number_input("Raw matreial Rate in INR/Kg.",0.0,1000.0,125.0)
            qty = st.number_input("Total Quantity",1)
            uploaded_file = st.file_uploader("Choose a Cad Feture File", type=["clt"])
        with c2:
            ref_wt = st.number_input("thrusold weight for raw material (in Kg)",0.000,100.000,0.500,step=1e-3,format="%.3f")
            density = st.number_input("Density in gm/cc",0.0,50.0,8.0)
            surface_area = st.number_input("Surface Area in mm^2",0)
            pdf_file = st.file_uploader("Choose a Solidwork Mass Property File", type=["pdf"])

        # cad_file = st.file_uploader("Choose a Cad file", type=["step","iges","stp","igs"])

        submitButton = st.form_submit_button(label = 'Calculate')

    machine_model_file = Path(__file__).parents[0] / "ml_model/gs_cv_rndm.pkl"
    setupcost_model_file = Path(__file__).parents[0] / "ml_model/gs_cv_rndm_setup_cost.pkl"
    pickled_gs_cv_rndm_model = pickle.load(open(machine_model_file, 'rb'))
    pickled_gs_cv_rndm_setup_cost_model = pickle.load(open(setupcost_model_file, 'rb'))
    

    # x1 = [[0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,120,20,40,55000,45000,41000]]

    if uploaded_file is not None:
        output = fe_fun.feture_extration_fun(uploaded_file)
        lbh_data = fe_fun.get_lbh_from_file(uploaded_file)
        length = lbh_data["Length"]
        width = lbh_data["Width"]
        height = lbh_data["Height"]
        # print(os.getcwd()+"\\"+"gs_cv_rndm.pkl")

        mchn_vol = fe_fun.get_machined_vol(length,width,height,volume)
        final_feat_list = fe_fun.feature_list_for_ml(fe_fun.ref_feat,output)
        part_wt = fe_fun.get_raw_material_wt(lbh_data,density,ref_wt,qty)
        stock_material_cost = fe_fun.get_rm_cost(part_wt,rm_rate)

        final_feat_list[uploaded_file.name.split(".")[0]]["Length"] = length
        final_feat_list[uploaded_file.name.split(".")[0]]["Width"] = width
        final_feat_list[uploaded_file.name.split(".")[0]]["Height"] = height

        if pdf_file is None:
            final_feat_list[uploaded_file.name.split(".")[0]]["Surface area"] = surface_area
            final_feat_list[uploaded_file.name.split(".")[0]]["Volume"] = volume
        else:
            basic_prop = fe_fun.get_besic_prop(pdf_file)
            final_feat_list[uploaded_file.name.split(".")[0]]["Surface area"] = basic_prop["Surface area"]
            final_feat_list[uploaded_file.name.split(".")[0]]["Volume"] = basic_prop["Volume"]

        final_feat_list[uploaded_file.name.split(".")[0]]["Machined volume"] = mchn_vol
    
        df = pd.DataFrame(final_feat_list)
        test_data = df.values
        test_data = [list(np.concatenate(test_data))]
        machine_cost = pickled_gs_cv_rndm_model.predict(test_data)
        setup_cost = pickled_gs_cv_rndm_setup_cost_model.predict(test_data)
        total_Mfg_cost_per_part = machine_cost + setup_cost/qty
        st.write(stock_material_cost,total_Mfg_cost_per_part,df)

    # st.snow()

    # if cad_file is not None:
    #     with open(cad_file.name,"wb") as f:
    #         f.write(cad_file.getvalue())
    #     filepath = os.getcwd()+cad_file.name
    #     cad = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(file_name=filepath))
    #     valu =cad.volume
    #     st.write("done",valu)

with tab2:

    if "visibility" not in st.session_state:
            st.session_state.visibility = "visible"
            st.session_state.disabled = True

    st.checkbox("Edit Database", key="disabled")

    c1, c2, c3, c4,c5 = st.columns(5)
    with c1:
        rejection_percent = st.slider("Rejection Percentage in %",0,10,3,label_visibility=st.session_state.visibility,disabled=st.session_state.disabled)
        fright_percent = st.slider("fright Percentage in %",0,40,10,label_visibility=st.session_state.visibility,disabled=st.session_state.disabled)
    with c2:
        c_mf = st.number_input("cutting factor",0.000,100.000,0.012,step=1e-3,format="%.3f",label_visibility=st.session_state.visibility,disabled=st.session_state.disabled)
        mf_bend = st.number_input("Bend Factor",0.0,100.0,10.0,label_visibility=st.session_state.visibility,disabled=st.session_state.disabled)
    with c3:
        density = st.number_input("Density in gm/cc",0.0,50.0,8.0,label_visibility=st.session_state.visibility,disabled=st.session_state.disabled)
    with c4:
        pp_rate = st.number_input("Post Process rate (INR/Kg)",0.00,200.00,30.00,step=1e-2,
        format="%.2f",label_visibility=st.session_state.visibility,disabled=st.session_state.disabled)
    with c5:
        ns_mf = st.number_input("no of start factor",0.0,50.0,1.0,label_visibility=st.session_state.visibility,disabled=st.session_state.disabled)

    with st.form(key='sheet metal file'):

        # st.info('Please Upload a flat Pattern 1:1 DXf file ', icon="??????")
        dxf_file = st.file_uploader("Choose a flat Pattern 1:1 DXf file", type=["dxf"])

        c1, c2, c3, c4,c5 = st.columns(5)
        with c1:
            sub_process = st.selectbox("Select sub Process",("Laser Cutting","Laser Cutting & Bending"))
        with c2:
            surface_finish = st.selectbox("Surface finish",(None,"Buffing - Matte", "Buffing - Glossy", "Powder Coating", "Zinc Plating", "Anodising"))  
        with c3:
            thk = st.number_input("sheet thickenss in mm",0.5,25.0,2.0) 
        with c4:
            nos = st.number_input("Quantity",1)
            color = st.text_input("Color")
        with c5:
            no_of_bend = st.number_input("No of Bend",0)
            rm_rate = st.number_input("Raw matreial Rate in INR/Kg.",0.0,1000.0,125.0)

        
        submitButton = st.form_submit_button(label = 'Calculate')

    if dxf_file is not None:
        with open(Path(__file__).parents[0] /"dxf_file"/ dxf_file.name,"wb") as f:
            f.write(dxf_file.getvalue())
        filepath = Path(__file__).parents[0] /"dxf_file"/ dxf_file.name
        # st.write(filepath)
        # filepath = os.getcwd()+"\\"+dxf_file.name
        # s_perimeter = sheet_metal_fe.get_dxf_perimeter(filepath)
        try :
            cal_data = {
            "perimeter":sheet_metal_fe.get_dxf_perimeter(filepath),
            "no_of_start":sheet_metal_fe.get_no_of_start(filepath),
            "box_size":sheet_metal_fe.get_blank_size(filepath),
            "sheet_size": (1250,2500),
            "density": float(density),  # in gm/cc,db
            "c_mf": c_mf,  # cutting factor, db
            "ns_mf": float(ns_mf),  # no of start factor, db
            "rm_rate": rm_rate,  # rate card, db
            "fright_percent": float(fright_percent)/100.0,  # db
            "rejection_percent": float(rejection_percent)/100.0, # db
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
            a["name"] = dxf_file.name
            a["creation"] = datetime.datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
            os.remove(filepath)
            st.write(a)
            query = upload_query(a)
            # query2 = '''insert into sheetmetaldata (name ,creation ,perimeter ,no_of_start ,blank_size_x ,blank_size_y ,nest_blank_size_x ,nest_blank_size_y ,no_of_sheet ,sheet_thickness ,area ,volume ,wt ,nos ,wt_per_part ,rm_cost ,lasser_cutting_cost ,rm_cutting_cost ,rm_fright_cost ,rejection_cost ,bending_cost ,post_processing_cost ,total_cost_per_part ,total_cost ,optimum_nos ,optimum_rm_cost ,optimum_total_cost_per_part ,optimum_total_cost ) VALUES ("Flat pattern - P-TG1-EXP-0001.DXF", "2023-01-27 15:26:23", 344.82, 3, 90.0, 60.0, 312.5, 312.5, 0, 2.0, 5400.0, 195.312, 1.562, 1, 1.562, 195.25, 11.28, 206.53, 19.53, 6.2, 0, 0, 232.26, 232.26, 15, 13.02, 50.03, 750.45);'''
            # query3 = "select * from sheetmetaldata;"
            run_query(query)
        except:
            st.warning("The file format is not Proper.")
            os.remove(filepath)


