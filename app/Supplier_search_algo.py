import pandas as pd
from pathlib import Path
import streamlit as st
import warnings

def get_machines_supplier_data(df):
    length = df['Length'][0]
    width = df['Width'][0]
    height = df['Height'][0]
    process = 'CNC Machining'

    # supp_db = pd.read_csv(Path(__file__).parents[0] / "supplier_db/supplier_machn_cap.csv")
    supp_db = pd.read_json(Path(__file__).parents[0] / "supplier_db/supplier_machn_cap.json")
    filtered_df = supp_db[
        (supp_db['manufacturing_sub_process'] == process) &
        (supp_db['Bed Size - X in mm'] > length) &
        (supp_db['Bed Size - Y in mm'] > width) &
        (supp_db['Bed Size - Z in mm'] > height)
    ]
    sup_col = ['Supplier Name', 'Name', 'Supplier Mobile',
       'O Address', 'O City', 'O State']
    machine_col = ['Brand']
    suplier_list = filtered_df[sup_col].drop_duplicates()
    machn_list = filtered_df[machine_col].drop_duplicates()
    cities_to_filter = st.multiselect('Select multiple options:', set(suplier_list['O City']), default=set(suplier_list['O City']))
    suplier_list = suplier_list[suplier_list['O City'].isin(cities_to_filter)]
    return suplier_list , machn_list
