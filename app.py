import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config & Font Injection ---
st.set_page_config(layout="wide", page_title="Global Emissions Dashboard")

# Injecting CSS to force the Aptos font across the app
st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Aptos', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

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
# Reverted to the original green scale for the pie chart and line chart
COLOR_SCALE = ["#238b45", "#41ab5d", "#74c476", "#a1d99b", "#c7e9c0", "#e5f5e0"]

# Custom scale for the Bar Chart: Replacing the "white" end of the Greens scale with Black
BAR_BLACK_GREEN_SCALE = ["#000000", "#74c476", "#238b45", "#00441b"]

# --- Sidebar Controls ---
st.sidebar.image("M.Bilal.png", use_container_width=True)
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("---")

# Fun Fact 1: Global Impact
st.sidebar.metric(
    label="🌍 Total CO2 Tracked",
    value=f"{total_co2/1000:.1f}k GT",
    help="Total sum of values in dataset."
)
st.sidebar.info(
    f"💡 **Fun Fact:** The dataset spans **{df['date'].nunique()}** unique days, "
    f"averaging about **{total_co2/df['date'].nunique():.1f}** units per day tracked."
)

# Injecting CSS to force the Aptos font but protect Streamlit's icons
st.markdown("""
    <style>
    /* Apply Aptos to standard text elements */
    html, body, p, div, h1, h2, h3, h4, h5, h6, span, label {
        font-family: 'Aptos', sans-serif;
    }
    /* Force Streamlit's UI icons to stay as icons instead of text */
    [data-testid="stIconMaterial"], .material-symbols-rounded, svg {
        font-family: 'Material Symbols Rounded' !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Select & Connect
countries = df[df['country'] != 'WORLD']['country'].unique().tolist()
countries.sort()
selected_country = st.sidebar.selectbox("🔗 Connect: Select Country", countries, index=0)

# 2. Filter: Sector
sectors = df['sector'].unique().tolist()
sectors.insert(0, "All")
selected_sector = st.sidebar.selectbox("🔎 Filter: Select Sector", sectors)

# 3. Encode: Scale
y_scale_type = st.sidebar.radio("📊 Encode: Axis Scale", ("linear", "log"))

# --- Dashboard Layout ---

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

    fig_bar = px.bar(
        bar_data,
        x='country',
        y='value',
        color='value',
        color_continuous_scale=BAR_BLACK_GREEN_SCALE, # APPLIED BLACK-TO-GREEN HERE
        labels={'value': 'Total CO2 Emissions', 'country': 'Country'},
        template="plotly_white"
    )
    
    fig_bar.update_layout(
        yaxis_type=y_scale_type,
        xaxis={'categoryorder': 'total descending'} 
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # Aggregating for Donut Chart
    donut_data_raw = df[(df['country'] == selected_country) & (df['country'] != 'WORLD')]
    if selected_sector != "All":
         donut_data_raw = donut_data_raw[donut_data_raw['sector'] == selected_sector]

    donut_data = donut_data_raw.groupby('sector')['value'].sum().reset_index()

    st.subheader(f"Sector Breakdown: {selected_country}")
    if not donut_data.empty:
        fig_donut = px.pie(
            donut_data, 
            values='value', 
            names='sector', 
            hole=0.6, 
            color_discrete_sequence=COLOR_SCALE, # REVERTED TO GREEN
            template="plotly_white"
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.warning(f"No data available for {selected_country} in sector {selected_sector}.")

st.markdown("---")

# Bottom Row: Trend + Fun Facts
col3, col4 = st.columns([2, 1])

with col3:
    st.subheader(f"Emissions Trend Over Time ({selected_country}, {selected_sector})")
    
    # Filtering for Trend
    trend_df = df[df['country'] == selected_country]
    if selected_sector != "All":
        trend_df = trend_df[trend_df['sector'] == selected_sector]
    
    # Aggregating daily
    trend_data = trend_df.groupby('date')['value'].sum().reset_index()
    
    fig_trend = px.line(
        trend_data,
        x='date',
        y='value',
        color_discrete_sequence=[COLOR_SCALE[0]], # REVERTED TO GREEN
        labels={'value': 'Daily Emissions', 'date': 'Date'},
        template="plotly_white"
    )
    fig_trend.update_layout(yaxis_type=y_scale_type)
    st.plotly_chart(fig_trend, use_container_width=True)

with col4:
    st.subheader("💡 Sector Fun Facts")
    
    fact_col_a, fact_col_b = st.columns(2)
    
    with fact_col_a:
        st.success(f"**Dominant Sector:**\n\n{highest_sector['sector']}\n\n({highest_sector['value']/1000:.1f}k units globally)")
    
    with fact_col_b:
        # Domestic Aviation contribution percent
        dom_av = sector_data[sector_data['sector'] == 'Domestic Aviation']
        if not dom_av.empty:
            percent_av = (dom_av['value'].values[0] / total_co2) * 100
            st.warning(f"✈️ **Domestic Aviation:**\n\nContributes **{percent_av:.1f}%** of all tracked global emissions.")
        else:
            st.info("✈️ Aviation data not available.")
            
    st.markdown("---")
    st.info(
        f"**Insight:** The data highlights how industrial and power sectors often dominate "
        f"national outputs, but the 'Ground Transport' sector is frequently the "
        f"largest component of emissions in many consumer-driven economies."
    )
