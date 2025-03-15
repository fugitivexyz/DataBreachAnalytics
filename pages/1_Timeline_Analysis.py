import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Timeline Analysis - Data Breach Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data (reusing the same function from Home.py)
@st.cache_data
def load_data():
    with open('breaches.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    
    # Convert date columns to datetime
    df['BreachDate'] = pd.to_datetime(df['BreachDate'])
    df['AddedDate'] = pd.to_datetime(df['AddedDate'])
    df['ModifiedDate'] = pd.to_datetime(df['ModifiedDate'])
    
    # Extract year and month for timeline analysis
    df['BreachYear'] = df['BreachDate'].dt.year
    df['BreachMonth'] = df['BreachDate'].dt.month
    df['BreachYearMonth'] = df['BreachDate'].dt.strftime('%Y-%m')
    
    # Create a column for breach size category
    df['BreachSizeCategory'] = pd.cut(
        df['PwnCount'],
        bins=[0, 10000, 1000000, 50000000, float('inf')],
        labels=['Small (<10k)', 'Medium (10k-1M)', 'Large (1M-50M)', 'Massive (>50M)']
    ).astype(str)  # Convert to string type immediately after creation
    
    return df

# Load the data
df = load_data()

# Page title and description
st.title('📊 Timeline Analysis')
st.markdown("""
<p style='font-size: 1.2em; color: #666;'>
Explore how data breaches have evolved over time, identifying trends and patterns in breach frequency and impact.
</p>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("📊 Analysis Filters")

# Date range filter
min_date = df['BreachDate'].min().date()
max_date = df['BreachDate'].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['BreachDate'].dt.date >= start_date) & 
                    (df['BreachDate'].dt.date <= end_date)]
else:
    filtered_df = df

# Breach size filter
breach_size = st.sidebar.multiselect(
    "Breach Size",
    options=df['BreachSizeCategory'].dropna().unique().tolist(),
    default=df['BreachSizeCategory'].dropna().unique().tolist()
)

if breach_size:
    filtered_df = filtered_df[filtered_df['BreachSizeCategory'].isin(breach_size)]

# Create two columns for the visualizations
col1, col2 = st.columns(2)

with col1:
    # Yearly trend analysis
    yearly_breaches = filtered_df.groupby('BreachYear').size().reset_index()
    yearly_breaches.columns = ['Year', 'Number of Breaches']
    
    fig_yearly = px.line(
        yearly_breaches,
        x='Year',
        y='Number of Breaches',
        title='Yearly Trend of Data Breaches',
        markers=True
    )
    fig_yearly.update_layout(
        xaxis_title='Year',
        yaxis_title='Number of Breaches',
        hovermode='x'
    )
    st.plotly_chart(fig_yearly, use_container_width=True)

with col2:
    # Monthly distribution
    monthly_breaches = filtered_df.groupby('BreachMonth').size().reset_index()
    monthly_breaches.columns = ['Month', 'Number of Breaches']
    
    fig_monthly = px.bar(
        monthly_breaches,
        x='Month',
        y='Number of Breaches',
        title='Monthly Distribution of Breaches',
        color='Number of Breaches'
    )
    fig_monthly.update_layout(
        xaxis_title='Month',
        yaxis_title='Number of Breaches',
        xaxis=dict(tickmode='array', ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                   tickvals=list(range(1, 13)))
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

# Breach size distribution over time
st.subheader('Breach Size Distribution Over Time')

# Handle potential missing or invalid categories
filtered_df['BreachSizeCategory'] = filtered_df['BreachSizeCategory'].astype(str)  # Ensure string type for consistency

# Create the distribution with proper handling of categories
yearly_size_dist = filtered_df.groupby(['BreachYear', 'BreachSizeCategory']).size().reset_index()
yearly_size_dist.columns = ['Year', 'Size Category', 'Count']

fig_size_dist = px.bar(
    yearly_size_dist,
    x='Year',
    y='Count',
    color='Size Category',
    title='Breach Size Distribution by Year',
    barmode='stack'
)

fig_size_dist.update_layout(
    xaxis_title='Year',
    yaxis_title='Number of Breaches',
    legend_title='Breach Size',
    hovermode='x'
)

st.plotly_chart(fig_size_dist, use_container_width=True)

# Key insights section
st.subheader('📈 Key Timeline Insights')

# Calculate insights
total_breaches = len(filtered_df)
yearly_avg = total_breaches / len(yearly_breaches)
worst_year = yearly_breaches.loc[yearly_breaches['Number of Breaches'].idxmax()]
worst_month = monthly_breaches.loc[monthly_breaches['Number of Breaches'].idxmax()]

# Display insights in columns
insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown(f"""
    #### Overall Trends
    - **Total Breaches**: {total_breaches:,}
    - **Average Breaches per Year**: {yearly_avg:.1f}
    - **Peak Year**: {worst_year['Year']} ({worst_year['Number of Breaches']:,} breaches)
    """)

with insight_col2:
    st.markdown(f"""
    #### Seasonal Patterns
    - **Most Common Month**: {['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][worst_month['Month']-1]}
    - **Peak Monthly Count**: {worst_month['Number of Breaches']:,} breaches
    """)