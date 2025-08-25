import streamlit as st
import pandas as pd
import time
import altair as alt

# Set page configuration for a modern, clean look
st.set_page_config(layout="wide", page_title="Live Agrivoltaic Dashboard", page_icon="📈")

# Function to load and preprocess data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    # The first column is the timestamp, let's make it the index
    # Note: Using the first column by position (iloc[:, 0]) for flexibility
    df['Time'] = pd.to_datetime(df.iloc[:, 0])
    df.set_index('Time', inplace=True)
    return df

# Initialize session state variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# --- Dashboard Title and Description ---
st.title("🌱 Live Agrivoltaic Simulation Dashboard")
st.markdown("### 📊 Displaying live data from a full year simulation to showcase system capabilities.")
st.markdown("---")

# --- Load the data ---
file_path_open_field = "full_simulation_data.csv"
file_path_agrivoltaic = "full_simulation_data1.csv"

try:
    df_open_field = load_data(file_path_open_field)
    df_agrivoltaic = load_data(file_path_agrivoltaic)
except FileNotFoundError:
    st.error("One or both CSV files were not found. Please make sure 'full_simulation_data.csv' and 'full_simulation_data1.csv' are in the same directory as the script.")
    st.stop()
    
total_rows = len(df_open_field)

# Get the latest data point
current_data_open_field = df_open_field.iloc[st.session_state.current_index]
current_data_agrivoltaic = df_agrivoltaic.iloc[st.session_state.current_index]

# --- Display KPIs (Key Performance Indicators) ---
with st.container():
    st.markdown("### 📈 Current Key Metrics")
    st.markdown("---")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    # GHI (Global Horizontal Irradiance) KPI
    kpi_col1.metric(
        label="GHI Open Field (W/m²)",
        value=f"{current_data_open_field['GHI_Open_Field (W/m2)']:.2f}",
        delta=f"{current_data_open_field['GHI_Open_Field (W/m2)'] - current_data_agrivoltaic['GHI_Agrivoltaic (W/m2)']:.2f} difference"
    )
    kpi_col2.metric(
        label="GHI Agrivoltaic (W/m²)",
        value=f"{current_data_agrivoltaic['GHI_Agrivoltaic (W/m2)']:.2f}"
    )

    # Temperature KPI
    kpi_col3.metric(
        label="Temp. Open Field (°C)",
        value=f"{current_data_open_field['Temperature_Open_Field (C)']:.2f}",
        delta=f"{current_data_open_field['Temperature_Open_Field (C)'] - current_data_agrivoltaic['Temperature_Agrivoltaic (C)']:.2f} difference"
    )
    kpi_col4.metric(
        label="Temp. Agrivoltaic (°C)",
        value=f"{current_data_agrivoltaic['Temperature_Agrivoltaic (C)']:.2f}"
    )

st.markdown("---")

# --- Main Charts ---
st.markdown("### 📊 Trends Over Time")

# Get the data subset for the chart
data_to_display = pd.concat([
    df_open_field.iloc[:st.session_state.current_index + 1].rename(columns={'GHI_Open_Field (W/m2)': 'GHI'}),
    df_agrivoltaic.iloc[:st.session_state.current_index + 1].rename(columns={'GHI_Agrivoltaic (W/m2)': 'GHI'})
])
data_to_display['Type'] = ['Open Field'] * (st.session_state.current_index + 1) + ['Agrivoltaic'] * (st.session_state.current_index + 1)
data_to_display.reset_index(inplace=True)

# Create a line chart for GHI using Altair
chart = alt.Chart(data_to_display).mark_line().encode(
    x=alt.X('Time', axis=alt.Axis(title='Time')),
    y=alt.Y('GHI', axis=alt.Axis(title='GHI (W/m²)')),
    color='Type'
).properties(
    title='GHI Comparison: Open Field vs. Agrivoltaic'
).interactive()

st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# --- Control Panel for "Live" simulation ---
st.markdown("### ▶️ Live Simulation Control")

# Button to advance the simulation
if st.button("Advance 1 Hour"):
    if st.session_state.current_index < total_rows - 1:
        st.session_state.current_index += 1
        st.experimental_rerun()
    else:
        st.info("Simulation finished! All data points have been displayed.")
        st.session_state.current_index = 0
        st.info("Simulation has been reset.")
        st.experimental_rerun()