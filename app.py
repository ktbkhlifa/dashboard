import streamlit as st
import pandas as pd
import time
import plotly.express as px
import io

# Set page configuration for a modern, clean look
st.set_page_config(layout="wide", page_title="Advanced Agrivoltaic Dashboard", page_icon="📈")

# Function to load and preprocess data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Time'] = pd.to_datetime(df.iloc[:, 0])
    df.set_index('Time', inplace=True)
    return df

# Initialize session state variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# --- Dashboard Title and Description ---
st.title("🌱 Advanced Agrivoltaic Simulation Dashboard")
st.markdown("### 📊 Dashboard interactif et moderne pour l'analyse des données agrivoltaïques.")
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

# --- Filtres de données (flexible date range) ---
st.sidebar.header("🗓️ Filtres de Données")
min_date = df_open_field.index.min().date()
max_date = df_open_field.index.max().date()

start_date = st.sidebar.date_input("Date de début", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Date de fin", value=max_date, min_value=min_date, max_value=max_date)

# Convert dates back to datetime for filtering
start_datetime = pd.to_datetime(f"{start_date} 00:00:00+00:00")
end_datetime = pd.to_datetime(f"{end_date} 23:59:59+00:00")

# Filter data based on selected dates
df_open_field_filtered = df_open_field.loc[start_datetime:end_datetime]
df_agrivoltaic_filtered = df_agrivoltaic.loc[start_datetime:end_datetime]

# --- Affichage des KPIs (Key Performance Indicators) ---
st.markdown("### 📈 Indicateurs Clés de Performance (KPIs)")
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

# Get the latest data point from the filtered data
if not df_open_field_filtered.empty:
    latest_open_field = df_open_field_filtered.iloc[-1]
    latest_agrivoltaic = df_agrivoltaic_filtered.iloc[-1]

    kpi_col1.metric(
        label="☀️ GHI Champ Ouvert (W/m²)",
        value=f"{latest_open_field['GHI_Open_Field (W/m2)']:.2f}",
        delta=f"{latest_open_field['GHI_Open_Field (W/m2)'] - latest_agrivoltaic['GHI_Agrivoltaic (W/m2)']:.2f} différence"
    )
    kpi_col2.metric(
        label="☀️ GHI Agrivoltaïque (W/m²)",
        value=f"{latest_agrivoltaic['GHI_Agrivoltaic (W/m2)']:.2f}"
    )
    kpi_col3.metric(
        label="🌡️ Temp. Champ Ouvert (°C)",
        value=f"{latest_open_field['Temperature_Open_Field (C)']:.2f}",
        delta=f"{latest_open_field['Temperature_Open_Field (C)'] - latest_agrivoltaic['Temperature_Agrivoltaic (C)']:.2f} différence"
    )
    kpi_col4.metric(
        label="🌡️ Temp. Agrivoltaïque (°C)",
        value=f"{latest_agrivoltaic['Temperature_Agrivoltaic (C)']:.2f}"
    )

st.markdown("---")

# --- Graphiques (Plots) ---
st.markdown("### 📊 Tendances et Analyses Détaillées")
st.subheader("GHI (Global Horizontal Irradiance) sur la Période Sélectionnée")

# Prepare data for plotting with Plotly Express
df_plot = pd.DataFrame({
    'Time': df_open_field_filtered.index,
    'GHI_Open_Field': df_open_field_filtered['GHI_Open_Field (W/m2)'],
    'GHI_Agrivoltaic': df_agrivoltaic_filtered['GHI_Agrivoltaic (W/m2)']
}).melt(id_vars='Time', var_name='Type', value_name='GHI (W/m²)')

# Create an interactive line chart with Plotly Express
fig_ghi = px.line(df_plot, x='Time', y='GHI (W/m²)', color='Type', 
                  labels={'Time': 'Date', 'GHI (W/m²)': 'Irradiance (W/m²)'},
                  title='Comparaison de GHI : Champ Ouvert vs. Agrivoltaïque')
st.plotly_chart(fig_ghi, use_container_width=True)

st.subheader("Température sur la Période Sélectionnée")
# Prepare data for plotting
df_temp_plot = pd.DataFrame({
    'Time': df_open_field_filtered.index,
    'Temp_Open_Field': df_open_field_filtered['Temperature_Open_Field (C)'],
    'Temp_Agrivoltaic': df_agrivoltaic_filtered['Temperature_Agrivoltaic (C)']
}).melt(id_vars='Time', var_name='Type', value_name='Temp (°C)')

fig_temp = px.line(df_temp_plot, x='Time', y='Temp (°C)', color='Type',
                   labels={'Time': 'Date', 'Temp (°C)': 'Température (°C)'},
                   title='Comparaison de Température : Champ Ouvert vs. Agrivoltaïque')
st.plotly_chart(fig_temp, use_container_width=True)

st.markdown("---")

# --- Téléchargement du rapport (Download Report) ---
st.markdown("### 📥 Télécharger le Rapport")

# Function to convert the filtered data to CSV
@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: The cache function should be stateless and deterministic.
    return df.to_csv(index=True).encode('utf-8')

report_csv = convert_df_to_csv(pd.concat([df_open_field_filtered, df_agrivoltaic_filtered], axis=1))

st.download_button(
    label="Télécharger le rapport complet (CSV)",
    data=report_csv,
    file_name='agrivoltaic_report.csv',
    mime='text/csv',
    help='Cliquez ici pour télécharger un fichier CSV contenant les données de la période sélectionnée.'
)

st.info("Le dashboard se met à jour automatiquement avec la date que vous choisissez. Il n'y a pas de bouton 'live' dans cette version, car la sélection de la date est plus flexible.")
