"""
NSF Grants Explorer - Streamlit Application
Analyzes NSF grants from 2020-2025 including terminated grants from the Trump administration
"""

import streamlit as st
import pandas as pd
import altair as alt

# Import analysis functions
from analysis_functions import (
    load_data,
    load_political_data,
    prepare_grants_by_state_data,
    create_choropleth_map,
    prepare_directorate_data,
    create_directorate_evolution_chart,
    prepare_termination_impact_data,
    create_termination_impact_chart,
    prepare_lifecycle_data,
    create_state_evolution_with_termination,
    prepare_political_data,
    create_political_scatter,
    STATE_COLOR_MAP
)

# Page configuration
st.set_page_config(
    page_title="NSF Grants Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default padding for compact view and set white background
st.markdown("""
<style>
    .stApp {background-color: white !important; color: black !important;}
    .stAppHeader {background-color: transparent !important;}
    .stSidebar {background-color: white !important;}
    .stSidebar, .stSidebar * {color: gray !important;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; background-color: white !important;}
    h1, h2, h3, h4, h5, h6, p, span, label {color: black !important;}
    button, .stButton button {background-color: gray !important; color: white !important;}
    .stMarkdown, .stMarkdown * {color: black !important;}
    .stMetric label, .stMetric div {color: black !important;}
    h1 {font-size: 1.5rem !important; margin-bottom: 0.5rem !important;}
    h2 {font-size: 1.2rem !important; margin-bottom: 0.3rem !important;}
    h3 {font-size: 1rem !important; margin-bottom: 0.2rem !important;}
    .stMetric {padding: 0.3rem !important;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING (cached)
# ============================================================================

@st.cache_data
def get_data():
    """Load and cache all data."""
    df = load_data()
    political_df = load_political_data()
    grants_by_state = prepare_grants_by_state_data(df)
    directorate_data = prepare_directorate_data(df)
    termination_impact = prepare_termination_impact_data(df)
    lifecycle_df = prepare_lifecycle_data(df)
    political_source = prepare_political_data(df, political_df)
    
    return {
        'df': df,
        'grants_by_state': grants_by_state,
        'directorate_data': directorate_data,
        'termination_impact': termination_impact,
        'lifecycle_df': lifecycle_df,
        'political_source': political_source
    }

# Load data
data = get_data()

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

st.sidebar.title("🔬 NSF Grants Explorer")

# Year Selection (Global)
selected_year = st.sidebar.slider(
    "📅 Select Year",
    min_value=2020,
    max_value=2025,
    value=2025,
    step=1,
    help="Controls year filter for all visualizations"
)

# State Selection
st.sidebar.markdown("---")
available_states = sorted(data['lifecycle_df']['State'].unique().tolist())
selected_states = st.sidebar.multiselect(
    "🗺️ Select States (max 8)",
    options=available_states,
    default=[],
    max_selections=8,
    help="Select states to compare in evolution charts"
)

# Termination Metric Selection
st.sidebar.markdown("---")
termination_metric = st.sidebar.radio(
    "⚠️ Termination Metric",
    options=['terminated_grants', 'termination_pct'],
    format_func=lambda x: 'Count' if x == 'terminated_grants' else 'Rate (%)',
    horizontal=True
)

st.sidebar.markdown("---")
st.sidebar.caption("NSF grants 2020-2025 | By Nicolás Villoria & Oriol Fontanals")

# ============================================================================
# MAIN CONTENT - COMPACT GRID LAYOUT
# ============================================================================

# ============================================================================
# ROW 1: Map (left) + Directorate Evolution (right)
# ============================================================================

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown(f"##### Q1: Grants by State ({selected_year})")
    map_chart = create_choropleth_map(data['grants_by_state'], selected_year, selected_states if selected_states else None)
    st.altair_chart(map_chart, use_container_width=True)

with col2:
    st.markdown("##### Q2: Directorate Evolution")
    evolution_chart = create_directorate_evolution_chart(data['directorate_data'])
    st.altair_chart(evolution_chart, use_container_width=True)

# ============================================================================
# ROW 2: Termination Impact (left) + State Evolution (right)
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Q3: Termination Impact by Directorate")
    termination_chart = create_termination_impact_chart(data['termination_impact'], termination_metric)
    st.altair_chart(termination_chart, use_container_width=True)

with col2:
    states_label = ', '.join(selected_states[:3]) + ('...' if len(selected_states) > 3 else '') if selected_states else 'All States'
    st.markdown(f"##### Q4-5: Grants Evolution ({states_label})")
    combined_chart = create_state_evolution_with_termination(
        data['df'], 
        data['lifecycle_df'], 
        selected_states if selected_states else None
    )
    st.altair_chart(combined_chart, use_container_width=True)

# ============================================================================
# ROW 3: Political Analysis (full width but compact)
# ============================================================================

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(f"##### Q6: Political Alignment ({selected_year})")
    political_chart = create_political_scatter(data['political_source'], selected_year, selected_states if selected_states else None)
    st.altair_chart(political_chart, use_container_width=True)

with col2:
    year_data = data['political_source'][data['political_source']['year'] == selected_year]
    dem_grants = year_data[year_data['political_alignment'] == 'Democrat']['active_grants'].sum()
    dem_funding = year_data[year_data['political_alignment'] == 'Democrat']['total_funding_millions'].sum()
    st.markdown("##### 🔵 Democrat States")
    st.metric("Grants", f"{dem_grants:,}")
    st.metric("Funding", f"${dem_funding:,.0f}M")

with col3:
    rep_grants = year_data[year_data['political_alignment'] == 'Republican']['active_grants'].sum()
    rep_funding = year_data[year_data['political_alignment'] == 'Republican']['total_funding_millions'].sum()
    st.markdown("##### 🔴 Republican States")
    st.metric("Grants", f"{rep_grants:,}")
    st.metric("Funding", f"${rep_funding:,.0f}M")

