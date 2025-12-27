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
    # Filter to main directorates and exclude "All years"
    main_directorates = ['MPS', 'CSE', 'ENG', 'GEO', 'EDU', 'BIO', 'TIP', 'SBE', 'O/D']
    filtered_data = directorate_data[
        (directorate_data['directorate'].isin(main_directorates)) &
        (directorate_data['year'] != 'All years')
    ].copy()
    filtered_data['year'] = filtered_data['year'].astype(int)
    
    line = alt.Chart(filtered_data).mark_line(
        interpolate='monotone',
        strokeWidth=2,
        point=True
    ).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d', labelAngle=0)),
        y=alt.Y('num_grants:Q', title='Active Grants'),
        color=alt.Color('directorate:N', title='Dir.', scale=alt.Scale(scheme='category10'),
                       legend=alt.Legend(orient='right', columns=1)),
        tooltip=[
            alt.Tooltip('directorate:N', title='Directorate'),
            alt.Tooltip('year:Q', title='Year'),
            alt.Tooltip('num_grants:Q', title='Grants', format=',')
        ]
    ).properties(
        width=350,
        height=280
    )
    
    return line


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
    
    chart = alt.Chart(termination_impact_df).mark_bar().encode(
        x=alt.X('directorate:N', sort='-y', title='Directorate', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y(f'terminated_grants:Q', title='Terminated'),
        color=alt.Color('directorate:N', legend=None, scale=alt.Scale(scheme='tableau10')),
        tooltip=[
            alt.Tooltip('directorate:N', title='Directorate'),
            alt.Tooltip('active_grants_2025:Q', title='Active (2025)', format=','),
            alt.Tooltip('terminated_grants:Q', title='Terminated', format=','),
            alt.Tooltip('termination_pct:Q', title='Rate (%)', format='.2f')
        ]
    ).properties(
        width=350,
        height=250
    )
    
    return chart


def prepare_lifecycle_data(df):
    """Prepare daily active grants lifecycle data."""
    df = df.copy()
    
    # Cap terminated grants at end of 2025
    mask_terminated = (df['terminated'] == True)
    mask_exceeds = df['awd_exp_date'] > pd.Timestamp('2025-12-31')
    df.loc[mask_terminated & mask_exceeds, 'awd_exp_date'] = pd.Timestamp('2025-12-31')
    df = df.dropna(subset=['awd_eff_date', 'awd_exp_date', 'inst_state_name'])
    
    events_start = df[['awd_eff_date', 'inst_state_name']].rename(columns={'awd_eff_date': 'Date'})
    events_start['Change'] = 1
    events_end = df[['awd_exp_date', 'inst_state_name']].copy()
    events_end['Date'] = events_end['awd_exp_date'] + pd.Timedelta(days=1)
    events_end = events_end.drop(columns=['awd_exp_date'])
    events_end['Change'] = -1
    
    daily_changes = pd.concat([events_start, events_end]).groupby(['inst_state_name', 'Date'])['Change'].sum().reset_index()
    daily_changes = daily_changes.sort_values(['inst_state_name', 'Date'])
    
    lifecycle_rows = []
    unique_states = daily_changes['inst_state_name'].unique()
    full_date_range = pd.date_range(start=daily_changes['Date'].min(), end=daily_changes['Date'].max(), freq='D')
    
    for state in unique_states:
        state_data = daily_changes[daily_changes['inst_state_name'] == state]
        state_data = state_data.set_index('Date').reindex(full_date_range).fillna(0)
        state_data['Active Grants'] = state_data['Change'].cumsum()
        state_data = state_data.reset_index().rename(columns={'index': 'Date'})
        state_data['State'] = state
        
        first_nonzero = state_data[state_data['Active Grants'] > 0].index.min()
        if pd.notna(first_nonzero):
            state_data = state_data.loc[first_nonzero:]
        
        lifecycle_rows.append(state_data[['Date', 'State', 'Active Grants']])
    
    return pd.concat(lifecycle_rows)


def prepare_lifecycle_data_with_statecode(df):
    """Prepare monthly lifecycle data with state codes for linked map selection."""
    df = df.copy()
    
    # Cap terminated grants at end of 2025
    mask_terminated = (df['terminated'] == True)
    mask_exceeds = df['awd_exp_date'] > pd.Timestamp('2025-12-31')
    df.loc[mask_terminated & mask_exceeds, 'awd_exp_date'] = pd.Timestamp('2025-12-31')
    df = df.dropna(subset=['awd_eff_date', 'awd_exp_date', 'inst_state_name', 'inst_state_code'])
    
    events_start = df[['awd_eff_date', 'inst_state_name', 'inst_state_code']].rename(columns={'awd_eff_date': 'Date'})
    events_start['Change'] = 1
    events_end = df[['awd_exp_date', 'inst_state_name', 'inst_state_code']].copy()
    events_end['Date'] = events_end['awd_exp_date'] + pd.Timedelta(days=1)
    events_end = events_end.drop(columns=['awd_exp_date'])
    events_end['Change'] = -1
    
    # Combine start and end events
    daily_changes = pd.concat([events_start, events_end]).groupby(['inst_state_name', 'inst_state_code', 'Date'])['Change'].sum().reset_index()
    daily_changes = daily_changes.sort_values(['inst_state_name', 'Date'])
    
    lifecycle_rows = []
    unique_states = daily_changes[['inst_state_name', 'inst_state_code']].drop_duplicates()
    # Use MONTHLY frequency for better performance
    full_date_range = pd.date_range(start=daily_changes['Date'].min(), end=daily_changes['Date'].max(), freq='MS')
    
    for _, row in unique_states.iterrows():
        state_name = row['inst_state_name']
        state_code = row['inst_state_code']
        state_data = daily_changes[daily_changes['inst_state_name'] == state_name].copy()
        state_data = state_data.groupby('Date')['Change'].sum().reset_index()
        state_data = state_data.set_index('Date').reindex(full_date_range).fillna(0)
        state_data['Active Grants'] = state_data['Change'].cumsum()
        state_data = state_data.reset_index().rename(columns={'index': 'Date'})
        state_data['State'] = state_name
        state_data['state_code'] = state_code
        
        first_nonzero = state_data[state_data['Active Grants'] > 0].index.min()
        if pd.notna(first_nonzero):
            state_data = state_data.loc[first_nonzero:]
        
        lifecycle_rows.append(state_data[['Date', 'State', 'state_code', 'Active Grants']])
    
    return pd.concat(lifecycle_rows, ignore_index=True)


def prepare_grants_by_state_wide(df):
    """Prepare wide-format grants by state data for linked choropleth with year slider."""
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
    
    # Pivot to wide format for year slider
    grants_wide = grants_df.pivot(
        index=['state', 'state_name', 'id'], 
        columns='year', 
        values=['num_grants', 'terminated_grants', 'terminated_pct']
    ).reset_index()
    grants_wide.columns = [f"{col[0]}_{col[1]}" if col[1] != '' else col[0] for col in grants_wide.columns]
    grants_wide = grants_wide.fillna(0)
    
    return grants_wide, grants_df['num_grants'].min(), grants_df['num_grants'].max()


def create_linked_map_and_lifecycle(grants_by_state, lifecycle_df, selected_year):
    """Create linked choropleth map and lifecycle chart with click-based state selection.
    
    Args:
        grants_by_state: Grants data from prepare_grants_by_state_data()
        lifecycle_df: Lifecycle data from prepare_lifecycle_data_with_statecode()
        selected_year: Year to display on the choropleth (from sidebar)
    """
    alt.data_transformers.enable('default')
    alt.data_transformers.disable_max_rows()

    # Filter data for selected year
    year_data = grants_by_state[grants_by_state['year'] == selected_year].copy()
    min_grants = grants_by_state['num_grants'].min()
    max_grants = grants_by_state['num_grants'].max()

    us_states = alt.topo_feature(vega_data.us_10m.url, 'states')

    # STATE LOOKUP FOR LABELS
    state_lookup = pd.DataFrame([
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
    ])

    east_coast_states = ['NH', 'MA', 'RI', 'NJ', 'DE', 'DC']
    state_lookup['label_longitude'] = state_lookup.apply(
        lambda row: row['longitude'] + 2 if row['state'] in east_coast_states else row['longitude'], axis=1
    )
    state_lookup['label_latitude'] = state_lookup.apply(
        lambda row: row['latitude'] - 1 if row['state'] in east_coast_states else row['latitude'], axis=1
    )

    # CREATE SHARED STATE SELECTION - use state to match lifecycle data
    state_selection = alt.selection_point(
        name='state_select',
        fields=['state'],
        on='click',
        toggle='event.shiftKey',
        clear='dblclick'
    )

    # 1. CHOROPLETH MAP (State Selector) - Uses year filtered by sidebar
    choropleth = alt.Chart(us_states).mark_geoshape(
        stroke='darkgray',
        strokeWidth=0.5
    ).encode(
        color=alt.Color(
            'num_grants:Q',
            scale=alt.Scale(scheme='blues', domain=[min_grants, max_grants]),
            title=f'Number of Grants ({selected_year})',
            legend=alt.Legend(orient='bottom')
        ),
        strokeWidth=alt.condition(state_selection, alt.value(3), alt.value(0.5)),
        stroke=alt.condition(state_selection, alt.value('#ff6600'), alt.value('darkgray')),
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

    # Leader lines for east coast
    leader_lines = alt.Chart(state_lookup[state_lookup['state'].isin(east_coast_states)]).mark_rule(
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

    # Puerto Rico circle
    pr_data = state_lookup[state_lookup['state'] == 'PR'].copy()
    pr_data = pr_data.merge(year_data[['id', 'num_grants', 'terminated_grants', 'terminated_pct']], on='id', how='left')
    
    pr_circle = alt.Chart(pr_data).mark_circle(size=400, stroke='white', strokeWidth=2).encode(
        longitude='longitude:Q', latitude='latitude:Q',
        color=alt.Color('num_grants:Q', scale=alt.Scale(scheme='blues', domain=[min_grants, max_grants]), legend=None),
        strokeWidth=alt.condition(state_selection, alt.value(4), alt.value(2)),
        stroke=alt.condition(state_selection, alt.value('#ff6600'), alt.value('white')),
        tooltip=[alt.Tooltip('state:N', title='State'), alt.Tooltip('num_grants:Q', title='Total Grants', format=',')]
    ).project(type='albersUsa')

    map_chart = (choropleth + leader_lines + state_labels + pr_circle).properties(
        width=500,
        height=380
    )

    # Rename state_code to state in lifecycle data for selection matching
    lifecycle_df_renamed = lifecycle_df.copy()
    lifecycle_df_renamed['state'] = lifecycle_df_renamed['state_code']

    # 2. TERMINATED GRANTS BAR CHART (Left of map, linked to selection)
    # Filter to only states with terminated grants > 0 and sort by terminated_grants
    terminated_data = year_data[year_data['terminated_grants'] > 0].copy()
    terminated_data = terminated_data.sort_values('terminated_grants', ascending=True)
    
    terminated_bar = alt.Chart(terminated_data).mark_bar(color='#d62728').encode(
        x=alt.X('terminated_grants:Q', title='Terminated Grants'),
        y=alt.Y('state:N', sort='-x', title='', axis=alt.Axis(labelFontSize=9)),
        opacity=alt.condition(state_selection, alt.value(1), alt.value(0.3)),
        tooltip=[
            alt.Tooltip('state:N', title='State'),
            alt.Tooltip('state_name:N', title='State Name'),
            alt.Tooltip('terminated_grants:Q', title='Terminated', format=','),
            alt.Tooltip('termination_pct:Q', title='Rate (%)', format='.2f')
        ]
    ).properties(
        width=120,
        height=380,
        title='Terminated'
    )

    # 3. LIFECYCLE LINE CHART (Filtered by Map Selection)
    lifecycle_line = alt.Chart(lifecycle_df_renamed).mark_line(strokeWidth=1.5).encode(
        x=alt.X('Date:T', axis=alt.Axis(title='Date', format='%Y-%m')),
        y=alt.Y('Active Grants:Q', axis=alt.Axis(title='Active Grants')),
        color=alt.Color('state:N', legend=None),
        opacity=alt.condition(state_selection, alt.value(1), alt.value(0.1)),
        strokeWidth=alt.condition(state_selection, alt.value(2.5), alt.value(0.5)),
        tooltip=['state:N', 'Date:T', 'Active Grants:Q']
    ).properties(
        width=400,
        height=380
    ).interactive()

    # Combine horizontally: bar chart | map | lifecycle
    dashboard = alt.hconcat(
        terminated_bar,
        map_chart,
        lifecycle_line
    ).resolve_scale(
        color='independent'
    )
    return dashboard


def create_grants_evolution_chart(lifecycle_df, selected_states=None):
    """Create line chart for grants evolution."""
    if not selected_states or len(selected_states) == 0:
        # Aggregate total
        agg = lifecycle_df.groupby('Date', as_index=False)['Active Grants'].sum()
        agg['State'] = 'All States'
        
        chart = alt.Chart(agg).mark_line(color='#1f77b4').encode(
            x=alt.X('Date:T', axis=alt.Axis(title='Date', format='%Y-%m')),
            y=alt.Y('Active Grants:Q', axis=alt.Axis(title='Active Grants')),
            tooltip=[
                alt.Tooltip('Date:T', title='Date', format='%Y-%m-%d'),
                alt.Tooltip('Active Grants:Q', title='Grants', format=',')
            ]
        ).properties(
            width=350,
            height=180
        ).interactive()
    else:
        subset = lifecycle_df[lifecycle_df['State'].isin(selected_states)].copy()
        current_domain = [s for s in selected_states if s in STATE_COLOR_MAP]
        current_range = [STATE_COLOR_MAP[s] for s in current_domain]
        
        chart = alt.Chart(subset).mark_line().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='Date', format='%Y-%m')),
            y=alt.Y('Active Grants:Q', axis=alt.Axis(title='Active Grants')),
            color=alt.Color('State:N', 
                          legend=alt.Legend(title='State', orient='bottom'),
                          scale=alt.Scale(domain=current_domain, range=current_range) if current_domain else alt.Scale()),
            tooltip=[
                alt.Tooltip('Date:T', format='%Y-%m-%d'),
                alt.Tooltip('Active Grants:Q', format=','),
                alt.Tooltip('State:N')
            ]
        ).properties(
            width=350,
            height=180
        ).interactive()
    
    return chart


# Q5: State Evolution with Termination Analysis

def create_state_evolution_with_termination(df, lifecycle_df, selected_states=None):
    """Create combined chart showing grants evolution and termination bar."""
    # Line chart
    line_chart = create_grants_evolution_chart(lifecycle_df, selected_states)
    
    # Bar chart for terminated grants
    if not selected_states or len(selected_states) == 0:
        total_terminated = df[df['terminated'] == True].shape[0]
        bar_data = pd.DataFrame({'State': ['All States'], 'Terminated Grants': [total_terminated]})
        
        bar_chart = alt.Chart(bar_data).mark_bar(color='#d62728').encode(
            x=alt.X('Terminated Grants:Q', axis=alt.Axis(title='Terminated')),
            y=alt.Y('State:N', axis=alt.Axis(title='')),
            tooltip=['State', 'Terminated Grants']
        ).properties(width=350, height=50)
    else:
        all_selected_df = pd.DataFrame({'State': selected_states})
        actual_counts = df[
            (df['inst_state_name'].isin(selected_states)) & 
            (df['terminated'] == True)
        ].groupby('inst_state_name').size().reset_index(name='Terminated Grants')
        
        merged_counts = pd.merge(
            all_selected_df, actual_counts, 
            left_on='State', right_on='inst_state_name', 
            how='left'
        )
        merged_counts['Terminated Grants'] = merged_counts['Terminated Grants'].fillna(0).astype(int)
        
        current_domain = [s for s in selected_states if s in STATE_COLOR_MAP]
        current_range = [STATE_COLOR_MAP[s] for s in current_domain]
        
        bar_chart = alt.Chart(merged_counts).mark_bar().encode(
            x=alt.X('Terminated Grants:Q', axis=alt.Axis(title='Terminated')),
            y=alt.Y('State:N', axis=alt.Axis(title=''), sort='-x'),
            color=alt.Color('State:N', scale=alt.Scale(domain=current_domain, range=current_range) if current_domain else alt.Scale(), legend=None),
            tooltip=['State', 'Terminated Grants']
        ).properties(width=350, height=max(50, 20 * len(selected_states)))
    
    return line_chart & bar_chart


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
    year_data = source_df[source_df['year'] == selected_year].copy()
    
    party_colors = alt.Scale(domain=['Democrat', 'Republican'], range=['#2166ac', '#b2182b'])
    
    # Hover selection parameter
    hover = alt.selection_point(
        fields=['State'],
        on='mouseover',
        empty=False
    )
    
    when_hover = alt.when(hover)

    # Base chart for trails (all years data)
    base = alt.Chart(source_df).encode(
        x=alt.X('active_grants:Q', scale=alt.Scale(zero=False)),
        y=alt.Y('total_funding_millions:Q', scale=alt.Scale(zero=False)),
        detail='State:N'
    )
    
    # Hover trail - line connecting all years for hovered state
    trail_line = base.mark_trail().encode(
        order=alt.Order('year:Q', sort='ascending'),
        size=alt.Size('year:Q',
                      scale=alt.Scale(domain=[2020, 2025], range=[2, 20]),
                      legend=None),
        opacity=when_hover.then(alt.value(0.5)).otherwise(alt.value(0)),
        color=alt.value('#444444')
    )
    
    # Trail points
    trail_points = base.mark_point(size=100).encode(
        opacity=when_hover.then(alt.value(0.8)).otherwise(alt.value(0)),
        color=alt.value('#444444')
    )

    # Year labels on hover trail
    year_labels = base.mark_text(align='left', dx=10, dy=-10, fontSize=11, fontWeight='bold').encode(
        text='year:O',
        color=alt.value('#333333'),
        opacity=when_hover.then(alt.value(1)).otherwise(alt.value(0))
    )

    # State label on hover (only for current year point)
    state_labels = alt.Chart(year_data).mark_text(
        align='left',
        dx=-15,
        dy=-25,
        fontSize=14,
        fontWeight='bold'
    ).encode(
        x='active_grants:Q',
        y='total_funding_millions:Q',
        text='State:N',
        color=alt.Color('political_alignment:N', scale=party_colors, legend=None),
        opacity=when_hover.then(alt.value(1)).otherwise(alt.value(0))
    )
    
    # Main points for current year
    points_chart = alt.Chart(year_data).mark_circle(size=100).encode(
        x=alt.X('active_grants:Q', scale=alt.Scale(zero=False), title='Active Grants'),
        y=alt.Y('total_funding_millions:Q', scale=alt.Scale(zero=False), title='Funding ($M)'),
        color=alt.Color('political_alignment:N', scale=party_colors, title='Party',
                       legend=alt.Legend(orient='top')),
        opacity=when_hover.then(alt.value(1)).otherwise(alt.value(0.5)),
        tooltip=[
            alt.Tooltip('State:N', title='State'),
            alt.Tooltip('active_grants:Q', title='Grants', format=','),
            alt.Tooltip('total_funding_millions:Q', title='Funding ($M)', format=',.1f'),
            alt.Tooltip('terminated_grants:Q', title='Terminated'),
            alt.Tooltip('political_alignment:N', title='Party')
        ]
    ).add_params(hover)

    # Background year text
    background_year = alt.Chart(pd.DataFrame({'year': [selected_year]})).mark_text(
        baseline='middle',
        fontSize=150,
        opacity=0.1,
        fontWeight='bold',
        color='#888888'
    ).encode(
        text='year:O'
    )
    
    # Combine all layers
    final_chart = alt.layer(
        background_year,
        trail_line,
        trail_points,
        year_labels,
        points_chart,
        state_labels
    ).properties(
        width=600,
        height=400
    )
    
    return final_chart


