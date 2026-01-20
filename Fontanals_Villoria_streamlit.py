"""
Authors: Oriol Fontanals & Nicolas Villoria
Title: NSF Grants Explorer - Streamlit Application
Description: Analyzes NSF active grants from 2020-2025 including terminated grants from the Trump administration
"""

import streamlit as st
import altair as alt
import json
import streamlit.components.v1 as components

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
    .stAppHeader {background-color: transparent !important; display: none !important;}
    .stSidebar {background-color: white !important;}
    .stSidebar, .stSidebar * {color: black !important;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem; background-color: white !important;}
    .stMainBlockContainer {padding-top: 0rem !important; margin-top: 0rem !important;}
    header {visibility: hidden;}
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
# DATA LOADING 
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

# Render as HTML to prevent blinking on Linux
# Disable vegafusion and max rows limit to avoid dependencies
alt.data_transformers.enable('default', max_rows=None)
chart_spec = final_chart.to_dict()
vega_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    html, body {{ margin: 0; padding: 0; background-color: white; }}
    #vis {{ width: 100%; display: flex; justify-content: center; align-items: flex-start; }}
  </style>
</head>
<body>
  <div id="vis"></div>
  <script type="text/javascript">
    var spec = {json.dumps(chart_spec)};
    vegaEmbed('#vis', spec, {{
      "actions": false,
      "renderer": "svg"
    }});
  </script>
</body>
</html>
"""
components.html(vega_html, height=1100, scrolling=True)

# ============================================================================
