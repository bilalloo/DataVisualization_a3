import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Global Emissions Dashboard")

# Load and process data
@st.cache_data
def load_data():
    df = pd.read_csv('dataset.csv')
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Missing `dataset.csv`. Please ensure it is in the same folder.")
    st.stop()

# Basic calculations for facts
total_co2 = df['value'].sum()
global_data_no_world = df[df['country'] != 'WORLD']
sector_data = global_data_no_world.groupby('sector')['value'].sum().reset_index()
highest_sector = sector_data.loc[sector_data['value'].idxmax()]

# --- Aesthetic Customization ---
# Main chart colors: different shades of green
COLOR_SCALE = ["#238b45", "#41ab5d", "#74c476", "#a1d99b", "#c7e9c0", "#e5f5e0"]

# --- Sidebar Controls ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/29/Go-home_copy_%28green_gradient%29.svg", width=100) # Optional decoration
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("---")

# Fun Fact 1: Global Impact
st.sidebar.metric(
    label="🌍 Total CO2 Tracked",
    value=f"{total_co2/1000:.1f}k GT",
    help="Total sum of values in dataset, likely GT/kilo-tonnes."
)
st.sidebar.info(
    f"💡 Fun Fact: The dataset spans **{df['date'].nunique()}** unique days, "
    f"averaging about **{total_co2/df['date'].nunique():.1f}** units per day tracked."
)

st.sidebar.markdown("---")

# Filter: Sector
sectors = df['sector'].unique().tolist()
sectors.insert(0, "All")
selected_sector = st.sidebar.selectbox("🔎 Filter by Sector:", sectors)

# Encode: Scale
y_scale_type = st.sidebar.radio("📊 Encode Axis Scale:", ("linear", "log"))

# --- Dashboard Layout (Visual Style like Example 2) ---

st.title("Global Carbon Emissions Dashboard")
st.markdown("---")

# Top Row: 2 Charts
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Emissions by Country ({selected_sector} Sectors)")
    
    # Filtering Data
    filtered_df = df[df['country'] != 'WORLD']
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df['sector'] == selected_sector]
    
    # Aggregating for Bar Chart
    bar_data = filtered_df.groupby('country')['value'].sum().sort_values(ascending=False).reset_index()

    # Reconfigure is implicit in Plotly's interactive sorting
    fig_bar = px.bar(
        bar_data,
        x='country',
        y='value',
        color='value',
        color_continuous_scale="Greens",
        labels={'value': 'Total CO2 Emissions', 'country': 'Country'},
        template="plotly_white"
    )
    
    fig_bar.update_layout(
        yaxis_type=y_scale_type,
        xaxis={'categoryorder': 'total descending'} # Default sort
    )
    
    # Elaborate: Selection/Connect is handled by click, but simpler to 
    # use Plotly's internal selection capability or a simple dropdown selection.
    selected_country