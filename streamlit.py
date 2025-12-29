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
    prepare_directorate_data,
    prepare_termination_impact_data,
    prepare_lifecycle_data_with_statecode,
    prepare_political_data,
    final_vis
)

# Page configuration
st.set_page_config(
    page_title="NSF Grants Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default padding for compact view and set white background
st.markdown("""
<style>
    .stApp {background-color: white !important; color: black !important;}
    .stAppHeader {background-color: transparent !important;}
    .stSidebar {background-color: white !important;}
    .stSidebar, .stSidebar * {color: black !important;}
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
# SIDEBAR CONTROLS
# ============================================================================

st.sidebar.title("NSF Grants Explorer")

# Year Selection with 2x3 button grid
st.sidebar.markdown("### Select Year")

# Initialize selected year in session state
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = 2025

# Create 2x3 grid of year buttons in sidebar
with st.sidebar:
    year_row1 = st.columns(3)
    year_row2 = st.columns(3)
    
    years = [2020, 2021, 2022, 2023, 2024, 2025]
    
    for i, year in enumerate(years[:3]):
        with year_row1[i]:
            if st.button(
                str(year), 
                key=f"year_{year}",
                use_container_width=True,
                type="primary" if st.session_state.selected_year == year else "secondary"
            ):
                st.session_state.selected_year = year
                st.rerun()
    
    for i, year in enumerate(years[3:]):
        with year_row2[i]:
            if st.button(
                str(year), 
                key=f"year_{year}",
                use_container_width=True,
                type="primary" if st.session_state.selected_year == year else "secondary"
            ):
                st.session_state.selected_year = year
                st.rerun()

selected_year = st.session_state.selected_year

st.sidebar.markdown("---")
st.sidebar.caption("NSF grants 2020-2025 | By Nicolás Villoria & Oriol Fontanals")

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
    termination_impact_df = prepare_termination_impact_data(df)
    lifecycle_df = prepare_lifecycle_data_with_statecode(df)
    political_source_df = prepare_political_data(df, political_df)
    
    return {
        'df': df,
        'grants_by_state': grants_by_state,
        'directorate_data': directorate_data,
        'termination_impact_df': termination_impact_df,
        'lifecycle_df': lifecycle_df,
        'political_source_df': political_source_df
    }

# Load data
data = get_data()

# ============================================================================
# MAIN CONTENT - COMPACT GRID LAYOUT
# ============================================================================

# Generate final visualization based on selected year
final_chart = final_vis(
    data['df'],
    data['grants_by_state'],
    data['lifecycle_df'],
    data['directorate_data'],
    data['termination_impact_df'],
    data['political_source_df'],
    selected_year
)
st.altair_chart(final_chart, use_container_width=True)

# ============================================================================
