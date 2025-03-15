import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Data Breach Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and professional look
st.markdown("""
<style>
    /* Main layout and typography */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #ecf0f1;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #3498db;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #ecf0f1;
    }
    
    /* Cards styling */
    .card {
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        background-color: white;
        overflow: hidden;
        width: 100%;
        display: block;
        position: relative;
        color: #2c3e50;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .metric-card {
        background-color: white;
        border-left: 5px solid #3498db;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        height: 100%;
        color: #2c3e50;
    }
    .insight-card {
        background-color: white;
        border-left: 5px solid #e74c3c;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        padding: 1.5rem;
        height: 100%;
        width: 100%;
        color: #2c3e50;
    }
    
    .insight-card .content {
        width: 100%;
    }
    
    .insight-card h3 {
        color: #e74c3c;
        font-size: 1.4rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #ecf0f1;
        padding-bottom: 0.5rem;
    }
    
    .insight-card ul {
        margin-bottom: 1.5rem;
        padding-left: 1.2rem;
    }
    
    .insight-card li {
        margin-bottom: 0.7rem;
        line-height: 1.5;
    }
    
    .insight-card strong {
        color: #2980b9;
    }
    
    /* Metrics styling */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    
    /* Filter section styling */
    .sidebar .stSelectbox, .sidebar .stMultiselect {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #7f8c8d;
        padding: 1.5rem 0;
        margin-top: 2rem;
        border-top: 1px solid #ecf0f1;
        font-size: 0.9rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .sub-header {
            font-size: 1.5rem;
        }
        .metric-value {
            font-size: 1.8rem;
        }
    }
    
    /* Fix for white text and input bars */
    .stMarkdown, .stText {
        color: #2c3e50;
    }
    
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
        border: 1px solid #dfe1e6;
        border-radius: 4px;
    }
    
    /* Dashboard metrics container */
    .dashboard-metrics {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
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
    
    # Explode the DataClasses column to analyze data types
    data_classes_df = df.explode('DataClasses')
    
    return df, data_classes_df

# Load the data
df, data_classes_df = load_data()

# Sidebar filters
st.sidebar.title("Dashboard Filters")

# Date range filter
min_date = df['BreachDate'].min().date()
max_date = df['BreachDate'].max().date()
date_range = st.sidebar.date_input(
    "Breach Date Range",
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

# Verification status filter
verification_status = st.sidebar.multiselect(
    "Verification Status",
    options=["Verified", "Unverified"],
    default=["Verified", "Unverified"]
)

if verification_status:
    if "Verified" in verification_status and "Unverified" in verification_status:
        pass  # Keep all records
    elif "Verified" in verification_status:
        filtered_df = filtered_df[filtered_df['IsVerified'] == True]
    elif "Unverified" in verification_status:
        filtered_df = filtered_df[filtered_df['IsVerified'] == False]

# Sensitivity filter
sensitivity_status = st.sidebar.multiselect(
    "Sensitivity Status",
    options=["Sensitive", "Non-Sensitive"],
    default=["Sensitive", "Non-Sensitive"]
)

if sensitivity_status:
    if "Sensitive" in sensitivity_status and "Non-Sensitive" in sensitivity_status:
        pass  # Keep all records
    elif "Sensitive" in sensitivity_status:
        filtered_df = filtered_df[filtered_df['IsSensitive'] == True]
    elif "Non-Sensitive" in sensitivity_status:
        filtered_df = filtered_df[filtered_df['IsSensitive'] == False]

# Breach size filter
breach_size = st.sidebar.multiselect(
    "Breach Size",
    options=df['BreachSizeCategory'].dropna().unique().tolist(),
    default=df['BreachSizeCategory'].dropna().unique().tolist()
)

if breach_size:
    filtered_df = filtered_df[filtered_df['BreachSizeCategory'].isin(breach_size)]

# Create a filtered version of data_classes_df based on the current filtered_df
filtered_data_classes_df = data_classes_df[data_classes_df['Name'].isin(filtered_df['Name'])]

# Main dashboard
st.markdown('<h1 class="main-header">Data Breach Dashboard</h1>', unsafe_allow_html=True)

# Overview (Summary Stats)
st.markdown('<div class="dashboard-metrics">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_breaches = len(filtered_df)
    st.markdown(f'''
        <div class="card metric-card">
            <div class="metric-value">{total_breaches:,}</div>
            <div class="metric-label">Total Breaches</div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    total_pwned = filtered_df['PwnCount'].sum()
    st.markdown(f'''
        <div class="card metric-card">
            <div class="metric-value">{total_pwned:,}</div>
            <div class="metric-label">Total Affected Users</div>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    verified_count = filtered_df['IsVerified'].sum()
    verified_percentage = (verified_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    st.markdown(f'''
        <div class="card metric-card">
            <div class="metric-value">{verified_count:,} ({verified_percentage:.1f}%)</div>
            <div class="metric-label">Verified Breaches</div>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    sensitive_count = filtered_df['IsSensitive'].sum()
    sensitive_percentage = (sensitive_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    st.markdown(f'''
        <div class="card metric-card">
            <div class="metric-value">{sensitive_count:,} ({sensitive_percentage:.1f}%)</div>
            <div class="metric-label">Sensitive Breaches</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Most Common Data Classes Breached
st.markdown('<h2 class="sub-header">Most Common Data Classes Breached</h2>', unsafe_allow_html=True)

data_class_counts = filtered_data_classes_df['DataClasses'].value_counts().reset_index()
data_class_counts.columns = ['DataClass', 'Count']
top_data_classes = data_class_counts.head(10)

# Calculate percentage of breaches for each data class
top_data_classes = top_data_classes.copy()  # Create a copy to avoid SettingWithCopyWarning
top_data_classes.loc[:, 'Percentage'] = (top_data_classes['Count'] / top_data_classes['Count'].sum() * 100).round(1)

# Get the most common data class for insights
most_common_data_class = data_class_counts.iloc[0]['DataClass']

# Calculate other variables for insights
largest_breach = filtered_df.loc[filtered_df['PwnCount'].idxmax(), 'Name']
largest_breach_count = filtered_df['PwnCount'].max()

# Calculate trend
current_year = datetime.now().year
recent_breaches = filtered_df[filtered_df['BreachYear'] >= (current_year - 2)]
previous_breaches = filtered_df[(filtered_df['BreachYear'] < (current_year - 2)) & 
                               (filtered_df['BreachYear'] >= (current_year - 4))]
recent_count = len(recent_breaches)
previous_count = len(previous_breaches)
trend_text = 'increasing' if recent_count > previous_count else 'decreasing'

# Create labels with percentages - Fix for the TypeError
top_data_classes['Label'] = top_data_classes.apply(
    lambda row: f"{row['DataClass']} ({row['Percentage']}%)", axis=1
)

# Sort by count in descending order for better visualization
top_data_classes = top_data_classes.sort_values('Count', ascending=True)

fig_data_classes = px.bar(
    top_data_classes,
    x='Count',
    y='Label',  # Use the new label that includes percentage
    orientation='h',
    title='Top 10 Compromised Data Classes',
    color='Count',
    color_continuous_scale='Reds',
    labels={'Count': 'Number of Breaches', 'Label': 'Data Class'},
    text='Count'  # Display the count on the bars
)

# Improve the layout
fig_data_classes.update_traces(textposition='outside')
fig_data_classes.update_layout(
    yaxis={'categoryorder':'total ascending'},
    xaxis_title='Number of Breaches',
    margin=dict(l=10, r=10, t=40, b=10),
    plot_bgcolor='rgba(0,0,0,0)',
    height=500  # Increase height for better readability
)
st.plotly_chart(fig_data_classes, use_container_width=True)

# Most Significant Breaches
st.markdown('<h2 class="sub-header">Most Significant Breaches</h2>', unsafe_allow_html=True)

top_breaches = filtered_df.nlargest(10, 'PwnCount')

fig_top_breaches = px.bar(
    top_breaches,
    x='Name',
    y='PwnCount',
    title='Top 10 Breaches by Users Affected',
    color='PwnCount',
    color_continuous_scale='Blues',
    hover_data=['Domain', 'BreachDate', 'IsVerified', 'IsSensitive'],
    labels={'PwnCount': 'Users Affected', 'Name': 'Breach Name'}
)
st.plotly_chart(fig_top_breaches, use_container_width=True)

# Actionable Insights & Recommendations
st.markdown('<h2 class="sub-header">Actionable Insights & Recommendations</h2>', unsafe_allow_html=True)

# Generate insights based on the data
st.markdown(
    f"""
    <div class="card insight-card">
        <div class="content">
            <h3>Key Data Breach Insights</h3>
            <ul>
                <li><b>Most Common Data Type:</b> {most_common_data_class}</li>
                <li><b>Largest Breach:</b> {largest_breach} affecting {largest_breach_count:,} users</li>
                <li><b>Recent Trend:</b> Data breaches are {trend_text} compared to previous years ({recent_count} breaches in the last 2 years vs {previous_count} in the 2 years before that)</li>
            </ul>
            <h3>Recommendations</h3>
            <ul>
                <li><b>Focus security training</b> on protecting {most_common_data_class} data</li>
                <li><b>Implement stronger authentication mechanisms</b> to prevent unauthorized access</li>
                <li><b>Regularly audit and update</b> data protection policies</li>
                <li><b>Consider implementing data minimization strategies</b> to reduce breach impact</li>
            </ul>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Add footer
st.markdown('<div class="footer">Data Breach Dashboard | Updated: ' + datetime.now().strftime("%B %Y") + '</div>', unsafe_allow_html=True)