import pandas as pd
from pathlib import Path
import streamlit as st
import mysql.connector
import warnings

def get_machines_supplier_data(df):
    length = df['Length'][0]
    width = df['Width'][0]
    height = df['Height'][0]
    process = 'CNC Machining'

    
    query = "SELECT * FROM _338944048dd98013.auto_generated_table"
    # supp_db = pd.read_sql_query(query, engine)
    # Function to run query and return DataFrame
    def run_query_and_get_df(query):
        conn = mysql.connector.connect(**st.secrets["mysql"])
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    supp_db = run_query_and_get_df(query)
    st.dataframe(supp_db)
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
