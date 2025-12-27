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
    create_directorate_evolution_chart,
    prepare_termination_impact_data,
    create_termination_impact_chart,
    prepare_lifecycle_data,
    prepare_lifecycle_data_with_statecode,
    create_linked_map_and_lifecycle,
    prepare_political_data,
    create_political_scatter
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
    lifecycle_df_linked = prepare_lifecycle_data_with_statecode(df)
    political_source = prepare_political_data(df, political_df)
    
    return {
        'df': df,
        'grants_by_state': grants_by_state,
        'directorate_data': directorate_data,
        'termination_impact': termination_impact,
        'lifecycle_df': lifecycle_df,
        'lifecycle_df_linked': lifecycle_df_linked,
        'political_source': political_source
    }

# Load data
data = get_data()

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
# MAIN CONTENT - COMPACT GRID LAYOUT
# ============================================================================

# ============================================================================
# ROW 1: Linked Map + Lifecycle Chart (full width)
# ============================================================================

st.markdown(f"##### Q1 & Q4-5: Grants by State ({selected_year}) - click to filter, shift+click multi-select, double-click reset")
linked_chart = create_linked_map_and_lifecycle(
    data['grants_by_state'], 
    data['lifecycle_df_linked'],
    selected_year
)
st.altair_chart(linked_chart, use_container_width=True)

# ============================================================================
# ROW 2: Directorate Evolution (left) + Termination Impact (right)
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Q2: Directorate Evolution")
    evolution_chart = create_directorate_evolution_chart(data['directorate_data'])
    st.altair_chart(evolution_chart, use_container_width=True)

with col2:
    st.markdown("##### Q3: Termination Impact by Directorate")
    termination_chart = create_termination_impact_chart(data['termination_impact'])
    st.altair_chart(termination_chart, use_container_width=True)

# ============================================================================
# ROW 3: Political Analysis (full width, compact)
# ============================================================================

st.markdown(f"##### Q6: Political Alignment ({selected_year})")
political_chart = create_political_scatter(data['political_source'], selected_year)
st.altair_chart(political_chart, use_container_width=True)

