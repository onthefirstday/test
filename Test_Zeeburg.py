import pandas as pd
import streamlit as st
# import seaborn as sns
import pickle
import matplotlib.pyplot as plt

st.title('Test')

path = 'C:\\Users\\eheath\\OneDrive - HvA\\Documents\\HvA\\Future Charging\\Zeeburg Batterij III\\data'

# start_date = '2024-06-24'
# end_date = '2024-09-10'

# @st.cache_data()
# def load_data(start_date, end_date):
#     with open(f'{path}\\240909 - Full_df.pkl','rb') as infile:
#         return pickle.load(infile).query('index >= @start_date and index < @end_date')
    
@st.cache_data()
def load_data():
    with open(f'{path}\\small_df.pkl','rb') as infile:
        return pickle.load(infile)
    
    
df_slice = load_data()

def CP_split(dataframe, column1, val1, column2 = None, val2 = None):
    if column2 is None:
        return dataframe.loc[(dataframe[column1] == val1)]
    else:
        return dataframe.loc[(dataframe[column1] == val1) & (dataframe[column2] == val2)]
    
    
df_slice_connected = CP_split(df_slice, 'type', 'VehicleConnected')
df_slice_P = CP_split(df_slice, 'type', '3PhaseActivePowW')

df_slice_P.loc[df_slice_P['v'] >= 100, 'charging'] = 1
df_slice_P.loc[df_slice_P['v'] < 100, 'charging'] = 0

# Total system occupancy
df_slice_connected_grouped = pd.DataFrame(df_slice_connected['v'].groupby(level=0).sum())
# df_slice_connected_grouped['index'] = df_slice_connected_grouped.index
df_slice_connected_grouped = pd.DataFrame(df_slice_connected_grouped['v'].round(0))

df_slice_connected_grouped['Day'] = df_slice_connected_grouped.index.day_name()

# Total system active charging occupancy
df_slice_charging_grouped = pd.DataFrame(df_slice_P['charging'].groupby(level=0).sum())
# df_slice_connected_grouped['index'] = df_slice_connected_grouped.index
df_slice_charging_grouped = pd.DataFrame(df_slice_charging_grouped['charging'].round(0))

df_slice_charging_grouped['Day'] = df_slice_charging_grouped.index.day_name()

def slicer(df, number, query):
    df_temp = df[df['type'].astype(str).str[:number] == query]
    return df_temp

# AC & DC power at battery inverter
P_AC_INV = slicer(df_slice, 7, 'PAC_INV')#.groupby(level=0).sum()
P_AC_INV = P_AC_INV[(P_AC_INV['type'].astype(str).str[7:] == '1') | (P_AC_INV['type'].astype(str).str[7:] == '2') | (P_AC_INV['type'].astype(str).str[7:] == '3') | (P_AC_INV['type'].astype(str).str[7:] == '4')].groupby(level=0)['v'].sum()


# AC power for the 'energy counters'
P_AC_EC_1 = slicer(df_slice, 8,'PAC_1_EC')#.groupby(level=0).sum()
P_AC_EC_2 = slicer(df_slice, 8,'PAC_2_EC')#.groupby(level=0).sum()
P_AC_EC_3 = slicer(df_slice, 8,'PAC_3_EC')#.groupby(level=0).sum()

soc_slice = df_slice.loc[df_slice.sensor == 'ams-a-bat-he']


# def plot():
#     layout = go.Layout(
#         xaxis=dict(title="DateTime", ticks='', color='white'),
#         yaxis=dict(color='white'),
#         title=name,
#         paper_bgcolor='#2d2d2d',
#         plot_bgcolor='#2d2d2d'
#     )

#     fig = go.Figure(layout=layout)
    
    
plt.style.use('default')
plt.rcParams.update({'font.size': 22})
fig, ax = plt.subplots(3,1,figsize=(16,8))
ax[0].plot(P_AC_INV, label = 'Battery', color='tab:green')
ax[0].plot(P_AC_EC_1['v'], label = 'Grid Import', color='tab:red')
ax[0].plot(P_AC_EC_3['v'], label = 'Load', color='tab:brown')
ax[0].set_ylabel('Power [kW]')
ax[0].legend(loc='upper right')

ax[1].plot(soc_slice['v'], label = 'SOC', color='tab:blue')
ax[1].set_ylabel('SOC [%]')
ax[1].legend(loc='upper right')

ax[2].plot(df_slice_connected_grouped['v'], label = 'Occupancy', color='k') 
ax[2].plot(df_slice_charging_grouped['charging'], label = 'Charging', color='tab:cyan')
ax[2].set_ylabel('Occupancy')
# ax[2].yaxis.set_major_locator(ticker.MultipleLocator(2))
ax[2].legend(loc='upper right')

ax[0].grid()
ax[1].grid()
ax[2].grid()
fig.tight_layout()


st.pyplot(fig)







#%%
# df_slice = df_slice.loc[(df_slice.type == 'VehicleConnected') |
#                         (df_slice.type == '3PhaseActivePowW') | 
#                         (df_slice.type == 'PAC_INV') |
#                         (df_slice.type == 'PAC_1_EC') | 
#                         (df_slice.type == 'PAC_2_EC') | 
#                         (df_slice.type == 'PAC_3_EC') | 
#                         (df_slice.sensor == 'ams-a-bat-he')]

# df_slice.to_pickle(f'{path}\\small_df.pkl')  
