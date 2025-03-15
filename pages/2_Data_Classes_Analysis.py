import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Set page configuration
st.set_page_config(
    page_title="Data Classes Analysis - Data Breach Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    with open('breaches.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    
    # Convert date columns to datetime
    df['BreachDate'] = pd.to_datetime(df['BreachDate'])
    
    # Create a column for breach size category
    df['BreachSizeCategory'] = pd.cut(
        df['PwnCount'],
        bins=[0, 10000, 1000000, 50000000, float('inf')],
        labels=['Small (<10k)', 'Medium (10k-1M)', 'Large (1M-50M)', 'Massive (>50M)']
    ).astype(str)  # Convert to string type immediately after creation
    
    # Explode the DataClasses column to analyze data types
    data_classes_df = df.explode('DataClasses')
    
    return df, data_classes_df

# Load the data
df, data_classes_df = load_data()

# Page title and description
st.title('📊 Data Classes Analysis')
st.markdown("""
<p style='font-size: 1.2em; color: #666;'>
Analyze the types of data compromised in breaches and understand the most vulnerable information categories.
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

# Create filtered version of data_classes_df
filtered_data_classes_df = data_classes_df[data_classes_df['Name'].isin(filtered_df['Name'])]

# Data Class Distribution
st.subheader('Distribution of Compromised Data Types')

data_class_counts = filtered_data_classes_df['DataClasses'].value_counts().reset_index()
data_class_counts.columns = ['Data Class', 'Count']
data_class_counts['Percentage'] = (data_class_counts['Count'] / len(filtered_df) * 100).round(1)

fig_distribution = px.bar(
    data_class_counts,
    x='Data Class',
    y='Count',
    title='Frequency of Data Types in Breaches',
    color='Count',
    labels={'Count': 'Number of Breaches', 'Data Class': 'Type of Data'},
    text='Percentage'
)

fig_distribution.update_traces(
    texttemplate='%{text}%',
    textposition='outside'
)

fig_distribution.update_layout(
    xaxis_tickangle=-45,
    height=600
)

st.plotly_chart(fig_distribution, use_container_width=True)

# Data Class Combinations
st.subheader('Common Data Class Combinations')

# Create combinations of data classes for each breach
data_combinations = filtered_df.apply(lambda x: ', '.join(sorted(x['DataClasses'])), axis=1).value_counts().head(10)
data_combinations_df = pd.DataFrame({
    'Combination': data_combinations.index,
    'Count': data_combinations.values
})

fig_combinations = px.bar(
    data_combinations_df,
    x='Count',
    y='Combination',
    orientation='h',
    title='Top 10 Most Common Data Class Combinations in Breaches',
    color='Count',
    labels={'Count': 'Number of Breaches', 'Combination': 'Data Classes Combination'}
)

fig_combinations.update_layout(
    height=500,
    yaxis={'categoryorder':'total ascending'}
)

st.plotly_chart(fig_combinations, use_container_width=True)

# Temporal Analysis of Data Classes
st.subheader('Evolution of Data Classes Over Time')

# Prepare data for temporal analysis
filtered_data_classes_df['Year'] = filtered_data_classes_df['BreachDate'].dt.year
temporal_data = filtered_data_classes_df.groupby(['Year', 'DataClasses']).size().reset_index()
temporal_data.columns = ['Year', 'Data Class', 'Count']

fig_temporal = px.line(
    temporal_data,
    x='Year',
    y='Count',
    color='Data Class',
    title='Trends in Compromised Data Types Over Time',
    labels={'Count': 'Number of Breaches', 'Year': 'Year'}
)

fig_temporal.update_layout(
    height=500,
    legend_title='Data Class',
    hovermode='x unified'
)

st.plotly_chart(fig_temporal, use_container_width=True)

# Key Insights
st.subheader('📈 Key Insights')

# Calculate insights
total_breaches = len(filtered_df)
most_common_data = data_class_counts.iloc[0]
most_common_combo = data_combinations_df.iloc[0]

# Display insights in columns
insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown(f"""
    #### Data Type Statistics
    - **Most Common Data Type**: {most_common_data['Data Class']}
    - **Frequency**: {most_common_data['Count']:,} breaches ({most_common_data['Percentage']}%)
    - **Total Unique Data Types**: {len(data_class_counts)} types
    """)

with insight_col2:
    st.markdown(f"""
    #### Combination Analysis
    - **Most Common Combination**: {most_common_combo['Combination']}
    - **Frequency**: {most_common_combo['Count']:,} breaches
    - **Average Data Types per Breach**: {filtered_df['DataClasses'].str.len().mean():.1f} types
    """)

# Recommendations
st.subheader('🔐 Security Recommendations')

st.markdown("""
#### Based on the analysis, consider these security measures:

1. **Data Encryption**
   - Implement strong encryption for the most commonly breached data types
   - Use different encryption methods for different data sensitivity levels

2. **Access Control**
   - Implement strict access controls for sensitive data combinations
   - Regular audit of access permissions and user privileges

3. **Data Minimization**
   - Only collect and store essential data
   - Regularly review and purge unnecessary data

4. **Security Training**
   - Focus training on protecting the most targeted data types
   - Regular security awareness programs for all employees
""")