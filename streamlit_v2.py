"""
NSF Grants Explorer - Streamlit Application v2
Interactive 2x3 Grid Layout with Click-based State Selection
"""

import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data as vega_data

# Page configuration
st.set_page_config(
    page_title="NSF Grants Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enable default data transformer and disable max rows
alt.data_transformers.enable('default')
alt.data_transformers.disable_max_rows()

# Register and enable white theme for Altair (updated API for altair>=5.5.0)
@alt.theme.register('white_theme', enable=True)
def white_theme():
    return alt.theme.ThemeConfig({
        'background': 'white',
        'view': {'fill': 'white', 'stroke': 'transparent'},
        'title': {'color': 'black'},
        'axis': {
            'labelColor': 'black',
            'titleColor': 'black',
            'tickColor': '#888',
            'domainColor': '#888',
            'gridColor': '#eee'
        },
        'legend': {
            'labelColor': 'black',
            'titleColor': 'black'
        },
        'header': {
            'labelColor': 'black',
            'titleColor': 'black'
        },
        'text': {'color': 'black'}
    })

# Custom CSS for light theme
st.markdown("""
<style>
    /* Main app background */
    .stApp {background-color: #ffffff !important;}
    .stAppHeader {background-color: #ffffff !important;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 100%; background-color: #ffffff;}
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stMarkdown * {color: #1a1a1a !important;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {background-color: #f8f9fa !important;}
    [data-testid="stSidebar"] * {color: #1a1a1a !important;}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {color: #1a1a1a !important;}
    
    /* Compact spacing */
    div[data-testid="stVerticalBlock"] > div {padding: 0.2rem 0;}
    .element-container {margin-bottom: 0.3rem !important;}
    
    /* Button styling */
    .stButton button {
        background-color: #f0f0f0 !important;
        color: #1a1a1a !important;
        border: 1px solid #ccc !important;
        font-size: 0.85rem !important;
        padding: 0.4rem 1rem !important;
    }
    .stButton button:hover {background-color: #e0e0e0 !important;}
    
    /* Select box styling */
    [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label {color: #1a1a1a !important;}
    
    /* Chart container */
    .stVegaLiteChart {background-color: white !important;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTS
# ============================================================================

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

STATE_ABBR_TO_NAME = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
    'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
    'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon',
    'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia',
    'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'PR': 'Puerto Rico'
}

STATE_NAME_TO_ABBR = {v: k for k, v in STATE_ABBR_TO_NAME.items()}

STATE_LOOKUP = pd.DataFrame([
    {"id": 1, "state": "AL", "longitude": -86.9023, "latitude": 32.3182},
    {"id": 2, "state": "AK", "longitude": -153.3691, "latitude": 63.5888},
    {"id": 4, "state": "AZ", "longitude": -111.0937, "latitude": 34.0489},
    {"id": 5, "state": "AR", "longitude": -92.3731, "latitude": 35.2010},
    {"id": 6, "state": "CA", "longitude": -119.4179, "latitude": 36.7783},
    {"id": 8, "state": "CO", "longitude": -105.7821, "latitude": 39.5501},
    {"id": 9, "state": "CT", "longitude": -72.7554, "latitude": 41.6032},
    {"id": 10, "state": "DE", "longitude": -75.5277, "latitude": 38.9108},
    {"id": 11, "state": "DC", "longitude": -77.0369, "latitude": 38.9072},
    {"id": 12, "state": "FL", "longitude": -81.5158, "latitude": 27.6648},
    {"id": 13, "state": "GA", "longitude": -82.9071, "latitude": 32.1656},
    {"id": 15, "state": "HI", "longitude": -157.8583, "latitude": 21.3069},
    {"id": 16, "state": "ID", "longitude": -114.7420, "latitude": 44.0682},
    {"id": 17, "state": "IL", "longitude": -89.3985, "latitude": 40.6331},
    {"id": 18, "state": "IN", "longitude": -86.1349, "latitude": 40.2672},
    {"id": 19, "state": "IA", "longitude": -93.0977, "latitude": 41.8780},
    {"id": 20, "state": "KS", "longitude": -96.7265, "latitude": 38.5266},
    {"id": 21, "state": "KY", "longitude": -84.6701, "latitude": 37.6681},
    {"id": 22, "state": "LA", "longitude": -91.8749, "latitude": 31.1695},
    {"id": 23, "state": "ME", "longitude": -69.3819, "latitude": 44.6939},
    {"id": 24, "state": "MD", "longitude": -76.6413, "latitude": 39.0639},
    {"id": 25, "state": "MA", "longitude": -71.5301, "latitude": 42.2302},
    {"id": 26, "state": "MI", "longitude": -84.5467, "latitude": 43.3266},
    {"id": 27, "state": "MN", "longitude": -93.9196, "latitude": 45.6945},
    {"id": 28, "state": "MS", "longitude": -89.6787, "latitude": 32.7416},
    {"id": 29, "state": "MO", "longitude": -92.2896, "latitude": 38.4561},
    {"id": 30, "state": "MT", "longitude": -110.4544, "latitude": 46.9219},
    {"id": 31, "state": "NE", "longitude": -98.2680, "latitude": 41.1254},
    {"id": 32, "state": "NV", "longitude": -117.0554, "latitude": 38.3135},
    {"id": 33, "state": "NH", "longitude": -71.5639, "latitude": 43.4525},
    {"id": 34, "state": "NJ", "longitude": -74.5210, "latitude": 40.2989},
    {"id": 35, "state": "NM", "longitude": -106.2371, "latitude": 34.8405},
    {"id": 36, "state": "NY", "longitude": -74.9481, "latitude": 42.1657},
    {"id": 37, "state": "NC", "longitude": -79.8064, "latitude": 35.6301},
    {"id": 38, "state": "ND", "longitude": -99.7840, "latitude": 47.5289},
    {"id": 39, "state": "OH", "longitude": -82.7644, "latitude": 40.3888},
    {"id": 40, "state": "OK", "longitude": -97.0929, "latitude": 35.5653},
    {"id": 41, "state": "OR", "longitude": -122.0709, "latitude": 44.5720},
    {"id": 42, "state": "PA", "longitude": -77.2098, "latitude": 40.5908},
    {"id": 72, "state": "PR", "longitude": -66.5901, "latitude": 18.2208},
    {"id": 44, "state": "RI", "longitude": -71.5114, "latitude": 41.6809},
    {"id": 45, "state": "SC", "longitude": -80.9066, "latitude": 33.8569},
    {"id": 46, "state": "SD", "longitude": -99.4388, "latitude": 44.2998},
    {"id": 47, "state": "TN", "longitude": -86.6923, "latitude": 35.7478},
    {"id": 48, "state": "TX", "longitude": -97.5631, "latitude": 31.0545},
    {"id": 49, "state": "UT", "longitude": -111.8910, "latitude": 40.1500},
    {"id": 50, "state": "VT", "longitude": -72.7107, "latitude": 44.0459},
    {"id": 51, "state": "VA", "longitude": -78.1690, "latitude": 37.7693},
    {"id": 53, "state": "WA", "longitude": -121.4906, "latitude": 47.4009},
    {"id": 54, "state": "WV", "longitude": -80.9545, "latitude": 38.4912},
    {"id": 55, "state": "WI", "longitude": -89.6165, "latitude": 44.2685},
    {"id": 56, "state": "WY", "longitude": -107.3025, "latitude": 42.7559}
])

# East coast states that need label offsets
EAST_COAST_STATES = ['NH', 'MA', 'RI', 'NJ', 'DE', 'DC']
STATE_LOOKUP['label_longitude'] = STATE_LOOKUP.apply(
    lambda row: row['longitude'] + 3 if row['state'] in EAST_COAST_STATES else row['longitude'], axis=1
)
STATE_LOOKUP['label_latitude'] = STATE_LOOKUP.apply(
    lambda row: row['latitude'] - 1.5 if row['state'] in EAST_COAST_STATES else row['latitude'], axis=1
)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load and preprocess NSF grants data."""
    df = pd.read_csv('nsf_data_clean.csv', low_memory=False)
    df['awd_eff_date'] = pd.to_datetime(df['awd_eff_date'], errors='coerce')
    df['awd_exp_date'] = pd.to_datetime(df['awd_exp_date'], errors='coerce')
    
    # Cap terminated grants at end of 2025
    mask_terminated = (df['terminated'] == True)
    mask_exceeds = df['awd_exp_date'] > pd.Timestamp('2025-12-31')
    df.loc[mask_terminated & mask_exceeds, 'awd_exp_date'] = pd.Timestamp('2025-12-31')
    df = df.dropna(subset=['awd_eff_date', 'awd_exp_date', 'inst_state_name'])
    
    return df


@st.cache_data
def load_political_data():
    """Load political alignment data."""
    return pd.read_csv('state_political_alignment.csv')


@st.cache_data
def prepare_grants_by_state_year(df):
    """Prepare grants by state and year for choropleth."""
    results = []
    for state in df['inst_state_code'].unique():
        state_df = df[df['inst_state_code'] == state]
        state_name = state_df['inst_state_name'].iloc[0] if len(state_df) > 0 else state
        
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            active_mask = (state_df['awd_eff_date'] <= year_end) & (state_df['awd_exp_date'] >= year_start)
            num_active = active_mask.sum()
            terminated_count = state_df[active_mask]['terminated'].sum() if year == 2025 else 0
            terminated_pct = (terminated_count / num_active * 100) if num_active > 0 else 0
            
            results.append({
                'state': state,
                'state_name': state_name,
                'year': year,
                'num_grants': num_active,
                'terminated_grants': int(terminated_count),
                'terminated_pct': round(terminated_pct, 2)
            })
    
    grants_df = pd.DataFrame(results)
    grants_df['id'] = grants_df['state'].map(STATE_FIPS)
    grants_df = grants_df.dropna(subset=['id'])
    grants_df['id'] = grants_df['id'].astype(int)
    
    # Create wide format for multi-year lookup
    grants_wide = grants_df.pivot(
        index=['state', 'state_name', 'id'], 
        columns='year', 
        values=['num_grants', 'terminated_grants', 'terminated_pct']
    ).reset_index()
    grants_wide.columns = [f"{col[0]}_{col[1]}" if col[1] != '' else col[0] for col in grants_wide.columns]
    grants_wide = grants_wide.fillna(0)
    
    return grants_df, grants_wide


@st.cache_data
def prepare_directorate_data(df):
    """Prepare data for directorate visualizations."""
    main_directorates = ['MPS', 'CSE', 'ENG', 'GEO', 'EDU', 'BIO', 'TIP', 'SBE', 'O/D']
    results = []
    
    for directorate in df['dir_abbr'].unique():
        if directorate not in main_directorates:
            continue
        dir_df = df[df['dir_abbr'] == directorate]
        
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            active_mask = (dir_df['awd_eff_date'] <= year_end) & (dir_df['awd_exp_date'] >= year_start)
            num_active = active_mask.sum()
            terminated_count = dir_df[active_mask]['terminated'].sum() if year == 2025 else 0
            termination_pct = (terminated_count / num_active * 100) if num_active > 0 else 0
            
            results.append({
                'directorate': directorate,
                'year': year,
                'num_grants': num_active,
                'terminated_grants': int(terminated_count),
                'termination_pct': round(termination_pct, 2)
            })
    
    return pd.DataFrame(results)


@st.cache_data
def prepare_lifecycle_data(df):
    """Prepare MONTHLY active grants lifecycle data by state (optimized)."""
    # Use monthly sampling for much faster performance
    date_range = pd.date_range(start='2020-01-01', end='2025-12-31', freq='MS')  # Month start
    
    results = []
    state_info = df.groupby('inst_state_code')['inst_state_name'].first().to_dict()
    
    for state_code, state_name in state_info.items():
        state_df = df[df['inst_state_code'] == state_code]
        
        for date in date_range:
            # Count active grants on this date
            active_count = ((state_df['awd_eff_date'] <= date) & 
                           (state_df['awd_exp_date'] >= date)).sum()
            
            results.append({
                'Date': date,
                'State': state_name,
                'state_code': state_code,
                'Active Grants': active_count
            })
    
    return pd.DataFrame(results)


@st.cache_data
def prepare_political_data(df, political_df):
    """Prepare data for political alignment visualization."""
    state_year_stats = []
    
    for state_abbr in df['inst_state_code'].unique():
        state_df = df[df['inst_state_code'] == state_abbr]
        state_name = state_df['inst_state_name'].iloc[0] if len(state_df) > 0 else STATE_ABBR_TO_NAME.get(state_abbr, state_abbr)
        
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            active_mask = (state_df['awd_eff_date'] <= year_end) & (state_df['awd_exp_date'] >= year_start)
            active_grants = state_df[active_mask]
            num_active = len(active_grants)
            total_funding = active_grants['awd_amount'].sum() / 1_000_000
            
            if year == 2025:
                num_terminated = active_grants['terminated'].sum()
                terminated_funding = active_grants[active_grants['terminated'] == True]['awd_amount'].sum() / 1_000_000
            else:
                num_terminated = 0
                terminated_funding = 0
            
            state_year_stats.append({
                'Abbreviation': state_abbr,
                'State': state_name,
                'year': year,
                'active_grants': num_active,
                'total_funding_millions': round(total_funding, 2),
                'terminated_grants': int(num_terminated),
                'terminated_funding_millions': round(terminated_funding, 2),
                'termination_pct': round((num_terminated / num_active * 100) if num_active > 0 else 0, 2)
            })
    
    state_year_df = pd.DataFrame(state_year_stats)
    source_df = state_year_df.merge(political_df, on='Abbreviation', how='left')
    source_df = source_df.dropna(subset=['2020_Election_Winner'])
    
    def get_political_alignment(row):
        return row['2020_Election_Winner'] if row['year'] < 2024 else row['2024_Election_Winner']
    
    source_df['political_alignment'] = source_df.apply(get_political_alignment, axis=1)
    
    return source_df


# ============================================================================
# CHART CREATION FUNCTIONS
# ============================================================================

def create_linked_map_and_state_charts(grants_wide, lifecycle_df, df, selected_year):
    """Create choropleth map linked with lifecycle and termination charts via shared selection."""
    us_states = alt.topo_feature(vega_data.us_10m.url, 'states')
    
    # Get min/max for color scale
    num_cols = [c for c in grants_wide.columns if c.startswith('num_grants_')]
    min_grants = min(grants_wide[num_cols].min())
    max_grants = max(grants_wide[num_cols].max())
    
    # Create shared state selection
    state_selection = alt.selection_point(
        name='state_select',
        fields=['state'],
        on='click',
        toggle='event.shiftKey',
        clear='dblclick'
    )
    
    # =========== CHOROPLETH MAP ===========
    choropleth = alt.Chart(us_states).mark_geoshape(
        stroke='white',
        strokeWidth=0.5
    ).encode(
        color=alt.Color(
            'current_num_grants:Q',
            scale=alt.Scale(scheme='blues', domain=[min_grants, max_grants]),
            title='Grants',
            legend=alt.Legend(orient='bottom', direction='horizontal', gradientLength=150)
        ),
        strokeWidth=alt.condition(state_selection, alt.value(3), alt.value(0.5)),
        stroke=alt.condition(state_selection, alt.value('#ff6600'), alt.value('white')),
        tooltip=[
            alt.Tooltip('state:N', title='State'),
            alt.Tooltip('state_name:N', title='Name'),
            alt.Tooltip('current_num_grants:Q', title='Grants', format=','),
            alt.Tooltip('current_terminated:Q', title='Terminated', format=','),
            alt.Tooltip('current_pct:Q', title='Term %', format='.1f')
        ]
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(grants_wide, 'id', list(grants_wide.columns))
    ).transform_calculate(
        current_num_grants=f"datum['num_grants_{selected_year}']",
        current_terminated=f"datum['terminated_grants_{selected_year}']",
        current_pct=f"datum['terminated_pct_{selected_year}']"
    ).project(type='albersUsa').add_params(state_selection)
    
    # Leader lines for east coast
    leader_lines = alt.Chart(STATE_LOOKUP[STATE_LOOKUP['state'].isin(EAST_COAST_STATES)]).mark_rule(
        strokeWidth=1, color='gray', opacity=0.5, strokeDash=[2, 2]
    ).encode(
        longitude='longitude:Q', latitude='latitude:Q',
        longitude2='label_longitude:Q', latitude2='label_latitude:Q'
    ).project(type='albersUsa')
    
    # State labels
    state_labels = alt.Chart(STATE_LOOKUP).mark_text(
        fontSize=7, fontWeight='bold', color='#333', opacity=0.8
    ).encode(
        longitude='label_longitude:Q', latitude='label_latitude:Q', text='state:N'
    ).project(type='albersUsa')
    
    # Puerto Rico circle
    pr_lookup = STATE_LOOKUP[STATE_LOOKUP['state'] == 'PR'].copy()
    pr_circle = alt.Chart(pr_lookup).mark_circle(size=300, stroke='white', strokeWidth=1).encode(
        longitude='longitude:Q', latitude='latitude:Q',
        color=alt.Color('current_num_grants:Q', scale=alt.Scale(scheme='blues', domain=[min_grants, max_grants]), legend=None),
        strokeWidth=alt.condition(state_selection, alt.value(3), alt.value(1)),
        stroke=alt.condition(state_selection, alt.value('#ff6600'), alt.value('white')),
        tooltip=[alt.Tooltip('state:N', title='State'), alt.Tooltip('current_num_grants:Q', title='Grants', format=',')]
    ).transform_lookup(
        lookup='id', from_=alt.LookupData(grants_wide, 'id', list(grants_wide.columns))
    ).transform_calculate(
        current_num_grants=f"datum['num_grants_{selected_year}']"
    ).project(type='albersUsa')
    
    map_chart = (choropleth + leader_lines + state_labels + pr_circle).properties(
        width=420, height=280, title=alt.TitleParams(text=f'Grants Distribution ({selected_year})', anchor='start')
    )
    
    # =========== LIFECYCLE LINE CHART (filtered by map selection) ===========
    # Sample lifecycle data for performance - keep only every state's data
    lifecycle_sampled = lifecycle_df.copy()
    
    lifecycle_line = alt.Chart(lifecycle_sampled).mark_line(strokeWidth=1.5).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m')),
        y=alt.Y('Active Grants:Q', title='Active Grants'),
        color=alt.Color('State:N', legend=None),
        opacity=alt.condition(state_selection, alt.value(1), alt.value(0.08)),
        strokeWidth=alt.condition(state_selection, alt.value(2.5), alt.value(0.3)),
        tooltip=['State:N', alt.Tooltip('Date:T', format='%b %Y'), 'Active Grants:Q']
    ).transform_lookup(
        lookup='state_code',
        from_=alt.LookupData(STATE_LOOKUP, 'state', ['state'])
    ).properties(
        width=280, height=200, title=alt.TitleParams(text='Grants Timeline (Monthly)', anchor='start')
    )
    
    # =========== TERMINATION BAR CHART (filtered by map selection) ===========
    # Prepare termination data - top 15 states only for performance
    term_data = df[df['terminated'] == True].groupby(['inst_state_code', 'inst_state_name']).size().reset_index(name='terminated_grants')
    term_data.columns = ['state', 'state_name', 'terminated_grants']
    term_data = term_data.nlargest(15, 'terminated_grants')
    
    termination_bar = alt.Chart(term_data).mark_bar(color='#d62728').encode(
        x=alt.X('terminated_grants:Q', title='Terminated Grants'),
        y=alt.Y('state_name:N', sort='-x', title=''),
        opacity=alt.condition(state_selection, alt.value(1), alt.value(0.2)),
        tooltip=['state_name:N', 'terminated_grants:Q']
    ).transform_lookup(
        lookup='state',
        from_=alt.LookupData(STATE_LOOKUP, 'state', ['state'])
    ).properties(
        width=280, height=200, title=alt.TitleParams(text='Top 15 Terminated by State', anchor='start')
    )
    
    # Combine into linked dashboard (map on left, state charts stacked on right)
    right_charts = lifecycle_line & termination_bar
    linked_dashboard = (map_chart | right_charts).add_params(state_selection)
    
    return linked_dashboard


def create_directorate_evolution_chart(directorate_data):
    """Create line chart showing evolution of grants by directorate."""
    filtered_data = directorate_data.copy()
    filtered_data['year'] = filtered_data['year'].astype(int)
    
    # Highlight selection on hover
    highlight = alt.selection_point(on='pointerover', fields=['directorate'], nearest=True)
    
    base = alt.Chart(filtered_data).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d', labelAngle=0, tickCount=6)),
        y=alt.Y('num_grants:Q', title='Active Grants'),
        color=alt.Color('directorate:N', title='Directorate', 
                       scale=alt.Scale(scheme='tableau10'),
                       legend=alt.Legend(orient='right', columns=1, labelFontSize=9)),
        tooltip=[
            alt.Tooltip('directorate:N', title='Directorate'),
            alt.Tooltip('year:Q', title='Year'),
            alt.Tooltip('num_grants:Q', title='Grants', format=','),
            alt.Tooltip('terminated_grants:Q', title='Terminated', format=',')
        ]
    )
    
    lines = base.mark_line(interpolate='monotone', strokeWidth=2).encode(
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.4))
    )
    
    points = base.mark_circle(size=40).encode(
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.4))
    )
    
    chart = (lines + points).add_params(highlight).properties(width=280, height=220).interactive()
    
    return chart


def create_termination_impact_chart(directorate_data, metric='terminated_grants'):
    """Create bar chart showing termination impact by directorate (2025 only)."""
    data_2025 = directorate_data[directorate_data['year'] == 2025].copy()
    data_2025 = data_2025.sort_values(metric, ascending=False)
    
    y_title = 'Terminated Grants' if metric == 'terminated_grants' else 'Termination Rate (%)'
    
    chart = alt.Chart(data_2025).mark_bar().encode(
        x=alt.X('directorate:N', sort='-y', title='Directorate', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y(f'{metric}:Q', title=y_title),
        color=alt.Color('directorate:N', legend=None, scale=alt.Scale(scheme='reds')),
        tooltip=[
            alt.Tooltip('directorate:N', title='Directorate'),
            alt.Tooltip('num_grants:Q', title='Active 2025', format=','),
            alt.Tooltip('terminated_grants:Q', title='Terminated', format=','),
            alt.Tooltip('termination_pct:Q', title='Rate %', format='.2f')
        ]
    ).properties(width=280, height=220)
    
    return chart


def create_political_scatter(source_df, selected_year):
    """Create scatter plot for political alignment analysis (simplified for performance)."""
    year_data = source_df[source_df['year'] == selected_year].copy()
    party_colors = alt.Scale(domain=['Democrat', 'Republican'], range=['#2166ac', '#b2182b'])
    
    # Simple hover for tooltip
    hover = alt.selection_point(on='pointerover', nearest=True, empty=False)
    
    # Main scatter points
    points = alt.Chart(year_data).mark_circle(size=80).encode(
        x=alt.X('active_grants:Q', scale=alt.Scale(zero=False), title='Active Grants'),
        y=alt.Y('total_funding_millions:Q', scale=alt.Scale(zero=False), title='Funding ($M)'),
        color=alt.Color('political_alignment:N', scale=party_colors, title='Party',
                       legend=alt.Legend(orient='top')),
        opacity=alt.condition(hover, alt.value(1), alt.value(0.6)),
        size=alt.condition(hover, alt.value(150), alt.value(80)),
        tooltip=[
            alt.Tooltip('State:N'),
            alt.Tooltip('active_grants:Q', title='Grants', format=','),
            alt.Tooltip('total_funding_millions:Q', title='Funding $M', format=',.1f'),
            alt.Tooltip('terminated_grants:Q', title='Terminated'),
            alt.Tooltip('political_alignment:N', title='Party')
        ]
    ).add_params(hover).properties(
        width=400, height=280
    ).interactive()
    
    return points


# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Initialize session state for selected states
if 'selected_states' not in st.session_state:
    st.session_state.selected_states = []

# Load all data
df = load_data()
political_df = load_political_data()
grants_by_state, grants_wide = prepare_grants_by_state_year(df)
directorate_data = prepare_directorate_data(df)
lifecycle_df = prepare_lifecycle_data(df)
political_source = prepare_political_data(df, political_df)

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("## 🔬 NSF Grants Explorer")
    st.markdown("---")
    
    # Year Selection
    st.markdown("### 📅 Year Selection")
    selected_year = st.selectbox(
        "Select Year",
        options=[2020, 2021, 2022, 2023, 2024, 2025],
        index=5,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # State Selection
    st.markdown("### 🗺️ State Selection")
    available_states = sorted(df['inst_state_code'].unique().tolist())
    selected_states = st.multiselect(
        "Select States (max 8)",
        options=available_states,
        default=st.session_state.selected_states,
        max_selections=8,
        format_func=lambda x: f"{x} - {STATE_ABBR_TO_NAME.get(x, x)}",
        label_visibility="collapsed"
    )
    st.session_state.selected_states = selected_states
    
    if st.button("🔄 Clear Selection", use_container_width=True):
        st.session_state.selected_states = []
        st.rerun()
    
    st.caption("Click states on the map or use the selector above")
    
    st.markdown("---")
    
    # Info section
    st.markdown("### ℹ️ About")
    st.caption("Analyzing NSF grants from 2020-2025, including terminated grants from the Trump administration.")
    st.caption("By Nicolás Villoria & Oriol Fontanals")

# ============================================================================
# HEADER
# ============================================================================

st.markdown("## 🔬 NSF Grants Explorer (2020-2025)")
st.markdown("---")

# ============================================================================
# 2x3 GRID LAYOUT
# ============================================================================

# Row 1: Directorate Evolution | Map + State Charts (linked)
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("##### 📊 Directorate Evolution")
    evolution_chart = create_directorate_evolution_chart(directorate_data)
    st.altair_chart(evolution_chart, use_container_width=True)

with col2:
    st.markdown("##### 🗺️ Map & State Analysis (Click to Filter)")
    linked_dashboard = create_linked_map_and_state_charts(grants_wide, lifecycle_df, df, selected_year)
    st.altair_chart(linked_dashboard, use_container_width=True)
    st.caption("💡 Click states on the map to filter. Shift+click for multiple selections. Double-click to clear.")

# Row 2: Termination by Directorate | Political Alignment
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("##### ⚠️ Termination by Directorate (2025)")
    termination_chart = create_termination_impact_chart(directorate_data, 'terminated_grants')
    st.altair_chart(termination_chart, use_container_width=True)

with col2:
    st.markdown(f"##### 🏛️ Political Alignment ({selected_year})")
    political_chart = create_political_scatter(political_source, selected_year)
    st.altair_chart(political_chart, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("NSF Grants Data 2020-2025 | By Nicolás Villoria & Oriol Fontanals | Interactive visualization with click-based state selection")
