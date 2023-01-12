import streamlit as st
import fe_fun

st.set_page_config(page_title="File Uploader", page_icon=":clipboard:", layout="wide")

# cad_file = st.file_uploader("Choose a Cad file", type=["step","iges","stp","igs"])
uploaded_file = st.file_uploader("Choose a file", type=["clt"])

if uploaded_file is not None:
    output = fe_fun.feture_ectration_fun(uploaded_file)
    st.write(output)

# if cad_file is not None:
#     cad_opt = cad_fe.cad_fe()
#     st.write("done")
