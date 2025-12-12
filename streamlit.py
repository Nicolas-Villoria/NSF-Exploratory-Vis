"""
NSF Grants Explorer - Streamlit Application
Analyzes NSF grants from 2020-2025 including terminated grants from the Trump administration
"""

import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NSF Grants Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ============ DATA LOADING ============
@st.cache_data
def load_data():
    """Load and preprocess the NSF grants data"""
    df = pd.read_csv('nsf_data_clean.csv', low_memory=False)
    
    # Convert dates
    df['awd_eff_date'] = pd.to_datetime(df['awd_eff_date'], errors='coerce')
    df['awd_exp_date'] = pd.to_datetime(df['awd_exp_date'], errors='coerce')
    
    # Clean up terminated column
    df['terminated'] = df['terminated'].fillna(False).astype(bool)
    
    return df


@st.cache_data
def load_political_data():
    """Load political alignment data"""
    return pd.read_csv('state_political_alignment.csv')


@st.cache_data
def compute_grants_by_state_year(df):
    """Compute grants statistics by state and year"""
    results = []
    
    for state in df['inst_state_code'].dropna().unique():
        state_df = df[df['inst_state_code'] == state]
        state_name = state_df['inst_state_name'].iloc[0] if len(state_df) > 0 else state
        
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            
            # Count active grants
            active_mask = (
                (state_df['awd_eff_date'] <= year_end) & 
                (state_df['awd_exp_date'] >= year_start)
            )
            num_active = active_mask.sum()
            
            # Total funding for active grants
            total_funding = state_df[active_mask]['awd_amount'].sum()
            
            # Terminated grants (only in 2025)
            if year == 2025:
                terminated_count = state_df['terminated'].sum()
                terminated_funding = state_df[state_df['terminated'] == True]['awd_amount'].sum()
            else:
                terminated_count = 0
                terminated_funding = 0
            
            termination_pct = (terminated_count / num_active * 100) if num_active > 0 else 0
            
            results.append({
                'state': state,
                'state_name': state_name,
                'year': year,
                'num_grants': num_active,
                'total_funding': total_funding,
                'terminated_grants': int(terminated_count),
                'terminated_funding': terminated_funding,
                'termination_pct': round(termination_pct, 2)
            })
    
    return pd.DataFrame(results)


@st.cache_data
def compute_grants_by_directorate_year(df):
    """Compute grants statistics by directorate and year"""
    results = []
    
    for directorate in df['dir_abbr'].dropna().unique():
        dir_df = df[df['dir_abbr'] == directorate]
        dir_long_name = dir_df['org_dir_long_name'].iloc[0] if len(dir_df) > 0 else directorate
        
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            
            # Count active grants
            active_mask = (
                (dir_df['awd_eff_date'] <= year_end) & 
                (dir_df['awd_exp_date'] >= year_start)
            )
            num_active = active_mask.sum()
            total_funding = dir_df[active_mask]['awd_amount'].sum()
            
            # Terminated grants (only in 2025)
            if year == 2025:
                terminated_count = dir_df['terminated'].sum()
                terminated_funding = dir_df[dir_df['terminated'] == True]['awd_amount'].sum()
            else:
                terminated_count = 0
                terminated_funding = 0
            
            termination_pct = (terminated_count / num_active * 100) if num_active > 0 else 0
            
            results.append({
                'directorate': directorate,
                'dir_long_name': dir_long_name,
                'year': year,
                'num_grants': num_active,
                'total_funding': total_funding,
                'terminated_grants': int(terminated_count),
                'terminated_funding': terminated_funding,
                'termination_pct': round(termination_pct, 2)
            })
    
    return pd.DataFrame(results)


# State FIPS mapping
STATE_FIPS = {
    'AL': 1, 'AK': 2, 'AZ': 4, 'AR': 5, 'CA': 6, 'CO': 8, 'CT': 9, 'DE': 10,
    'FL': 12, 'GA': 13, 'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19,
    'KS': 20, 'KY': 21, 'LA': 22, 'ME': 23, 'MD': 24, 'MA': 25, 'MI': 26,
    'MN': 27, 'MS': 28, 'MO': 29, 'MT': 30, 'NE': 31, 'NV': 32, 'NH': 33,
    'NJ': 34, 'NM': 35, 'NY': 36, 'NC': 37, 'ND': 38, 'OH': 39, 'OK': 40,
    'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45, 'SD': 46, 'TN': 47, 'TX': 48,
    'UT': 49, 'VT': 50, 'VA': 51, 'WA': 53, 'WV': 54, 'WI': 55, 'WY': 56,
    'DC': 11, 'PR': 72
}


# ============ VISUALIZATION FUNCTIONS ============

def create_choropleth_map(grants_by_state_year, selected_year, metric='num_grants'):
    """Create choropleth map for grants distribution by state"""
    us_states = alt.topo_feature(data.us_10m.url, 'states')
    
    # Filter data for selected year
    year_data = grants_by_state_year[grants_by_state_year['year'] == selected_year].copy()
    year_data['id'] = year_data['state'].map(STATE_FIPS)
    year_data = year_data.dropna(subset=['id'])
    year_data['id'] = year_data['id'].astype(int)
    
    # Determine color scheme and title based on metric
    if metric == 'num_grants':
        color_field = 'num_grants:Q'
        color_title = 'Number of Grants'
        scheme = 'blues'
    elif metric == 'terminated_grants':
        color_field = 'terminated_grants:Q'
        color_title = 'Terminated Grants'
        scheme = 'reds'
    else:  # termination_pct
        color_field = 'termination_pct:Q'
        color_title = 'Termination Rate (%)'
        scheme = 'oranges'
    
    choropleth = alt.Chart(us_states).mark_geoshape(
        stroke='white',
        strokeWidth=0.5
    ).encode(
        color=alt.Color(
            color_field,
            scale=alt.Scale(scheme=scheme),
            title=color_title
        ),
        tooltip=[
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('num_grants:Q', title='Active Grants', format=','),
            alt.Tooltip('total_funding:Q', title='Total Funding ($)', format=',.0f'),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants'),
            alt.Tooltip('termination_pct:Q', title='Termination %', format='.2f')
        ]
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(year_data, 'id', 
                             ['state', 'state_name', 'num_grants', 'total_funding', 
                              'terminated_grants', 'termination_pct'])
    ).project(
        type='albersUsa'
    ).properties(
        width=700,
        height=450,
        title=f'NSF Grants Distribution by State ({selected_year})'
    )
    
    return choropleth


def create_directorate_bar_chart(dir_data, selected_year, metric='num_grants'):
    """Create bar chart for grants by directorate"""
    if selected_year == 'All Years':
        # Aggregate across all years
        agg_data = dir_data.groupby(['directorate', 'dir_long_name']).agg({
            'num_grants': 'sum',
            'total_funding': 'sum',
            'terminated_grants': 'sum',
            'terminated_funding': 'sum'
        }).reset_index()
        title_year = 'All Years'
    else:
        agg_data = dir_data[dir_data['year'] == int(selected_year)].copy()
        title_year = selected_year
    
    y_field = f'{metric}:Q'
    y_title = 'Number of Grants' if metric == 'num_grants' else 'Terminated Grants'
    
    chart = alt.Chart(agg_data).mark_bar().encode(
        x=alt.X('directorate:N', sort='-y', title='Directorate', 
                axis=alt.Axis(labelAngle=-45)),
        y=alt.Y(y_field, title=y_title),
        color=alt.Color('directorate:N', legend=None, scale=alt.Scale(scheme='category20')),
        tooltip=[
            alt.Tooltip('dir_long_name:N', title='Directorate'),
            alt.Tooltip('num_grants:Q', title='Total Grants', format=','),
            alt.Tooltip('total_funding:Q', title='Total Funding ($)', format=',.0f'),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants', format=',')
        ]
    ).properties(
        width=700,
        height=400,
        title=f'Grants by Directorate ({title_year})'
    )
    
    return chart


def create_directorate_evolution_chart(dir_data):
    """Create line chart showing evolution of grants by directorate"""
    main_directorates = ['MPS', 'CSE', 'ENG', 'GEO', 'EDU', 'BIO', 'TIP', 'SBE']
    filtered_data = dir_data[dir_data['directorate'].isin(main_directorates)]
    
    # Create nearest point selection
    nearest = alt.selection_point(
        nearest=True, 
        on='mouseover',
        fields=['year'], 
        empty=False
    )
    
    # Base line chart
    line = alt.Chart(filtered_data).mark_line(
        interpolate='monotone',
        strokeWidth=2
    ).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('num_grants:Q', title='Number of Active Grants'),
        color=alt.Color('directorate:N', title='Directorate', 
                       scale=alt.Scale(scheme='category10'))
    )
    
    # Selectors across the chart
    selectors = alt.Chart(filtered_data).mark_point().encode(
        x='year:Q',
        opacity=alt.value(0)
    ).add_params(nearest)
    
    # Draw points on lines
    points = line.mark_point(size=80).encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    
    # Text labels
    text = line.mark_text(align='left', dx=10, dy=0, fontSize=11).encode(
        text=alt.condition(nearest, 'num_grants:Q', alt.value(' '))
    )
    
    # Vertical rule
    rules = alt.Chart(filtered_data).mark_rule(
        color='gray', strokeWidth=1
    ).encode(
        x='year:Q'
    ).transform_filter(nearest)
    
    chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=700,
        height=400,
        title='Evolution of Active Grants by Directorate (2020-2025)'
    )
    
    return chart


def create_termination_impact_chart(dir_data, metric='terminated_grants'):
    """Create bar chart showing termination impact by directorate"""
    # Get 2025 data
    data_2025 = dir_data[dir_data['year'] == 2025].copy()
    main_directorates = ['MPS', 'CSE', 'ENG', 'GEO', 'EDU', 'BIO', 'TIP', 'SBE']
    data_2025 = data_2025[data_2025['directorate'].isin(main_directorates)]
    
    y_field = f'{metric}:Q'
    if metric == 'terminated_grants':
        y_title = 'Terminated Grants (Count)'
        scheme = 'reds'
    else:
        y_title = 'Termination Rate (%)'
        scheme = 'oranges'
    
    chart = alt.Chart(data_2025).mark_bar().encode(
        x=alt.X('directorate:N', sort='-y', title='Directorate',
                axis=alt.Axis(labelAngle=-45)),
        y=alt.Y(y_field, title=y_title),
        color=alt.Color('directorate:N', legend=None, 
                       scale=alt.Scale(scheme='tableau10')),
        tooltip=[
            alt.Tooltip('dir_long_name:N', title='Directorate'),
            alt.Tooltip('num_grants:Q', title='Active Grants (2025)', format=','),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants', format=','),
            alt.Tooltip('termination_pct:Q', title='Termination Rate (%)', format='.2f')
        ]
    ).properties(
        width=700,
        height=400,
        title='Grant Termination Impact by Directorate (2025)'
    )
    
    return chart


def create_state_evolution_chart(df, selected_states):
    """Create line chart showing grant evolution for selected states"""
    if not selected_states:
        st.warning("Please select at least one state to view the evolution.")
        return None
    
    # Filter data for selected states
    state_data = df[df['state'].isin(selected_states)].copy()
    
    chart = alt.Chart(state_data).mark_line(point=True, strokeWidth=2).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('num_grants:Q', title='Number of Active Grants'),
        color=alt.Color('state_name:N', title='State'),
        tooltip=[
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('year:Q', title='Year'),
            alt.Tooltip('num_grants:Q', title='Active Grants', format=','),
            alt.Tooltip('total_funding:Q', title='Total Funding ($)', format=',.0f'),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants'),
            alt.Tooltip('termination_pct:Q', title='Termination %', format='.2f')
        ]
    ).properties(
        width=700,
        height=400,
        title=f'Grant Evolution for Selected States (2020-2025)'
    ).interactive()
    
    return chart


def create_political_alignment_chart(df, grants_by_state, political_df, selected_year):
    """Create scatter plot showing political alignment vs grants"""
    # Get data for selected year
    year_data = grants_by_state[grants_by_state['year'] == selected_year].copy()
    
    # Merge with political data
    year_data = year_data.merge(
        political_df, 
        left_on='state', 
        right_on='Abbreviation', 
        how='left'
    )
    year_data = year_data.dropna(subset=['2020_Election_Winner'])
    
    # Get political alignment based on year
    if selected_year < 2024:
        year_data['political_alignment'] = year_data['2020_Election_Winner']
    else:
        year_data['political_alignment'] = year_data['2024_Election_Winner']
    
    # Convert funding to millions
    year_data['funding_millions'] = year_data['total_funding'] / 1_000_000
    
    # Political party color scale
    party_colors = alt.Scale(domain=['Democrat', 'Republican'], range=['#2166ac', '#b2182b'])
    
    chart = alt.Chart(year_data).mark_circle(size=150, opacity=0.7).encode(
        x=alt.X('num_grants:Q', title='Number of Active Grants', scale=alt.Scale(zero=False)),
        y=alt.Y('funding_millions:Q', title='Total Funding (Millions $)', scale=alt.Scale(zero=False)),
        color=alt.Color('political_alignment:N', scale=party_colors, title='Political Alignment'),
        size=alt.Size('terminated_grants:Q', title='Terminated Grants', 
                     scale=alt.Scale(range=[50, 500])),
        tooltip=[
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('num_grants:Q', title='Active Grants', format=','),
            alt.Tooltip('funding_millions:Q', title='Total Funding ($M)', format=',.1f'),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants'),
            alt.Tooltip('termination_pct:Q', title='Termination %', format='.2f'),
            alt.Tooltip('political_alignment:N', title='Political Alignment')
        ]
    ).properties(
        width=700,
        height=500,
        title=f'NSF Grants by State: Political Alignment Analysis ({selected_year})'
    ).interactive()
    
    return chart


def create_termination_by_party_chart(df, grants_by_state, political_df):
    """Create bar chart comparing terminations by political party"""
    # Get 2025 data (when terminations happened)
    data_2025 = grants_by_state[grants_by_state['year'] == 2025].copy()
    
    # Merge with political data
    data_2025 = data_2025.merge(
        political_df,
        left_on='state',
        right_on='Abbreviation',
        how='left'
    )
    data_2025 = data_2025.dropna(subset=['2024_Election_Winner'])
    
    # Aggregate by party
    party_agg = data_2025.groupby('2024_Election_Winner').agg({
        'num_grants': 'sum',
        'terminated_grants': 'sum',
        'total_funding': 'sum',
        'terminated_funding': 'sum'
    }).reset_index()
    
    party_agg['termination_pct'] = (party_agg['terminated_grants'] / party_agg['num_grants'] * 100).round(2)
    party_agg.columns = ['party', 'total_grants', 'terminated_grants', 'total_funding', 
                         'terminated_funding', 'termination_pct']
    
    # Create grouped bar chart
    party_colors = alt.Scale(domain=['Democrat', 'Republican'], range=['#2166ac', '#b2182b'])
    
    base = alt.Chart(party_agg).encode(
        x=alt.X('party:N', title='Political Party (2024 Election)')
    )
    
    bars = base.mark_bar(width=50).encode(
        y=alt.Y('terminated_grants:Q', title='Terminated Grants'),
        color=alt.Color('party:N', scale=party_colors, legend=None),
        tooltip=[
            alt.Tooltip('party:N', title='Party'),
            alt.Tooltip('total_grants:Q', title='Total Active Grants', format=','),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants', format=','),
            alt.Tooltip('termination_pct:Q', title='Termination Rate (%)', format='.2f')
        ]
    )
    
    text = base.mark_text(dy=-10, fontSize=14, fontWeight='bold').encode(
        y=alt.Y('terminated_grants:Q'),
        text=alt.Text('terminated_grants:Q', format=',')
    )
    
    chart = (bars + text).properties(
        width=400,
        height=400,
        title='Grant Terminations by Political Party (2025)'
    )
    
    return chart, party_agg


# ============ MAIN APP ============

def main():
    # Header
    st.markdown('<p class="main-header">🔬 NSF Grants Explorer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyzing NSF grants from 2020-2025 and terminated grants</p>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
        political_df = load_political_data()
        grants_by_state = compute_grants_by_state_year(df)
        grants_by_dir = compute_grants_by_directorate_year(df)
    
    # Sidebar with key metrics
    st.sidebar.title("📊 Key Metrics")
    
    total_grants = len(df)
    total_terminated = df['terminated'].sum()
    total_funding = df['awd_amount'].sum()
    unique_states = df['inst_state_code'].nunique()
    
    st.sidebar.metric("Total Grants", f"{total_grants:,}")
    st.sidebar.metric("Terminated Grants", f"{int(total_terminated):,}")
    st.sidebar.metric("Total Funding", f"${total_funding/1e9:.2f}B")
    st.sidebar.metric("States/Territories", unique_states)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This application analyzes NSF grants from 2020-2025, "
        "including grants terminated by the Trump administration in 2025."
    )
    
    # Main content with tabs
    tabs = st.tabs([
        "🗺️ Q1: Geographic Distribution",
        "📊 Q2: Directorates",
        "⚠️ Q3: Termination Impact",
        "📈 Q4: Evolution Over Time",
        "🔍 Q5: State Analysis",
        "🏛️ Q6: Political Analysis"
    ])
    
    # ============ TAB 1: Geographic Distribution ============
    with tabs[0]:
        st.header("Q1: How are grants distributed by states every year?")
        st.markdown("""
        This visualization shows the geographic distribution of NSF grants across U.S. states.
        Use the controls below to explore different years and metrics.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            year_q1 = st.slider("Select Year", 2020, 2025, 2025, key='year_q1')
        with col2:
            metric_q1 = st.selectbox(
                "Select Metric",
                options=['num_grants', 'terminated_grants', 'termination_pct'],
                format_func=lambda x: {
                    'num_grants': 'Number of Active Grants',
                    'terminated_grants': 'Terminated Grants',
                    'termination_pct': 'Termination Rate (%)'
                }[x],
                key='metric_q1'
            )
        
        map_chart = create_choropleth_map(grants_by_state, year_q1, metric_q1)
        st.altair_chart(map_chart, use_container_width=True)
        
        # Show top states table
        st.subheader(f"Top 10 States by {metric_q1.replace('_', ' ').title()} ({year_q1})")
        year_data = grants_by_state[grants_by_state['year'] == year_q1].sort_values(
            metric_q1, ascending=False
        ).head(10)
        
        display_cols = ['state_name', 'num_grants', 'total_funding', 'terminated_grants', 'termination_pct']
        st.dataframe(
            year_data[display_cols].rename(columns={
                'state_name': 'State',
                'num_grants': 'Active Grants',
                'total_funding': 'Total Funding ($)',
                'terminated_grants': 'Terminated',
                'termination_pct': 'Term. Rate (%)'
            }),
            hide_index=True,
            use_container_width=True
        )
    
    # ============ TAB 2: Directorates ============
    with tabs[1]:
        st.header("Q2: How are grants distributed per directorates?")
        st.markdown("""
        Explore how NSF grants are distributed across different research directorates.
        Select a specific year or view aggregated data for all years.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            year_q2 = st.selectbox(
                "Select Year",
                options=['All Years', '2020', '2021', '2022', '2023', '2024', '2025'],
                key='year_q2'
            )
        with col2:
            metric_q2 = st.selectbox(
                "Select Metric",
                options=['num_grants', 'terminated_grants'],
                format_func=lambda x: {
                    'num_grants': 'Total Grants',
                    'terminated_grants': 'Terminated Grants'
                }[x],
                key='metric_q2'
            )
        
        bar_chart = create_directorate_bar_chart(grants_by_dir, year_q2, metric_q2)
        st.altair_chart(bar_chart, use_container_width=True)
        
        st.subheader("Evolution of Active Grants by Directorate")
        evolution_chart = create_directorate_evolution_chart(grants_by_dir)
        st.altair_chart(evolution_chart, use_container_width=True)
    
    # ============ TAB 3: Termination Impact ============
    with tabs[2]:
        st.header("Q3: Are cancelled grants especially hitting a certain directorate?")
        st.markdown("""
        Analyze which directorates were most affected by grant terminations.
        Toggle between absolute numbers and relative rates to understand the impact.
        """)
        
        metric_q3 = st.radio(
            "Select Metric",
            options=['terminated_grants', 'termination_pct'],
            format_func=lambda x: {
                'terminated_grants': 'Terminated Grants (Count)',
                'termination_pct': 'Termination Rate (%)'
            }[x],
            horizontal=True,
            key='metric_q3'
        )
        
        impact_chart = create_termination_impact_chart(grants_by_dir, metric_q3)
        st.altair_chart(impact_chart, use_container_width=True)
        
        # Summary statistics
        data_2025 = grants_by_dir[grants_by_dir['year'] == 2025]
        main_dirs = ['MPS', 'CSE', 'ENG', 'GEO', 'EDU', 'BIO', 'TIP', 'SBE']
        summary = data_2025[data_2025['directorate'].isin(main_dirs)][
            ['directorate', 'dir_long_name', 'num_grants', 'terminated_grants', 'termination_pct']
        ].sort_values('terminated_grants', ascending=False)
        
        st.subheader("Termination Summary by Directorate (2025)")
        st.dataframe(
            summary.rename(columns={
                'directorate': 'Code',
                'dir_long_name': 'Directorate',
                'num_grants': 'Active Grants',
                'terminated_grants': 'Terminated',
                'termination_pct': 'Rate (%)'
            }),
            hide_index=True,
            use_container_width=True
        )
    
    # ============ TAB 4: Evolution Over Time ============
    with tabs[3]:
        st.header("Q4: How have total grants evolved over the years?")
        st.markdown("""
        Track how the number of active grants has changed over time.
        Select multiple states to compare their trajectories.
        """)
        
        # State selection
        all_states = grants_by_state['state'].unique().tolist()
        state_names = grants_by_state[['state', 'state_name']].drop_duplicates()
        state_dict = dict(zip(state_names['state'], state_names['state_name']))
        
        selected_states_q4 = st.multiselect(
            "Select States to Compare (max 8)",
            options=all_states,
            format_func=lambda x: state_dict.get(x, x),
            default=['CA', 'TX', 'NY'],
            max_selections=8,
            key='states_q4'
        )
        
        if selected_states_q4:
            evolution_chart = create_state_evolution_chart(grants_by_state, selected_states_q4)
            if evolution_chart:
                st.altair_chart(evolution_chart, use_container_width=True)
        else:
            # Show overall trend
            total_by_year = grants_by_state.groupby('year').agg({
                'num_grants': 'sum',
                'total_funding': 'sum',
                'terminated_grants': 'sum'
            }).reset_index()
            
            chart = alt.Chart(total_by_year).mark_line(
                point=True, strokeWidth=3, color='#1f77b4'
            ).encode(
                x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
                y=alt.Y('num_grants:Q', title='Total Active Grants'),
                tooltip=[
                    alt.Tooltip('year:Q', title='Year'),
                    alt.Tooltip('num_grants:Q', title='Active Grants', format=','),
                    alt.Tooltip('total_funding:Q', title='Total Funding ($)', format=',.0f'),
                    alt.Tooltip('terminated_grants:Q', title='Terminated Grants')
                ]
            ).properties(
                width=700,
                height=400,
                title='Total Active NSF Grants Over Time (All States)'
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
    
    # ============ TAB 5: State Analysis ============
    with tabs[4]:
        st.header("Q5: For a selected state, how have grants evolved?")
        st.markdown("""
        Deep dive into a specific state's grant history and termination status.
        """)
        
        state_names_list = grants_by_state[['state', 'state_name']].drop_duplicates()
        state_dict = dict(zip(state_names_list['state_name'], state_names_list['state']))
        
        selected_state_name = st.selectbox(
            "Select State",
            options=sorted(state_names_list['state_name'].dropna().unique()),
            key='state_q5'
        )
        
        selected_state = state_dict.get(selected_state_name)
        
        if selected_state:
            state_data = grants_by_state[grants_by_state['state'] == selected_state]
            
            # Key metrics for selected state
            col1, col2, col3, col4 = st.columns(4)
            latest = state_data[state_data['year'] == 2025].iloc[0]
            
            col1.metric("Active Grants (2025)", f"{latest['num_grants']:,}")
            col2.metric("Total Funding (2025)", f"${latest['total_funding']/1e6:.1f}M")
            col3.metric("Terminated Grants", f"{int(latest['terminated_grants']):,}")
            col4.metric("Termination Rate", f"{latest['termination_pct']:.2f}%")
            
            # Evolution chart
            chart = alt.Chart(state_data).mark_area(
                line=True,
                color='#1f77b4',
                opacity=0.3
            ).encode(
                x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
                y=alt.Y('num_grants:Q', title='Active Grants'),
                tooltip=[
                    alt.Tooltip('year:Q', title='Year'),
                    alt.Tooltip('num_grants:Q', title='Active Grants', format=','),
                    alt.Tooltip('total_funding:Q', title='Total Funding ($)', format=',.0f'),
                    alt.Tooltip('terminated_grants:Q', title='Terminated'),
                    alt.Tooltip('termination_pct:Q', title='Term. Rate (%)', format='.2f')
                ]
            ).properties(
                width=700,
                height=350,
                title=f'Grant Evolution - {selected_state_name}'
            )
            
            points = alt.Chart(state_data).mark_point(
                size=100, color='#1f77b4', filled=True
            ).encode(
                x='year:Q',
                y='num_grants:Q'
            )
            
            st.altair_chart(chart + points, use_container_width=True)
            
            # Detailed table
            st.subheader("Year-by-Year Data")
            st.dataframe(
                state_data[['year', 'num_grants', 'total_funding', 'terminated_grants', 'termination_pct']].rename(columns={
                    'year': 'Year',
                    'num_grants': 'Active Grants',
                    'total_funding': 'Total Funding ($)',
                    'terminated_grants': 'Terminated',
                    'termination_pct': 'Term. Rate (%)'
                }),
                hide_index=True,
                use_container_width=True
            )
    
    # ============ TAB 6: Political Analysis ============
    with tabs[5]:
        st.header("Q6: Political Alignment Analysis")
        st.markdown("""
        Explore the relationship between state political alignment and NSF grant funding/terminations.
        This analysis uses presidential election results (2020 and 2024) to classify states.
        """)
        
        year_q6 = st.slider("Select Year", 2020, 2025, 2025, key='year_q6')
        
        political_chart = create_political_alignment_chart(df, grants_by_state, political_df, year_q6)
        st.altair_chart(political_chart, use_container_width=True)
        
        st.subheader("Terminations by Political Party")
        party_chart, party_agg = create_termination_by_party_chart(df, grants_by_state, political_df)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.altair_chart(party_chart, use_container_width=True)
        with col2:
            st.markdown("### Summary Statistics")
            for _, row in party_agg.iterrows():
                st.markdown(f"**{row['party']}**")
                st.markdown(f"- Total Grants: {row['total_grants']:,}")
                st.markdown(f"- Terminated: {row['terminated_grants']:,}")
                st.markdown(f"- Rate: {row['termination_pct']:.2f}%")
                st.markdown("---")
        
        st.info("""
        **Data Sources:**
        - 2020 Election Results: The National Archives (Electoral College Results 2020)
        - 2024 Election Results: Wikipedia - 2024 United States presidential election
        - Governor Affiliations: National Governors Association
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>NSF Grants Explorer | Data from 2020-2025</p>
            <p>By Nicolás Villoria and Oriol Fontanals</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
