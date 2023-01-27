# streamlit_app.py

import streamlit as st
import mysql.connector

# Initialize connection.
# Uses st.experimental_singleton to only run once.
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
def run_query(query):
    conn = init_connection()
    cur = conn.cursor()
    print(query)
    cur.execute(query)
    conn.commit()
    return cur.fetchall()

# rows = run_query("Describe rfq;")
# print(rows)

def upload_query(data):
    s = f'''INSERT INTO sheetmetaldata 
        ( name ,creation  ,perimeter  ,no_of_start  ,blank_size_x  ,blank_size_y  ,nest_blank_size_x  ,nest_blank_size_y  ,no_of_sheet  ,sheet_thickness  ,area  ,volume  ,wt  ,nos  ,wt_per_part  ,rm_cost  ,lasser_cutting_cost  ,rm_cutting_cost  ,rm_fright_cost  ,rejection_cost  ,bending_cost  ,post_processing_cost  ,total_cost_per_part  ,total_cost  ,optimum_nos  ,optimum_rm_cost  ,optimum_total_cost_per_part  ,optimum_total_cost  )
        VALUES
        ("{data["name" ]}",  "{data["creation"]}",  {data["perimeter"]},  {data["no_of_start"]},  {data["blank_size"][0]},  {data["blank_size"][1]},  {data["nest_blank_size"][0]},  {data["nest_blank_size"][1]},  {data["no_of_sheet"]},  {data["sheet_thickness"]},  {data["area"]},  {data["volume"]},  {data["wt"]},  {data["nos"]},  {data["wt_per_part"]},  {data["rm_cost"]},  {data["lasser_cutting_cost"]},  {data["rm_cutting_cost"]},  {data["rm_fright_cost"]},  {data["rejection_cost"]},  {data["bending_cost"]},  {data["post_processing_cost"]},  {data["total_cost_per_part"]},  {data["total_cost"]},  {data["optimum_nos"]},  {data["optimum_rm_cost"]},  {data["optimum_total_cost_per_part"]},  {data["optimum_total_cost"]});'''
    return s

# Print results.
# for row in rows:
#     print(f"{row[0]} has a :{row[1]}:")
    # st.write(f"{row[0]} has a :{row[1]}:")