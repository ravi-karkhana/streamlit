import re
import pandas as pd
import math
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from util import *

# Ignore all warnings
warnings.filterwarnings("ignore")

# operation prediction model
def get_operation_prediction(model, df):
    feat = ['Blind Hole(s)', 'Circular Milled Face(s)',
            'Concave Fillet Edge Milling Face(s)',
            'Convex Profile Edge Milling Face(s)', 'Countersink(s)',
            'Curved Milled Face(s)', 'Flat Bottom Hole(s)',
            'Flat Face Milled Face(s)', 'Flat Side Milled Face(s)', 'Pocket(s)',
            'Through Hole(s)', 'Total features', 'No of axis']

    operations_key = ['Boring', 'Centre Drill', 'Chamfering',
                      'Chamfering Interpolation', 'Counterboring',
                      'Counterboring Interpolation', 'Countersinking', 'Drilling', 'Facing',
                      'High Feed Milling', 'Internal Threading', 'Parting', 'Pocket Milling',
                      'Profile Milling', 'Profile Milling -  Finishing', 'Radial Chamfering',
                      'Shoulder Milling', 'Shoulder/Slot/Pocket Milling - Finishing',
                      'Side Slotting', 'Slot Milling', 'Tapping']

    operations_val = model.predict(df[feat].values)[0]
    operations = dict(zip(operations_key, operations_val))
    # Create a DataFrame from the dictionary
    df = pd.DataFrame.from_dict(operations, orient='index', columns=['Value'])

    # Convert the 'Value' column to numeric
    df['Value'] = pd.to_numeric(df['Value'])

    # Select rows where the 'Value' is 1
    selected_rows = df[df['Value'] == 1]

    return selected_rows
# Data Process for both file package
class DataProcessor:
    def __init__(self, feat_file_path, meta_file_path,mtrl_val):
        self.feat_file_path = feat_file_path
        self.meta_file_path = meta_file_path
        self.mtrl_val = mtrl_val

    def process_data(self):
        feat_df = ExtractFeatureToDF(self.feat_file_path).get_prep_fst_half_feat_ML()
        meta_df = TextFileProcessor(self.meta_file_path).process_columns()
        feat_meta_df = pd.merge(feat_df, meta_df, left_on='file_name', right_on='model_name', how='left').drop(['File_name_m', 'model_name'], axis=1)
        total_feat_meta_df = add_missing_and_process_columns(feat_meta_df)
        matrl_grp_ce = get_value_of_group_ce(self.mtrl_val,garde_group,Group_name_ce)
        final_df = pd.concat([total_feat_meta_df,matrl_grp_ce],axis=1)

        return final_df


# feature Exctraction package
class ExtractFeatureToDF:
    
    master_feature_lst = ['Flat Face Milled Face(s)', 'Flat Side Milled Face(s)', 'Curved Milled Face(s)', 'Circular Milled Face(s)',
                          'Deburr Face(s)', 'Convex Profile Edge Milling Face(s)', 'Concave Fillet Edge Milling Face(s)', 'Total features',
                          'Flat Milled Face(s)', 'Turn Diameter Face(s)', 'Turn Form Face(s)', 'Turn Face Face(s)', 'Bore Face(s)',
                          'Face(s)', 'Through Hole(s)', 'Countersink(s)', 'Pocket(s)', 'Flat Bottom Hole(s)', 'Blind Hole(s)', 'Partial Hole(s)']

    group_feat_1 = ['Flat Face Milled Face(s)', 'Flat Side Milled Face(s)', 'Curved Milled Face(s)', 'Circular Milled Face(s)',
                    'Deburr Face(s)', 'Flat Milled Face(s)', 'Total features']

    group_feat_2 = ['Convex Profile Edge Milling Face(s)', 'Concave Fillet Edge Milling Face(s)', 'Bore Face(s)',
                    'Turn Diameter Face(s)', 'Turn Face Face(s)', 'Turn Form Face(s)']

    group_feat_3 = ['Through Hole(s)', 'Countersink(s)', 'Flat Bottom Hole(s)', 'Blind Hole(s)', 'Partial Hole(s)']

    group_feat_4 = ['Pocket(s)']
    
    def __init__(self, path):
        self.path = path

    @staticmethod
    def extract_numbers_and_text(input_string):
        numbers = re.findall(r'\d+', input_string)
        numbers = [int(num) for num in numbers]
        text = re.findall(r'[a-zA-Z()]+', input_string)
        combined_text = ' '.join(text)
        result = [numbers, combined_text]
        return result

    @staticmethod
    def get_feature_value_from_model_part(data):
        filter_data = ['https', 'tasks']
        feature_data = data[1].split('\n')[1:-1]
        features = []
        values = []

        for line in feature_data:
            if not any(filter_word in line for filter_word in filter_data):
                line_parts = line.split(":")
                if len(line_parts) > 1:
                    feature = line_parts[0].strip()
                    value = line_parts[1].strip()
                    features.append(feature)
                    values.append(value)
                elif 'with' in line_parts[0]:
                    res = ExtractFeatureToDF.extract_numbers_and_text(line_parts[0])
                    features.append(res[1])
                    values.append(res[0][0])

        return {"features": features, "values": values}
    
    @staticmethod
    def convert_string_tofloat(df,col):
        if df[col].dtype==object:
            # Remove ' mm' substring from column
            df[col]=df[col].str.replace(' mm', '')
            # Convert column to float and round to 2 decimal places
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2) 
    
        
    @staticmethod   
    def extract_axis_components(axis_string):
        pattern = r'([-+]?\d+\.\d+)'
        matches = re.findall(pattern, axis_string)

        if len(matches) == 3:
            x = float(matches[0])
            y = float(matches[1])
            z = float(matches[2])
            return x, y, z
        else:
            return None

    @staticmethod
    def get_feture_with_value(main_feat, feature, values, num):
        part_feat = {}
        if main_feat in ExtractFeatureToDF.group_feat_1:
            part_feat[main_feat] = {'Nos.': values[num], 'length': '', 'width': '', 'depth': '', 'Radius': '', 'axis': ''}
            return part_feat, 'no', num - 1
        elif main_feat in ExtractFeatureToDF.group_feat_2:
            part_feat[main_feat] = {'Nos.': values[num + 1], 'length': '', 'width': '', 'depth': '', 'Radius': values[num + 2], 'axis': ''}
            return part_feat, main_feat, num + 2
        elif main_feat in ExtractFeatureToDF.group_feat_3:
            part_feat[main_feat] = {'Nos.': values[num + 1], 'length': '', 'width': '', 'depth': values[num + 3], 'Radius': values[num + 2], 'axis': ExtractFeatureToDF.extract_axis_components(values[num + 4])}
            return part_feat, main_feat, num + 4
        elif main_feat in ExtractFeatureToDF.group_feat_4:
            part_feat[main_feat] = {'Nos.': values[num + 1], 'length': values[num + 2], 'width': values[num + 3], 'depth': values[num + 4], 'Radius': '', 'axis':  ExtractFeatureToDF.extract_axis_components(values[num + 5])}
            return part_feat, main_feat, num + 5
        else:
            part_feat[main_feat] = {'Nos.': '', 'length': '', 'width': '', 'depth': '', 'Radius': '', 'axis': ''}
            return part_feat, 'no', num - 1

    @staticmethod
    def get_data_in_structure(response):
        feat_len = len(response['features'])
        part_feats = []
        for i in range(feat_len):
            if response['features'][i] in ExtractFeatureToDF.master_feature_lst:
                res, store_sub_feat, next_index_pred = ExtractFeatureToDF.get_feture_with_value(response['features'][i], response['features'], response['values'], i)
                part_feats.append(res)
                try:
                    while store_sub_feat != 'no' and 'with' in response['features'][next_index_pred + 1]:
                        res, store_sub_feat, next_index_pred = ExtractFeatureToDF.get_feture_with_value(store_sub_feat, response['features'], response['values'], next_index_pred)
                        part_feats.append(res)
                except:
                    continue
        return part_feats

    @staticmethod
    def get_list_of_df_for_one_file(full_feature_val_lst, file_name):
        dataframes = []
        for feature_val in full_feature_val_lst[file_name]:
            df = pd.DataFrame(feature_val).T
            df['file_name'] = file_name
            dataframes.append(df)
        return dataframes

    @staticmethod
    def get_all_df_in_one_df(df_lst):
        empty_df = pd.DataFrame()
        for df in df_lst:
            empty_df = pd.concat([empty_df, df])
        return empty_df
    
    @staticmethod
    def get_volume_grp3(df):
        df['feature_volume'] = math.pi* df['Radius']*df['Radius']*df['depth']*df['Nos.']
        df['feature_volume'] = pd.to_numeric(df['feature_volume'], errors='coerce').round(2) 
        return df
    
    @staticmethod
    def get_volume_grp4(df):
        df['feature_volume'] = df['length']*df['width']*df['depth']*df['Nos.']
        df['feature_volume'] = pd.to_numeric(df['feature_volume'], errors='coerce').round(2)
        return df

    @staticmethod
    def get_full_feat_lst(self):
        full_feat_lst = {}
        contents = self.path.read().decode("utf-8")
        model_data = contents.split("Model:")
        part_data = [x.split("Part") for x in model_data]
        for content in part_data:
            if len(content) > 1:
                response = ExtractFeatureToDF.get_feature_value_from_model_part(content)
                full_feat_lst[content[0].strip()] = ExtractFeatureToDF.get_data_in_structure(response)

        dataframes = []
        for file_name in full_feat_lst.keys():
            dataframes.append(ExtractFeatureToDF.get_all_df_in_one_df(ExtractFeatureToDF.get_list_of_df_for_one_file(full_feat_lst, file_name)))

        dff = ExtractFeatureToDF.get_all_df_in_one_df(dataframes)
        dff = dff.reset_index().rename(columns={'index': 'Feature Name'})
        ExtractFeatureToDF.convert_string_tofloat(dff,'length')
        ExtractFeatureToDF.convert_string_tofloat(dff,'width')
        ExtractFeatureToDF.convert_string_tofloat(dff,'depth')
        ExtractFeatureToDF.convert_string_tofloat(dff,'Radius')
        dff_grp4 = ExtractFeatureToDF.get_volume_grp4(dff[dff['Feature Name'].isin(ExtractFeatureToDF.group_feat_4)])
        dff_grp3 = ExtractFeatureToDF.get_volume_grp3(dff[dff['Feature Name'].isin(ExtractFeatureToDF.group_feat_3)])
        dff_grp = dff[~dff['Feature Name'].isin(ExtractFeatureToDF.group_feat_3 + ExtractFeatureToDF.group_feat_4)]
        dff = pd.concat([dff_grp,dff_grp3,dff_grp4])
        dff.sort_values('file_name').reset_index().drop('index', axis=1)
            
        return dff
    
    def get_prep_fst_half_feat_ML(self):

        df = ExtractFeatureToDF.get_full_feat_lst(self)
        # Group by 'file_name', extract distinct axis names, and count the number of distinct axes
        axis_df = df.groupby(['file_name'])['axis'].apply(lambda x: x.dropna().nunique()).reset_index()
        axis_df.rename(columns={'axis': 'No of axis'}, inplace=True)
        df_grp_radius = df.groupby(['file_name'])['Radius'].nunique().reset_index()
        df_grp_nos = df.groupby(['file_name','Feature Name'])['Nos.'].sum().reset_index()

        # Pivot the table by Feature Name for file_name and fill it with the values of Nos
        df_grp_nos_piv = df_grp_nos.pivot(index='file_name', columns='Feature Name', values='Nos.').reset_index()
        
        df_grp_vol = df[df['Feature Name'].isin(ExtractFeatureToDF.group_feat_3 + ExtractFeatureToDF.group_feat_4)].groupby(['file_name','Feature Name'])['feature_volume'].sum().reset_index()
        # Pivot the table by Feature Name for file_name and fill it with the values of feature_volume
        df_grp_vol_piv = df_grp_vol.pivot(index='file_name', columns='Feature Name', values='feature_volume')
        # Rename the pivoted columns with _volume suffix
        df_grp_vol_piv = df_grp_vol_piv.add_suffix('_volume').reset_index()
        
        # join the table 
        df_grp_nos_vol_piv = pd.merge(df_grp_nos_piv,df_grp_vol_piv,on='file_name', how='left')

        df_grp_nos_vol_piv = pd.merge(df_grp_nos_vol_piv,df_grp_radius,on='file_name', how='left')
        df_grp_nos_vol_piv = pd.merge(df_grp_nos_vol_piv, axis_df, on='file_name', how='outer')

        return df_grp_nos_vol_piv.fillna(0)
    

# meta data Extraction Package
class TextFileProcessor:
    def __init__(self, file_path, max_col='Length', mid_col='Height', min_col='Width'):
        self.file_path = file_path
        self.max_col = max_col
        self.mid_col = mid_col
        self.min_col = min_col

    @staticmethod
    def process_text_file(file_path, max_col, mid_col, min_col):
        # Read the text file
        text = file_path.read().decode("utf-8")

        # Define regex patterns to extract information
        pattern = r'{File_name=(.+?), model_name=(.+?), Volume=(.+?), Length=(.+?), Height=(.+?), Surface_area=(.+?), Width=(.+?)}'

        # Extract information using regex
        matches = re.findall(pattern, text)

        # Create a DataFrame from the extracted information
        df = pd.DataFrame(matches, columns=['File_name_m', 'model_name', 'Volume', 'Length', 'Height', 'Surface_area', 'Width'])

        # Sort the DataFrame columns
        for i in range(len(df)):
            box_dim = [df[max_col].iloc[i], df[mid_col].iloc[i], df[min_col].iloc[i]]
            box_dim.sort()
            df[max_col].iloc[i] = max(box_dim)
            df[mid_col].iloc[i] = box_dim[1]
            df[min_col].iloc[i] = min(box_dim)

        return df
    
    def process_columns(self):
        df = self.process_text_file(self.file_path, self.max_col, self.mid_col, self.min_col)
        column_names = ['Length', 'Width', 'Height', 'Volume', 'Surface_area']
        for column in column_names:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce').round(2)

        if 'Length' in df.columns and 'Width' in df.columns and 'Height' in df.columns and 'Volume' in df.columns:
            df['Machined_volume'] = (df['Length'] * df['Width'] * df['Height']) - df['Volume']
            df['Machined_volume'] = pd.to_numeric(df['Machined_volume'], errors='coerce').round(2)

        return df


# adding the missing column in df and proper format to each column
def add_missing_and_process_columns(df):
    column_names = ['Blind Hole(s)', 'Circular Milled Face(s)', 'Concave Fillet Edge Milling Face(s)',
                'Convex Profile Edge Milling Face(s)', 'Countersink(s)', 'Curved Milled Face(s)',
                'Flat Bottom Hole(s)', 'Flat Face Milled Face(s)', 'Flat Side Milled Face(s)',
                'Pocket(s)', 'Through Hole(s)', 'Total features', 'Blind Hole(s)_volume',
                'Countersink(s)_volume', 'Flat Bottom Hole(s)_volume', 'Pocket(s)_volume',
                'Through Hole(s)_volume', 'Volume', 'Length', 'Height', 'Surface_area',
                'Width', 'Machined_volume']
    for column in column_names:
        if column not in df.columns:
            df[column] = 0
    # Adding proper format to each column
    for column in column_names:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce').round(2)
    return df

#  Getting the group dataframe
def get_value_of_group_ce(val, grade, group):
    group_copy = group.copy()
    grp_val = 'Material Sub Group_' + grade[val]
    group_copy[grp_val] = 1
    mtrl_grp_df = pd.DataFrame([group_copy.values()], columns=group_copy.keys())
    return mtrl_grp_df



# Cost Calculation

# Machining cost Calculation
def calculate_machining_cost( machining_time, machine_hour_rate):
    mt = machining_time
    mc = machine_hour_rate / ((60 / mt ) * 0.8)
    return round(mc,2)

# Tooling cost Calculation
def calculate_tool_and_setup_costs(number_of_tools, machining_time, machine_hour_rate, number_of_parts):
    mt = machining_time
    nt = number_of_tools
    mhr = machine_hour_rate

    machining_cost = calculate_machining_cost( mt, mhr)
    # mch_wt = 1.15  # to given weightage to the machining cost for normalizing
    # machining_cost = (machining_cost/mch_wt)

    # Tooling cost calculation
    if mt / nt <= 10:
        tcf = 0.1
    elif 10 < mt / nt <= 20:
        tcf = 0.5
    elif 20 < mt / nt <= 30:
        tcf = 1
    elif 30 < mt / nt <= 39:
        tcf = 2
    else:
        tcf = 4

    tc = round((nt * 20 * tcf),2)

    # Setup cost calculation
    sh = 25 if (mt * 3) / 60 > 25 else (mt * 3) / 60
    sc = round(((sh * mhr) + (((nt * 3) / 60) * mhr) + (machining_cost + tc)),2)
    scpp = round((sc / number_of_parts),2)

    return tc, sc, scpp


# Total cost 
def calculate_total_machining_cost_per_part(cost_data):
    machining_cost = cost_data["Machining cost"]
    tooling_cost = cost_data["Tooling Cost per Part"]
    setup_cost_per_part = cost_data["Setup Cost per Part"]
    tmcp = (machining_cost + tooling_cost + setup_cost_per_part) * 1.05
    return round(tmcp,2)

# Post processing cost
def get_process_cost_ce(df, mtrl_grd, post_process):
    volume = df['Volume'][0]
    surface_area = df['Surface_area'][0]
    cost_per_kg = post_process_rate['Cost per Kg'][post_process]
    cost_per_square_inch = post_process_rate['Cost per sq inch'][post_process]

    post_cost_kg = volume * material_density[mtrl_grd] * (cost_per_kg / 1000000)
    post_cost_square_inch = surface_area * 0.00155 * cost_per_square_inch

    return round(max(post_cost_kg, post_cost_square_inch), 2)

# Raw Material cost:
class RawMaterialCalculator:
    def __init__(self, df, mtrl_grd, quantity):
        self.Length = df['Length'][0]
        self.Width = df['Width'][0]
        self.Height = df['Height'][0]
        self.density = material_density[mtrl_grd]
        try:
            self.rate = material_rate[mtrl_grd]
        except:
            self.rate = None
        self.quantity = quantity

    def get_raw_material_weight(self):
        extra_material = 4.0
        volume = (float(self.Length) + extra_material) * (float(self.Width) + extra_material) * (float(self.Height) + extra_material)
        weight = volume * self.density / 1000000
        return float(weight)

    def get_raw_material_cost(self):
        if self.rate is None:
            return 0
        else:
            weight = self.get_raw_material_weight()
            if self.quantity > 100:
                cost = weight * self.rate
                return cost
            else:
                first_case = weight * self.rate
                a = self.rate / self.quantity
                b = self.rate / 2.5
                second_case = min(a, b)
                third_case = 30
                return round(max(first_case, second_case, third_case), 2)

# Calculates the scrap savings based on the given DataFrame and material grade.
def calculate_scrap_savings(df, mtrl_grd):
    try:
        Length = df['Length'].iloc[0]
        Width = df['Width'].iloc[0]
        Height = df['Height'].iloc[0]
        part_volume = df['Volume'].iloc[0]
        density = material_density[mtrl_grd]
        extra_material = 4.0
        try:
            rate = material_rate[mtrl_grd]
        except KeyError:
            rate = 0
        stock_volume = (float(Length) + extra_material) * (float(Width) + extra_material) * (float(Height) + extra_material)
        scrap_savings = density * (((0.95 * (stock_volume - part_volume)) / 1000000) * (0.1 * rate))
        return round(scrap_savings,2)
    except (IndexError, KeyError):
        return 0

def calculate_total_cost_per_part(cost_data):
    mtrl_cost = cost_data.get('Raw Material cost', 0)
    machining_cost = cost_data.get('Total Machining Cost', 0)
    post_processing_cost = cost_data.get('Post Process cost', 0)
    scrap_savings = cost_data.get('Scrap Cost per Part', 0)
    qty = cost_data.get('Quantity', 1)

    total_cost_per_part = round((mtrl_cost + machining_cost + post_processing_cost - scrap_savings),2)
    total_cost = round((total_cost_per_part *qty),2)

    return total_cost_per_part, total_cost

# Cost data function to calculate all cost and store a=in dictionry
def calculate_cost_data(machine_time, machn_hr_rate, no_of_tool, quantity, final_df, Matrl_grd_ce, pp_name_ce):
    cost_data = {}

    cost_data["Quantity"] = quantity
    cost_data["Machining time"] = machine_time
    # Calculate machining cost
    cost_data["Machining cost"] = calculate_machining_cost(machine_time, machn_hr_rate)

    # Calculate tooling cost and setup cost
    cost_data["Tooling Cost per Part"], cost_data["Setup Cost"], cost_data["Setup Cost per Part"] = calculate_tool_and_setup_costs(no_of_tool, machine_time, machn_hr_rate, quantity)

    # Calculate total machining cost
    cost_data["Total Machining Cost"] = calculate_total_machining_cost_per_part(cost_data)

    # Calculate raw material cost
    cost_data["Raw Material cost"] = RawMaterialCalculator(final_df, Matrl_grd_ce, quantity).get_raw_material_cost()

    # Calculate scrap cost per part
    cost_data["Scrap Cost per Part"] = calculate_scrap_savings(final_df, Matrl_grd_ce)

    # Calculate post-process cost
    cost_data["Post Process cost"] = get_process_cost_ce(final_df, Matrl_grd_ce, pp_name_ce)

    # Calculate total cost per part and total cost
    cost_data["Total Cost per Part"], cost_data["Total Cost"] = calculate_total_cost_per_part(cost_data)

    return cost_data

# plot data for qty vs per part cost
def get_graph_qty_vs_per_part_cost(machine_time, machn_hr_rate, no_of_tool, final_df, Matrl_grd_ce, pp_name_ce, cost_df):
    data = []
    for i in range(1, 80, 2):
        data.append(calculate_cost_data(machine_time, machn_hr_rate, no_of_tool, i, final_df, Matrl_grd_ce, pp_name_ce))

    df = pd.DataFrame(data)

    # Create a trace for the line graph
    trace = go.Scatter(x=df["Quantity"], y=df["Total Cost per Part"], mode='lines',name='Total Cost per Part')

    # Add a marker for the highlighted value
    highlight_trace = go.Scatter(
        x=[cost_df["Quantity"].iloc[0]],
        y=[cost_df["Total Cost per Part"].iloc[0]],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Your Total Cost per Part'
    )

    # Create the layout for the graph
    layout = go.Layout(
        title='Per Part Cost Vs. Quantity',
        xaxis=dict(title='Quantity'),
        yaxis=dict(title='Total Cost per Part'),
        showlegend=True
    )

    # Create the figure
    fig = go.Figure(data=[trace, highlight_trace], layout=layout)

    # Show the plot
    st.info("Here is the forcast of Per Part cost vs Quantity.")
    st.plotly_chart(fig)


# def get_graph_qty_vs_per_part_cost(machine_time, machn_hr_rate, no_of_tool, final_df, Matrl_grd_ce, pp_name_ce,cost_df ):
#     data = []
#     for i in range(1, 101, 5):
#         data.append(calculate_cost_data(machine_time, machn_hr_rate, no_of_tool, i, final_df, Matrl_grd_ce, pp_name_ce))

#     df = pd.DataFrame(data)
#     st.dataframe(df)

#     # Create subplots with one shared x-axis
#     fig = make_subplots(specs=[[{"secondary_y": True}]])

#     # Add line graph trace for Total Cost per Part
#     fig.add_trace(
#         go.Scatter(x=df["Quantity"], y=df["Total Cost per Part"], mode='lines', name='Total Cost per Part'),
#         secondary_y=False
#     )

#     # Add marker trace for highlighted cost
#     fig.add_trace(
#         go.Scatter(x=[cost_df["Quantity"].iloc[0]], y=[cost_df["Total Cost per Part"].iloc[0]], mode='markers', marker=dict(color='red', size=10),
#                    name='Your Total Cost per Part'),
#         secondary_y=False
#     )

#     # Add line graph trace for Total Cost
#     fig.add_trace(
#         go.Scatter(x=df["Quantity"], y=df["Total Cost"], mode='lines', name='Total Cost'),
#         secondary_y=True
#     )

#     # Configure axes labels
#     fig.update_xaxes(title_text='Quantity')
#     fig.update_yaxes(title_text='Total Cost per Part', secondary_y=False)
#     fig.update_yaxes(title_text='Total Cost', secondary_y=True)

#     # Show the plot
#     st.plotly_chart(fig)


# data preparation for difficulty factor
def prepare_difficulty_factor_data(df):
    df_columns= ['Blind Hole(s)', 'Circular Milled Face(s)', 'Concave Fillet Edge Milling Face(s)', 'Convex Profile Edge Milling Face(s)', 'Countersink(s)', 'Curved Milled Face(s)', 'Flat Bottom Hole(s)', 'Flat Face Milled Face(s)', 'Flat Side Milled Face(s)', 'Pocket(s)', 'Through Hole(s)', 'Total features']
    df_selected = df[df_columns]
    return df_selected

# data preparation for nos of tool
def prepare_nos_tool_data(df):
    df_columns= ['Blind Hole(s)', 'Circular Milled Face(s)', 'Concave Fillet Edge Milling Face(s)', 'Convex Profile Edge Milling Face(s)', 'Countersink(s)', 'Curved Milled Face(s)', 'Flat Bottom Hole(s)', 'Flat Face Milled Face(s)', 'Flat Side Milled Face(s)', 'Pocket(s)', 'Radius', 'Through Hole(s)', 'Total features']
    df_selected = df[df_columns]
    return df_selected

# Display warning messages for complex DF
def display_warning(difficulty_factor):
    warning_message = f"I'm afraid the CAD model is {difficulty_factor} and there might be complex features.\n\n" \
                      "Manual quotation is required."
    st.warning(warning_message)

#  Display warning messages for file is not proper
def display_warning_file():
    warning_message = f"I'm afraid the file is not Proper or there might be some data missing.\n\n" \
                      "Please! recheck an upload the file again!!."
    st.warning(warning_message)



