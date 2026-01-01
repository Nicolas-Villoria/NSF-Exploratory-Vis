"""
Analysis Functions for NSF Grants Explorer
Contains all visualization and question-answering functions for Streamlit app
"""

import pandas as pd
import altair as alt
from vega_datasets import data as vega_data

# Set global Altair theme for white background and black text
alt.themes.enable('default')
def white_theme():
    return {
        'config': {
            'background': 'white',
            'view': {'fill': 'white'},
            'title': {'color': 'black'},
            'axis': {
                'labelColor': 'black',
                'titleColor': 'black',
                'tickColor': 'black',
                'domainColor': 'black'
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
        }
    }
alt.themes.register('white_theme', white_theme)
alt.themes.enable('white_theme')

# Chart dimension constants for consistent sizing
CHART_WIDTH = 350
CHART_HEIGHT = 280
MAP_WIDTH = 400
MAP_HEIGHT = 300


# DATA LOADING FUNCTIONS

def load_data():
    """Load and preprocess the NSF grants data."""
    df = pd.read_csv('nsf_data_clean.csv', low_memory=False)
    df['awd_eff_date'] = pd.to_datetime(df['awd_eff_date'], errors='coerce')
    df['awd_exp_date'] = pd.to_datetime(df['awd_exp_date'], errors='coerce')
    return df


def load_political_data():
    """Load political alignment data."""
    return pd.read_csv('state_political_alignment.csv')


# State color map for consistent coloring
STATE_COLOR_MAP = {
    'Alabama': '#1f77b4', 'Alaska': '#aec7e8', 'Arizona': '#ff7f0e', 'Arkansas': '#ffbb78',
    'California': '#2ca02c', 'Colorado': '#98df8a', 'Connecticut': '#d62728', 'Delaware': '#ff9896',
    'District of Columbia': '#9467bd', 'Florida': '#c5b0d5', 'Georgia': '#8c564b', 'Hawaii': '#c49c94',
    'Idaho': '#e377c2', 'Illinois': '#f7b6d2', 'Indiana': '#7f7f7f', 'Iowa': '#c7c7c7',
    'Kansas': '#bcbd22', 'Kentucky': '#dbdb8d', 'Louisiana': '#17becf', 'Maine': '#9edae5',
    'Maryland': '#393b79', 'Massachusetts': '#5254a3', 'Michigan': '#6b6ecf', 'Minnesota': '#9c9ede',
    'Mississippi': '#637939', 'Missouri': '#8ca252', 'Montana': '#b5cf6b', 'Nebraska': '#cedb9c',
    'Nevada': '#8c6d31', 'New Hampshire': '#bd9e39', 'New Jersey': '#e7ba52', 'New Mexico': '#e7cb94',
    'New York': '#843c39', 'North Carolina': '#ad494a', 'North Dakota': '#d6616b', 'Ohio': '#e7969c',
    'Oklahoma': '#7b4173', 'Oregon': '#a55194', 'Pennsylvania': '#ce6dbd', 'Rhode Island': '#de9ed6',
    'South Carolina': '#3182bd', 'South Dakota': '#6baed6', 'Tennessee': '#9ecae1', 'Texas': '#c6dbef',
    'Utah': '#e6550d', 'Vermont': '#fd8d3c', 'Virginia': '#fdae6b', 'Washington': '#fdd0a2',
    'West Virginia': '#31a354', 'Wisconsin': '#74c476', 'Wyoming': '#a1d99b', 'Puerto Rico': '#756bb1',
    'Virgin Islands': '#9e9ac8', 'American Samoa': '#7b4173', 'Guam': '#a55194',
    'Northern Mariana Isl': '#ce6dbd', 'RI REQUIRED': '#de9ed6'
}

# State FIPS codes for map
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

# State lookup data for choropleth labels
STATE_LOOKUP_DATA = [
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
    {"id": 72, "state": "PR", "longitude": -75.5158, "latitude": 24.7663},
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
]

EAST_COAST_STATES = ['NH', 'MA', 'RI', 'NJ', 'DE', 'DC']

directorate_colors = {
    'MPS': '#1f77b4',
    'CSE': '#E69F00',
    'ENG': '#009E73',
    'GEO': '#D55E00',
    'EDU': '#F0E442',
    'BIO': '#7F6A3A',
    'SBE': '#56B4E9',
    'TIP': '#CC79A7',
    'O/D': '#999999',
}

DIR_DOMAIN = ['MPS','CSE','ENG','GEO','EDU','BIO','SBE', 'TIP','O/D']
DIR_RANGE  = [directorate_colors[k] for k in DIR_DOMAIN]
DIR_SCALE  = alt.Scale(domain=DIR_DOMAIN, range=DIR_RANGE)


# Q1: Grants Distribution by State

def prepare_grants_by_state_data(df):
    """Prepare grants by state data for choropleth map."""
    results = []
    for state in df['inst_state_code'].unique():
        state_df = df[df['inst_state_code'] == state]
        state_name = state_df['inst_state_name'].iloc[0] if len(state_df) > 0 else state
        
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            active_mask = (
                (state_df['awd_eff_date'] <= year_end) & 
                (state_df['awd_exp_date'] >= year_start)
            )
            num_active = active_mask.sum()
            terminated_count = state_df['terminated'].sum() if year == 2025 else 0
            terminated_pct = (terminated_count / num_active * 100) if num_active > 0 else 0
            
            results.append({
                'state': state,
                'state_name': state_name,
                'year': year,
                'num_grants': num_active,
                'terminated_grants': terminated_count,
                'terminated_pct': round(terminated_pct, 2)
            })
    
    grants_df = pd.DataFrame(results)
    grants_df['id'] = grants_df['state'].map(STATE_FIPS)
    grants_df = grants_df.dropna(subset=['id'])
    grants_df['id'] = grants_df['id'].astype(int)
    return grants_df


def create_choropleth_map(year_data, selected_year, min_grants, max_grants, state_selection):
    """Create choropleth map of US states showing grant distribution.
    
    Args:
        year_data: DataFrame with grants data for the selected year
        selected_year: Year to display on the choropleth
        min_grants: Minimum number of grants (for color scale)
        max_grants: Maximum number of grants (for color scale)
        state_selection: Altair selection parameter for linking
    
    Returns:
        Altair chart object (layered map with labels)
    """
    us_states = alt.topo_feature(vega_data.us_10m.url, 'states')
    
    # Prepare state lookup with label positions
    state_lookup = pd.DataFrame(STATE_LOOKUP_DATA)
    state_lookup['label_longitude'] = state_lookup.apply(
        lambda row: row['longitude'] + 2 if row['state'] in EAST_COAST_STATES else row['longitude'], axis=1
    )
    state_lookup['label_latitude'] = state_lookup.apply(
        lambda row: row['latitude'] - 1 if row['state'] in EAST_COAST_STATES else row['latitude'], axis=1
    )

    # Choropleth base map
    choropleth = alt.Chart(us_states).mark_geoshape(
        stroke='darkgray',
        strokeWidth=0.5
    ).encode(
        color=alt.Color(
            'num_grants:Q',
            scale=alt.Scale(scheme='blues', domain=[min_grants, max_grants]),
            title=f'Number of Grants',
            legend=alt.Legend(orient='bottom')
        ),
        strokeWidth=alt.condition(state_selection, alt.value(4), alt.value(1)),
        stroke=alt.condition(state_selection, alt.value("#FFC067"), alt.value("white")),
        tooltip=[
            alt.Tooltip('state:N', title='State'),
            alt.Tooltip('state_name:N', title='State Name'),
            alt.Tooltip('num_grants:Q', title='Total Grants', format=','),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants', format=','),
            alt.Tooltip('terminated_pct:Q', title='Termination %', format='.2f')
        ]
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(year_data, 'id', ['state', 'state_name', 'num_grants', 'terminated_grants', 'terminated_pct'])
    ).project(type='albersUsa').add_params(
        state_selection
    )

    # Leader lines for east coast states
    leader_lines = alt.Chart(state_lookup[state_lookup['state'].isin(EAST_COAST_STATES)]).mark_rule(
        strokeWidth=1, color='gray', opacity=0.6, strokeDash=[3, 3]
    ).encode(
        longitude='longitude:Q', latitude='latitude:Q',
        longitude2='label_longitude:Q', latitude2='label_latitude:Q'
    ).project(type='albersUsa')

    # State labels
    state_labels = alt.Chart(state_lookup).mark_text(
        fontSize=9, fontWeight='bold', color='black', opacity=0.7
    ).encode(
        longitude='label_longitude:Q', latitude='label_latitude:Q', text='state:N'
    ).project(type='albersUsa')

    # Puerto Rico circle (since it's not in the continental US projection)
    pr_data = state_lookup[state_lookup['state'] == 'PR'].copy()
    pr_data = pr_data.merge(year_data[['id', 'num_grants', 'terminated_grants', 'terminated_pct']], on='id', how='left')
    
    pr_circle = alt.Chart(pr_data).mark_circle(size=400, stroke='white', strokeWidth=2).encode(
        longitude='longitude:Q', latitude='latitude:Q',
        color=alt.Color('num_grants:Q', scale=alt.Scale(scheme='blues', domain=[min_grants, max_grants]), legend=None),
        strokeWidth=alt.condition(state_selection, alt.value(4), alt.value(0.5)),
        stroke=alt.condition(state_selection, alt.value('#FFC067'), alt.value('white')),
        tooltip=[alt.Tooltip('state:N', title='State'), alt.Tooltip('num_grants:Q', title='Total Grants', format=',')]
    ).project(type='albersUsa')

    # Combine all layers
    map_chart = (choropleth + leader_lines + state_labels + pr_circle).properties(
        width=MAP_WIDTH,
        height=230,
        title=alt.TitleParams(
            text="NSF Grants by State: Political Alignment Analysis in {}".format(selected_year),
            subtitle="Click to select a state, shift-click to multiselect, double-click to clear selection",
            fontSize=16,
            anchor="middle",
            align="center",
        )
    )
    
    return map_chart


# Q2: Grants Distribution by Directorate

def prepare_directorate_data(df):
    """Prepare data for directorate visualization."""
    directorate_results = []
    for directorate in df['dir_abbr'].unique():
        dir_df = df[df['dir_abbr'] == directorate]
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            active_mask = (
                (dir_df['awd_eff_date'] <= year_end) & 
                (dir_df['awd_exp_date'] >= year_start)
            )
            num_active = active_mask.sum()
            terminated_count = dir_df['terminated'].sum() if year == 2025 else 0
            
            directorate_results.append({
                'directorate': directorate,
                'year': str(year),
                'num_grants': num_active,
                'terminated_grants': terminated_count
            })
    
    # Add "All years" aggregation
    for directorate in df['dir_abbr'].unique():
        dir_df = df[df['dir_abbr'] == directorate]
        directorate_results.append({
            'directorate': directorate,
            'year': 'All years',
            'num_grants': len(dir_df),
            'terminated_grants': dir_df['terminated'].sum()
        })
    
    return pd.DataFrame(directorate_results)


def create_directorate_evolution_chart(directorate_data):
    """Create line chart showing evolution of grants by directorate."""
    # Create a selection that chooses the nearest point based on year
    nearest = alt.selection_point(
        nearest=True,
        on='mouseover',
        fields=['year'],
        empty=False
    )

    # The basic line chart
    line = alt.Chart(directorate_data).mark_line(
        interpolate='monotone',
        strokeWidth=2
    ).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('num_grants:Q', title='Number of Active Grants', scale=alt.Scale(domain=[0, 16000])),
        color=alt.Color(
            'directorate:N',
            title='Directorate',
            scale=DIR_SCALE, legend=alt.Legend(title='Directorate', orient='right', offset=2)
        )
    )

    # Transparent selectors across the chart
    selectors = alt.Chart(directorate_data).mark_point().encode(
        x='year:Q',
        opacity=alt.value(0),
    ).add_params(nearest)

    # Draw points on the lines, and highlight based on selection
    points = line.mark_point(size=80).encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(
        align='left',
        dx=10,
        dy=0,
        fontSize=11
    ).encode(
        text=alt.condition(nearest, 'num_grants:Q', alt.value(' '))
    )

    # Draw a vertical rule at the location of the selection
    rules = alt.Chart(directorate_data).mark_rule(
        color='gray',
        strokeWidth=1
    ).encode(
        x='year:Q',
    ).transform_filter(nearest)

    # Combine all layers
    q2_grants_per_dir_chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=CHART_WIDTH,
        height=255,
        title=alt.TitleParams('Evolution of Number of Active Grants by Directorate', color='black', fontSize=16, anchor='middle', align='center')
    )

    return q2_grants_per_dir_chart


# Q3: Termination Impact Analysis

def prepare_termination_impact_data(df):
    """Prepare data for termination impact analysis."""
    termination_impact = []
    main_directorates = ['MPS', 'CSE', 'ENG', 'GEO', 'EDU', 'BIO', 'TIP', 'SBE']
    
    for directorate in df['dir_abbr'].unique():
        if directorate not in main_directorates:
            continue
        dir_df = df[df['dir_abbr'] == directorate]
        
        year_start = pd.Timestamp('2025-01-01')
        year_end = pd.Timestamp('2025-12-31')
        active_mask = (
            (dir_df['awd_eff_date'] <= year_end) & 
            (dir_df['awd_exp_date'] >= year_start)
        )
        num_active_2025 = active_mask.sum()
        num_terminated = dir_df['terminated'].sum()
        termination_pct = (num_terminated / num_active_2025 * 100) if num_active_2025 > 0 else 0
        
        termination_impact.append({
            'directorate': directorate,
            'active_grants_2025': num_active_2025,
            'terminated_grants': num_terminated,
            'termination_pct': round(termination_pct, 2)
        })
    
    return pd.DataFrame(termination_impact).sort_values('terminated_grants', ascending=False)


def create_termination_impact_chart(termination_impact_df):
    """Create bar chart for termination impact."""
    
    q3_termination_impact_chart = alt.Chart(termination_impact_df).mark_bar().encode(
        x=alt.X(
            'directorate:N',
            sort='-y',
            title='Directorate',
            axis=alt.Axis(labelAngle=-45)
        ),
        y=alt.Y(
            'terminated_grants:Q',
            title='Value'
        ),
        color=alt.Color('directorate:N', scale=DIR_SCALE, title='Directorate', legend=None)
        ,
        tooltip=[
            alt.Tooltip('directorate:N', title='Directorate'),
            alt.Tooltip('active_grants_2025:Q', title='Active Grants (2025)', format=','),
            alt.Tooltip('terminated_grants:Q', title='Terminated Grants (2025)', format=','),
            alt.Tooltip('termination_pct:Q', title='Termination Rate (%)', format='.2f')
        ]
    ).properties(
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        title=alt.TitleParams('Grant Termination Impact by Directorate in 2025', color='black', fontSize=16, anchor='middle', align='center')
    )

    return q3_termination_impact_chart


# Q4: Grants Lifecycle Analysis

def prepare_lifecycle_data_with_statecode(df):
    """Prepare daily lifecycle data using vectorized operations."""
    # Ensure datetime format
    df = df.copy()
    # Note: dates are already converted in load_data, but ensuring consistency
    
    clean_df = df.dropna(subset=['awd_eff_date', 'awd_exp_date', 'inst_state_name', 'inst_state_code']).copy()
    clean_df = clean_df[clean_df['awd_eff_date'] <= clean_df['awd_exp_date']]

    # Create events DataFrame
    starts = clean_df[['awd_eff_date', 'inst_state_name']].rename(columns={'awd_eff_date': 'date'})
    starts['change'] = 1

    ends = clean_df[['awd_exp_date', 'inst_state_name']].copy()
    ends['date'] = ends['awd_exp_date'] + pd.Timedelta(days=1)
    ends = ends.drop(columns=['awd_exp_date'])
    ends['change'] = -1

    # Combine and reshape
    all_events = pd.concat([starts, ends], ignore_index=True)
    daily_changes = all_events.groupby(['date', 'inst_state_name'])['change'].sum().unstack(fill_value=0)

    # Resample and Calculate
    # Use daily resolution 
    daily_changes = daily_changes.resample('D').sum().fillna(0)
    active_counts_by_state = daily_changes.cumsum()
    
    # Add Allstates column
    active_counts_by_state['Allstates'] = active_counts_by_state.sum(axis=1)

    # Filter for required date range: 2020-01-01 to 2026 
    start_date = pd.Timestamp('2020-01-01')
    end_date = pd.Timestamp('2026-01-01') 
    active_counts_by_state = active_counts_by_state.loc[start_date:end_date]

    # Melt to Long Format
    active_counts_long = active_counts_by_state.reset_index().melt(
        id_vars=['date'],
        var_name='inst_state_name',
        value_name='active_grants'
    )

    # Get state codes for the chart selection
    # We need to preserve inst_state_code for the 'state' column used in selection
    id_map = clean_df[['inst_state_name', 'inst_state_code']].drop_duplicates()
    
    # Merge to get the codes
    active_counts_long = active_counts_long.merge(id_map, on='inst_state_name', how='left')
    
    # Handle Allstates code
    active_counts_long.loc[active_counts_long['inst_state_name'] == 'Allstates', 'inst_state_code'] = 'Allstates'

    # Rename columns to match create_lifecycle_line_chart expectations
    # Expected: Date, State, state_code, Active Grants
    active_counts_long = active_counts_long.rename(columns={
        'date': 'Date',
        'inst_state_name': 'State',
        'inst_state_code': 'state_code',
        'active_grants': 'Active Grants'
    })
    
    return active_counts_long


def create_lifecycle_line_chart(lifecycle_df, state_selection):
    """Create line chart showing grant lifecycle over time by state.
    
    Args:
        lifecycle_df: DataFrame with Date, State, state_code, Active Grants columns
        state_selection: Altair selection parameter for linking
    
    Returns:
        Altair chart object
    """
    # Rename state_code to state for selection matching
    lifecycle_df_renamed = lifecycle_df.copy()
    lifecycle_df_renamed['state'] = lifecycle_df_renamed['state_code']
    
    # Dynamic Y scale based on selection status
    y_scale = alt.Scale(
        domainRaw=alt.expr("length(data('state_select_store')) > 0 ? [0, 6000] : [0, 60000]"),
        nice=False
    )
    
    # Tick values every 4 months
    tick_values = [x for x in pd.date_range(start='2020-01-01', end='2026-01-01', freq='4MS')]

    # Common axis
    x_axis = alt.X(
        "Date:T", 
        axis=alt.Axis(
            title="Date", 
            format="%b %Y", 
            values=tick_values,
            labelAngle=-45
        )
    )
    y_axis = alt.Y("Active Grants:Q", scale=y_scale, axis=alt.Axis(title="Active Grants"))
    
    # All-states line (only when nothing selected)
    all_layer = (
        alt.Chart(lifecycle_df_renamed)
        .mark_line(color="#1f77b4")
        .encode(
            x=x_axis,
            y=y_axis,
            tooltip=[
                alt.Tooltip("Date:T", title="Date", format='%b %d, %Y'),
                alt.Tooltip("State:N", title="State"),
                alt.Tooltip("Active Grants:Q", title="Number of active grants"),
            ],
        )
        .transform_filter("length(data('state_select_store')) == 0")
        .transform_filter(alt.datum.State == 'Allstates')
    )

    all_label = (
        alt.Chart(lifecycle_df_renamed)
        .transform_filter("length(data('state_select_store')) == 0")
        .transform_filter(alt.datum.State == 'Allstates')
        .transform_window(
            sort=[alt.SortField("Date", order="descending")],
            rank="rank()",
        )
        .transform_filter(alt.datum.rank == 1)
        .mark_text(align="left", dx=6, fontSize=11, color="#1f77b4")
        .encode(
            x=alt.X("Date:T", axis=alt.Axis(title="Date", format="%b %Y", values=tick_values, labelAngle=-45)),
            y="Active Grants:Q",
            text=alt.value("All states"),
        )
    )

    # Hover selection for highlighting specific state line
    hover_state = alt.selection_point(
        name="hover_state",
        fields=["State"],
        on="mouseover",
        clear="mouseout",
        empty="none",
    )

    # Base chart for selected states only
    selected_base = (
        alt.Chart(lifecycle_df_renamed)
        .transform_filter("length(data('state_select_store')) > 0")
        .transform_filter(state_selection)
        .transform_filter(alt.datum.State != 'Allstates')
    )

    # Selected lines: dim all, highlight hovered
    selected_lines = (
        selected_base
        .mark_line()
        .encode(
            x=x_axis,
            y=y_axis,
            detail="State:N",
            color=alt.condition(hover_state, alt.value("#FFC067"), alt.value("#74a3cc")),
            strokeWidth=alt.condition(hover_state, alt.value(3), alt.value(1.75)),
            opacity=alt.condition(hover_state, alt.value(1), alt.value(1)),
            tooltip=[
                alt.Tooltip("Date:T", title="Date", format='%b %d, %Y'),
                alt.Tooltip("State:N", title="State"),
                alt.Tooltip("Active Grants:Q", title="Number of active grants"),
            ],
        )
        .add_params(hover_state)
    )

    # End-of-line labels
    end_labels = (
        selected_base
        .transform_window(
            sort=[alt.SortField("Date", order="descending")],
            rank="rank()",
            groupby=["State"],
        )
        .transform_filter(alt.datum.rank == 1)
        .mark_text(align="left", dx=6, fontSize=11)
        .encode(
            x="Date:T",
            y="Active Grants:Q",
            text="State:N",
            opacity=alt.value(1),
            color=alt.condition(hover_state, alt.value("#FFC067"), alt.value("#74a3cc")),
        )
    )

    # Dynamic title
    title_expr = alt.expr(
        "length(data('state_select_store')) > 0 ? "
        "'Evolution of number of active grants from 2020-2025 for selected states' : "
        "'Evolution of number of active grants from 2020-2025 for all states'"
    )

    # Combine selected layers
    chart = (all_layer + all_label + selected_lines + end_labels).add_params(
        state_selection
    ).properties(
        title=alt.TitleParams(text=title_expr, subtitle="When multiple states are selected, hover over a state to highlight its line",fontSize=16, anchor="middle", align="center"),
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
    )
    
    return chart


# Q5: Bar Chart of Terminated Grants by State

def create_terminated_bar_chart(terminated_data, state_selection):
    """Create horizontal bar chart showing terminated grants by state.
    
    Args:
        terminated_data: DataFrame with states that have terminated_grants > 0
        state_selection: Altair selection parameter for linking
    
    Returns:
        Altair chart object
    """
    # Renaming for consistency with other charts
    chart_data = terminated_data.rename(columns={'terminated_grants': 'Count', 'state_name': 'State'})

    # Dynamic x scale
    x_scale = alt.Scale(
        domainRaw=alt.expr("length(data('state_select_store')) > 0 ? [0, 300] : [0, 2500]"),
        nice=False
    )

    y_sorted = alt.Y(
        "State:N",
        title=None,
        sort=alt.EncodingSortField(
            field="Count",
            op="max",
            order="descending"
        ),
        axis=alt.Axis(labelFontSize=9)
    )

    # Layer A: All States
    all_layer = (
        alt.Chart(chart_data)
        .mark_bar(color="#1f77b4")
        .encode(
            x=alt.X("Count:Q", title="Number of Terminated Grants", scale=x_scale),
            y=y_sorted,
            tooltip=[
                alt.Tooltip("State:N", title="State"),
                alt.Tooltip("Count:Q", title="Number of Terminated Grants"),
            ],
        )
        .transform_filter("length(data('state_select_store')) == 0")
        .transform_filter("datum.State == 'All States'")
    )
    
    # Layer B: Selected states
    selected_layer = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("Count:Q", title="Number of Terminated Grants", scale=x_scale),
            y=y_sorted,
            color=alt.value("#74a3cc"),
            tooltip=[
                alt.Tooltip("State:N", title= "State") ,
                alt.Tooltip("Count:Q", title="Number of Terminated Grants"),
            ],
        )
        .transform_filter("length(data('state_select_store')) > 0")
        .transform_filter(state_selection)
        .transform_filter("datum.State != 'All States'")
    )

    title_expr = alt.expr("length(data('state_select_store')) > 0 ? 'Number of terminated grants for the selected states in 2025' : 'Number of terminated grants for all states in 2025'")

    chart = (all_layer + selected_layer).properties(
        title=alt.TitleParams(text=title_expr, fontSize=16, anchor="middle", align="center"),
        width=CHART_WIDTH,
        height=CHART_HEIGHT
    ).add_params(
        state_selection
    )
    
    return chart


# Q6: Political Alignment Analysis

def get_political_alignment(row):
    if row['year'] < 2024:
        return row['2020_Election_Winner']
    else:
        return row['2024_Election_Winner']
    

def prepare_political_data(df, political_df):
    """Prepare data for political alignment visualization."""
    state_year_stats = []
    for state_abbr in df['inst_state_code'].unique():
        state_df = df[df['inst_state_code'] == state_abbr]
        
        for year in range(2020, 2026):
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            
            active_mask = (
                (state_df['awd_eff_date'] <= year_end) & 
                (state_df['awd_exp_date'] >= year_start)
            )
            active_grants = state_df[active_mask]
            num_active = len(active_grants)
            total_funding = active_grants['awd_amount'].sum() / 1000000
            
            if year == 2025:
                num_terminated = state_df['terminated'].sum()
                terminated_funding = state_df[state_df['terminated'] == True]['awd_amount'].sum() / 1000000
            else:
                num_terminated = 0
                terminated_funding = 0
            
            termination_pct = (num_terminated / num_active * 100) if num_active > 0 else 0
            
            state_year_stats.append({
                'Abbreviation': state_abbr,
                'year': year,
                'active_grants': num_active,
                'total_funding_millions': round(total_funding, 2),
                'terminated_grants': int(num_terminated),
                'terminated_funding_millions': round(terminated_funding, 2),
                'termination_pct': round(termination_pct, 2)
            })
    
    state_year_df = pd.DataFrame(state_year_stats)
    source_df = state_year_df.merge(political_df, on='Abbreviation', how='left')
    source_df = source_df.dropna(subset=['2020_Election_Winner'])
    source_df['political_alignment'] = source_df.apply(get_political_alignment, axis=1)
    source_df = source_df.drop(columns=['2020_Election_Winner', '2024_Election_Winner', 'Current_Gov_Party'], errors='ignore')
    
    # Add State column for chart compatibility
    source_df['State'] = source_df['Abbreviation']
    
    return source_df


def create_political_scatter(source_df, selected_year):
    """Create Gapminder-style scatter plot for political analysis with hover trail."""
    
    # Controls
    hover = alt.selection_point(on="mouseover", fields=["State"], empty=False)
    hover_point_opacity = alt.selection_point(on="mouseover", fields=["State"])

    party_colors = alt.Scale(domain=["Democrat", "Republican"], range=["#2166ac", "#b2182b"])

    # Base chart (uses all years data for trails)
    base = (
        alt.Chart(source_df)
        .encode(
            x=alt.X("active_grants:Q", scale=alt.Scale(zero=False), title="Number of Active Grants"),
            y=alt.Y("total_funding_millions:Q", scale=alt.Scale(zero=False), title="Total Funding (Millions $)"),
            color=alt.Color(
                "political_alignment:N",
                scale=party_colors,
                title="Political Alignment",
                legend=alt.Legend(orient="bottom", titleFontSize=12, labelFontSize=10, symbolStrokeWidth=6),
            ),
            detail="State:N",
        )
        .interactive()
    )

    # Opacity logic (dim valid points if not hovered)
    opacity = (
        alt.when(hover_point_opacity)
        .then(alt.value(0.7))
        .otherwise(alt.value(0.25))
    )

    # Points filtered by selected_year
    visible_points = (
        base.mark_circle(size=200)
        .encode(
            opacity=opacity,
            tooltip=[
                alt.Tooltip("State:N", title="State"),
                alt.Tooltip("active_grants:Q", title="Active Grants", format=","),
                alt.Tooltip("total_funding_millions:Q", title="Total Funding ($M)", format=",.1f"),
                alt.Tooltip("terminated_grants:Q", title="Terminated Grants"),
                alt.Tooltip("termination_pct:Q", title="Termination %", format=".2f"),
            ],
        )
        .transform_filter(alt.datum.year == selected_year)
        .add_params(hover, hover_point_opacity)
    )

    # Hover trail effect
    when_hover = alt.when(hover)

    hover_line = alt.layer(
        base.mark_trail().encode(
            order=alt.Order("year:Q", sort="ascending"),
            size=alt.Size("year:Q", scale=alt.Scale(domain=[2020, 2025], range=[2, 20]), legend=None),
            opacity=when_hover.then(alt.value(0.5)).otherwise(alt.value(0)),
            color=alt.value("#444444"),
        ),
        base.mark_point(size=120).encode(
            opacity=when_hover.then(alt.value(0.9)).otherwise(alt.value(0)),
        ),
    )

    # Year labels on hover trail
    year_labels = (
        base.mark_text(align="left", dx=12, dy=-12, fontSize=12, fontWeight="bold")
        .encode(
            text="year:O",
            color=alt.value("#333333"),
            opacity=when_hover.then(alt.value(1)).otherwise(alt.value(0)),
        )
        .transform_filter(hover)
    )

    # State labels at current year (filtered)
    state_labels = (
        alt.Chart(source_df)
        .mark_text(align="left", dx=-20, dy=-35, fontSize=18, fontWeight="bold")
        .encode(
            x="active_grants:Q",
            y="total_funding_millions:Q",
            text="State:N",
            color=alt.Color("political_alignment:N", scale=party_colors),
            opacity=when_hover.then(alt.value(1)).otherwise(alt.value(0)),
        )
        .transform_filter(alt.datum.year == selected_year)
    )

    # Background year text
    background_year = (
        alt.Chart(pd.DataFrame({'year': [selected_year]}))
        .mark_text(
            baseline="middle",
            fontSize=120,
            fontWeight="bold",
            color="#9e9e9e",
            opacity=0.3,
            text=str(selected_year)
        )
    )

    # Combine all layers
    final_chart = (
        alt.layer(background_year, hover_line, visible_points, year_labels, state_labels)
        .properties(
            width=MAP_WIDTH,
            height=MAP_HEIGHT,
            title=alt.TitleParams(
                text="NSF Grants by State: Political Alignment Analysis",
                subtitle="Hover to see state trajectory over time.",
                fontSize=16,
                anchor="middle",
                align="center",
                offset=10
            ),
        )
    )
    
    return final_chart


def final_vis(df, grants_by_state, lifecycle_df, directorate_data, termination_impact_df, political_source_df, selected_year):
    """Create the complete NSF grants dashboard with all linked visualizations.
    
    Args:
        df: Raw NSF grants dataframe
        grants_by_state: Grants data from prepare_grants_by_state_data()
        lifecycle_df: Lifecycle data from prepare_lifecycle_data_with_statecode()
        directorate_data: Directorate data from prepare_directorate_data()
        termination_impact_df: Termination impact data from prepare_termination_impact_data()
        political_source_df: Political data from prepare_political_data()
        selected_year: Year to display on the choropleth (from sidebar)
    """
    alt.data_transformers.enable('vegafusion')
    # alt.data_transformers.disable_max_rows() # VegaFusion handles large data automatically

    # Filter data for selected year
    year_data = grants_by_state[grants_by_state['year'] == selected_year].copy()
    min_grants = grants_by_state['num_grants'].min()
    max_grants = grants_by_state['num_grants'].max()

    # CREATE SHARED STATE SELECTION - use state to match lifecycle data
    state_selection = alt.selection_point(
        name='state_select',
        fields=['state'],
        on='click',
        toggle='event.shiftKey',
        clear='dblclick',
        empty='none'
    )

    # 1. CHOROPLETH MAP (State Selector)
    map_chart = create_choropleth_map(year_data, selected_year, min_grants, max_grants, state_selection)

    # 2. DIRECTORATE EVOLUTION LINE CHART
    directorate_line = create_directorate_evolution_chart(directorate_data)

    # 3. TERMINATION IMPACT BAR CHART
    termination_impact_chart = create_termination_impact_chart(termination_impact_df)

    # 4. LIFECYCLE LINE CHART (Filtered by Map Selection)
    lifecycle_line = create_lifecycle_line_chart(lifecycle_df, state_selection)

    # 5. TERMINATED GRANTS BAR CHART (Left of map, linked to selection)
    # Filter to only states with terminated grants > 0 and sort by terminated_grants
    # Always use 2025 data for terminated grants chart
    terminated_data = grants_by_state[grants_by_state['year'] == 2025].copy()
    terminated_data = terminated_data[terminated_data['terminated_grants'] > 0]
    
    # Add All States total
    total_terminated = terminated_data['terminated_grants'].sum()
    all_states_row = pd.DataFrame([{
        'state_name': 'All States',
        'state': 'All States',  # For consistency
        'terminated_grants': total_terminated,
        'id': -1
    }])
    terminated_data = pd.concat([terminated_data, all_states_row], ignore_index=True)
    
    terminated_data = terminated_data.sort_values('terminated_grants', ascending=True)
    terminated_bar = create_terminated_bar_chart(terminated_data, state_selection)

    # 6. Political Alignment Scatter Plot
    political_scatter = create_political_scatter(political_source_df, selected_year)

    # Build columns using & (vertical) and | (horizontal) concatenation
    column_1 = lifecycle_line & terminated_bar
    column_2 = map_chart & political_scatter
    column_3 = directorate_line & termination_impact_chart

    # Combine columns horizontally
    dashboard = (column_1 | column_2 | column_3).properties(
        title=alt.TitleParams(
            text=f'NSF Grants Dashboard',
            subtitle="Explore NSF grant data and termination patterns",
            fontSize=30,
            anchor='middle',
            offset=20
        ),
        padding={'left': 40, 'right': 40, 'top': 10, 'bottom': 20}
    ).configure_view(
        strokeWidth=0
    ).configure_concat(
        spacing=40
    ).resolve_scale(
        color='independent'
    ).resolve_legend(
        color='independent'
    )
    
    return dashboard





