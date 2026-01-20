# NSF Grants Explorer

## Overview

This project analyzes National Science Foundation grant data from 2020 to 2025, with a focus on understanding the impact of the 2025 wave of grant terminations that followed the change in federal administration. We built an interactive dashboard that allows users to explore geographic distribution, funding trends by research directorate, and the relationship between state political alignment and termination patterns.

The NSF is one of the largest sources of federal funding for fundamental research in the U.S., so changes in its grant portfolio have real consequences for universities and research labs. Our goal was to make these patterns visible and explorable without requiring users to write queries or parse raw data.

## System Architecture

The system is structured around two main components: a preprocessing pipeline and a Streamlit application.

The preprocessing layer consists of Python scripts that combine yearly grant exports, join them with termination records, and produce a clean CSV ready for visualization. This approach keeps the data transformation separate from the visualization logic, making it easier to update either side independently. The `combine_grants.py` script aggregates grants from 2016-2025 into a single file, while `join_terminated_grants.py` matches award IDs against the list of terminated grants and adds a boolean flag.

The Streamlit app loads the cleaned data on startup and computes several derived datasets (grants by state, lifecycle timelines, directorate breakdowns, political alignment mappings). All of this is cached to avoid recomputation on each user interaction. The dashboard itself is built with Altair, composed of six linked visualizations that share a selection state so users can filter across views by clicking on states.

## Data and Feature Engineering

The primary data source is the NSF awards database, which we accessed as yearly CSV exports. Each record contains award metadata including effective and expiration dates, funding amounts, institutional affiliation, and the NSF directorate responsible for the grant. We also incorporated a list of terminated awards that was published in early 2025.

One challenge was that grants are not tied to a single year. A grant awarded in 2021 might still be active in 2024. We computed "active grants" for each year by checking whether a grant's effective and expiration dates overlap with that calendar year. This required careful handling of date boundaries and edge cases.

For political alignment, we joined state-level data with election results from 2020 and 2024. Grants active before 2024 are tagged with the 2020 election outcome for their state; grants in 2024-2025 use the 2024 result. This lets us examine whether termination rates differ by partisan geography.

We removed columns that were not relevant to the analysis (contact details, internal agency codes) to reduce noise and improve load times.

## Visualization Approach

The dashboard includes six coordinated views:

1. A choropleth map showing grant counts by state, with color intensity proportional to the number of active grants. Clicking a state filters the other charts.
2. A line chart tracking the number of active grants over time, with one line per selected state. When no state is selected, it shows a single aggregated line for the entire country.
3. A horizontal bar chart ranking states by the number of terminated grants in 2025.
4. A line chart showing how grant counts evolved by NSF directorate (MPS, CSE, BIO, etc.) from 2020 to 2025.
5. A bar chart comparing termination counts across directorates.
6. A scatter plot showing the relationship between active grants and total funding, colored by political alignment, with hover trails that reveal each state's trajectory over time.

All charts use a shared selection mechanism. When a user clicks on California in the map, the lifecycle chart, termination bar chart, and scatter plot update to show only California. Shift-click allows multiselect.

## User-Facing Application

The Streamlit app is intended for researchers, journalists, or policy analysts who want to understand how NSF funding has shifted over time and which states or research areas were most affected by terminations.

The sidebar includes a year selector (2020-2025) that controls the choropleth and scatter plot. Users can explore historical snapshots or focus on 2025 to see the termination impact directly.

The app is designed to load quickly and remain responsive. We use Altair with VegaFusion for rendering large datasets efficiently, and all heavy computation happens at startup and is cached.

## Engineering Trade-offs

We chose to precompute aggregates (grants by state, by year, by directorate) rather than computing them on the fly. This adds some upfront complexity but keeps interactions fast.

We used Altair for visualization because it handles linked selections natively and produces portable Vega-Lite specs. The downside is that some customizations require workarounds, but the interactivity benefits outweighed this.

Data is stored in flat CSV files rather than a database. For a dataset of this size (around 100k records after preprocessing), this is sufficient and avoids the overhead of running a separate database service.

## How to Run

Install dependencies:

```
pip install -r requirements.txt
```

Run the Streamlit app:

```
streamlit run Fontanals_Villoria_streamlit.py
```

The app will open in your browser. Use the sidebar to select a year and click on states to filter the dashboard.

## Complementary project and improvements
This is the second part of the Information Visualisation course project. In the first one (NSF-Grant-Termination-Analysis-Dashboard) we could see:

1. Institution-level drill-down so users could see which institutions lost the most funding.
2. Keyword and topic extraction from grant abstracts to identify which research themes were most affected.
3. Comparison between termination and reinstatement rates for grants on Ted Cruz's "wasteful spending" list.

Some further improvements after terminating the project could be the following:
1. Automate data refresh by pulling from the NSF API instead of relying on manual CSV exports.
2. Add export functionality so users can download filtered data for their own analysis.
