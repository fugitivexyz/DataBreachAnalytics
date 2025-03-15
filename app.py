import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import matplotlib.pyplot as plt
import altair as alt

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
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .metric-card {
        background-color: #f8f9fa;
        border-left: 5px solid #3498db;
    }
    .insight-card {
        background-color: #f8f9fa;
        border-left: 5px solid #e74c3c;
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
    )
    
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
    options=df['BreachSizeCategory'].unique().tolist(),
    default=df['BreachSizeCategory'].unique().tolist()
)

if breach_size:
    filtered_df = filtered_df[filtered_df['BreachSizeCategory'].isin(breach_size)]

# Data class filter
all_data_classes = data_classes_df['DataClasses'].unique().tolist()
selected_data_classes = st.sidebar.multiselect(
    "Data Classes Compromised",
    options=all_data_classes,
    default=[]
)

if selected_data_classes:
    # Filter to breaches that contain ANY of the selected data classes
    filtered_data_classes_df = data_classes_df[data_classes_df['DataClasses'].isin(selected_data_classes)]
    filtered_df = filtered_df[filtered_df['Name'].isin(filtered_data_classes_df['Name'])]

# Create a filtered version of data_classes_df based on the current filtered_df
filtered_data_classes_df = data_classes_df[data_classes_df['Name'].isin(filtered_df['Name'])]

# Main dashboard
st.markdown('<h1 class="main-header">Data Breach Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; margin-bottom: 2rem; color: #7f8c8d;">Comprehensive analysis of data breaches for cybersecurity professionals and industry analysts</p>', unsafe_allow_html=True)

# 1. Overview (Summary Stats)
st.markdown('<div class="dashboard-metrics">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
    total_breaches = len(filtered_df)
    st.markdown(f'<div class="metric-value">{total_breaches:,}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Total Breaches</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
    total_pwned = filtered_df['PwnCount'].sum()
    st.markdown(f'<div class="metric-value">{total_pwned:,}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Total Affected Users</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
    verified_count = filtered_df['IsVerified'].sum()
    verified_percentage = (verified_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    st.markdown(f'<div class="metric-value">{verified_count:,} ({verified_percentage:.1f}%)</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Verified Breaches</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="card metric-card">', unsafe_allow_html=True)
    sensitive_count = filtered_df['IsSensitive'].sum()
    sensitive_percentage = (sensitive_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    st.markdown(f'<div class="metric-value">{sensitive_count:,} ({sensitive_percentage:.1f}%)</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Sensitive Breaches</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 2. Most Common Data Classes Breached
st.markdown('<h2 class="sub-header">Most Common Data Classes Breached</h2>', unsafe_allow_html=True)

data_class_counts = filtered_data_classes_df['DataClasses'].value_counts().reset_index()
data_class_counts.columns = ['DataClass', 'Count']
top_data_classes = data_class_counts.head(10)

# Calculate percentage of breaches for each data class
top_data_classes = top_data_classes.copy()  # Create a copy to avoid SettingWithCopyWarning
top_data_classes.loc[:, 'Percentage'] = (top_data_classes['Count'] / top_data_classes['Count'].sum() * 100).round(1)
top_data_classes.loc[:, 'Label'] = top_data_classes['DataClass'] + ' (' + top_data_classes['Percentage'].astype(str) + '%)'  

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

# 3. Breach Timeline Analysis
st.markdown('<h2 class="sub-header">Breach Timeline Analysis</h2>', unsafe_allow_html=True)

# Group by year and month
timeline_data = filtered_df.groupby('BreachYearMonth').agg(
    BreachCount=('Name', 'count'),
    TotalAffected=('PwnCount', 'sum')
).reset_index()

# Sort by date
timeline_data['BreachYearMonth'] = pd.to_datetime(timeline_data['BreachYearMonth'])
timeline_data = timeline_data.sort_values('BreachYearMonth')

# Create two tabs for different timeline views
tab1, tab2 = st.tabs(["Breach Count Timeline", "Users Affected Timeline"])

with tab1:
    fig_timeline = px.line(
        timeline_data,
        x='BreachYearMonth',
        y='BreachCount',
        title='Number of Breaches Over Time',
        labels={'BreachYearMonth': 'Date', 'BreachCount': 'Number of Breaches'}
    )
    fig_timeline.update_traces(line_color='#ff4b4b')
    st.plotly_chart(fig_timeline, use_container_width=True)

with tab2:
    fig_affected = px.line(
        timeline_data,
        x='BreachYearMonth',
        y='TotalAffected',
        title='Number of Users Affected Over Time',
        labels={'BreachYearMonth': 'Date', 'TotalAffected': 'Number of Users Affected'}
    )
    fig_affected.update_traces(line_color='#4b4bff')
    st.plotly_chart(fig_affected, use_container_width=True)

# 4. Most Significant Breaches
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

# Show details for a selected breach
selected_breach = st.selectbox(
    "Select a breach to view details",
    options=filtered_df['Name'].tolist(),
    index=0 if not filtered_df.empty else None
)

if selected_breach:
    breach_details = filtered_df[filtered_df['Name'] == selected_breach].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"{breach_details['Title']}")
        st.write(f"**Domain:** {breach_details['Domain']}")
        st.write(f"**Breach Date:** {breach_details['BreachDate'].strftime('%Y-%m-%d')}")
        st.write(f"**Added to Database:** {breach_details['AddedDate'].strftime('%Y-%m-%d')}")
        st.write(f"**Users Affected:** {breach_details['PwnCount']:,}")
        st.write(f"**Verified:** {'Yes' if breach_details['IsVerified'] else 'No'}")
        st.write(f"**Sensitive:** {'Yes' if breach_details['IsSensitive'] else 'No'}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Description")
        # Convert HTML entities in description
        description = breach_details['Description']
        # Basic HTML entity conversion for display
        description = description.replace('\u003C', '<').replace('\u003E', '>')
        st.markdown(description, unsafe_allow_html=True)
        
        st.subheader("Compromised Data Classes")
        for data_class in breach_details['DataClasses']:
            st.write(f"- {data_class}")
        st.markdown('</div>', unsafe_allow_html=True)

# 5. Verification Status Analysis
st.markdown('<h2 class="sub-header">Verification Status Analysis</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Verification status distribution
    verification_counts = filtered_df['IsVerified'].value_counts().reset_index()
    verification_counts.columns = ['Status', 'Count']
    verification_counts['Status'] = verification_counts['Status'].map({True: 'Verified', False: 'Unverified'})
    
    fig_verification = px.pie(
        verification_counts,
        values='Count',
        names='Status',
        title='Breach Verification Status Distribution',
        color='Status',
        color_discrete_map={'Verified': '#4CAF50', 'Unverified': '#FFC107'}
    )
    st.plotly_chart(fig_verification, use_container_width=True)

with col2:
    # Average users affected by verification status
    verification_impact = filtered_df.groupby('IsVerified')['PwnCount'].mean().reset_index()
    verification_impact.columns = ['Status', 'Average Users Affected']
    verification_impact['Status'] = verification_impact['Status'].map({True: 'Verified', False: 'Unverified'})
    
    fig_impact = px.bar(
        verification_impact,
        x='Status',
        y='Average Users Affected',
        title='Average Users Affected by Verification Status',
        color='Status',
        color_discrete_map={'Verified': '#4CAF50', 'Unverified': '#FFC107'},
        labels={'Average Users Affected': 'Average Users Affected', 'Status': 'Verification Status'}
    )
    st.plotly_chart(fig_impact, use_container_width=True)

# 6. User Impact Analysis
st.markdown('<h2 class="sub-header">User Impact Analysis</h2>', unsafe_allow_html=True)

# Create tabs for different impact visualizations
impact_tab1, impact_tab2 = st.tabs(["Breach Size Distribution", "Severity Analysis"])

with impact_tab1:
    # Distribution of breaches by size category
    size_distribution = filtered_df['BreachSizeCategory'].value_counts().reset_index()
    size_distribution.columns = ['Size Category', 'Count']
    
    # Calculate percentage for each category
    size_distribution = size_distribution.copy()  # Create a copy to avoid SettingWithCopyWarning
    size_distribution.loc[:, 'Percentage'] = (size_distribution['Count'] / size_distribution['Count'].sum() * 100).round(1)
    size_distribution.loc[:, 'Label'] = size_distribution['Size Category'].astype(str) + ' (' + size_distribution['Percentage'].astype(str) + '%)'  
    
    fig_size = px.bar(
        size_distribution,
        x='Size Category',
        y='Count',
        title='Distribution of Breaches by Size',
        color='Size Category',
        color_discrete_sequence=px.colors.qualitative.Set3,
        labels={'Count': 'Number of Breaches', 'Size Category': 'Breach Size'},
        text='Percentage'
    )
    
    fig_size.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_size.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor='rgba(0,0,0,0)'
    )

with impact_tab2:
    # Create a severity score based on multiple factors
    # 1. Size of breach (PwnCount)
    # 2. Sensitivity (IsSensitive)
    # 3. Types of data compromised (DataClasses)
    
    # Create a copy to avoid modifying the original dataframe
    severity_df = filtered_df.copy()
    
    # Define high-risk data classes
    high_risk_classes = [
        'Passwords', 'Credit cards', 'Social security numbers', 'Financial data',
        'Health records', 'Dates of birth', 'Phone numbers', 'Security questions and answers'
    ]
    
    # Calculate severity score components
    severity_df['SizeScore'] = pd.cut(
        severity_df['PwnCount'], 
        bins=[0, 10000, 1000000, 50000000, float('inf')],
        labels=[1, 2, 3, 4]
    ).astype(int)
    
    severity_df['SensitiveScore'] = severity_df['IsSensitive'].astype(int) * 3
    
    # Calculate data class risk score
    severity_df['HighRiskDataCount'] = severity_df['DataClasses'].apply(
        lambda x: sum(1 for item in x if item in high_risk_classes)
    )
    severity_df['DataClassScore'] = severity_df['HighRiskDataCount'].apply(lambda x: min(x, 3))
    
    # Calculate total severity score (max 10)
    severity_df['SeverityScore'] = (severity_df['SizeScore'] + 
                                  severity_df['SensitiveScore'] + 
                                  severity_df['DataClassScore'])
    severity_df['SeverityScore'] = severity_df['SeverityScore'].apply(lambda x: min(x, 10))
    
    # Create severity categories
    severity_df['SeverityCategory'] = pd.cut(
        severity_df['SeverityScore'],
        bins=[0, 3, 6, 10],
        labels=['Low', 'Medium', 'High']
    )
    
    # Display top high severity breaches
    st.subheader("Breach Severity Analysis")
    st.write("Severity is calculated based on breach size, sensitivity, and types of data compromised.")
    
    # Show distribution of severity categories
    severity_counts = severity_df['SeverityCategory'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    
    fig_severity = px.pie(
        severity_counts,
        values='Count',
        names='Severity',
        title='Distribution of Breach Severity',
        color='Severity',
        color_discrete_map={'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'},
        hole=0.4
    )
    
    fig_severity.update_traces(textposition='inside', textinfo='percent+label')
    fig_severity.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
    )
    
    st.plotly_chart(fig_severity, use_container_width=True)
    
    # Show top high severity breaches
    high_severity = severity_df[severity_df['SeverityCategory'] == 'High'].sort_values('SeverityScore', ascending=False)
    
    if not high_severity.empty:
        st.subheader("Top High-Severity Breaches")
        st.dataframe(
            high_severity[['Name', 'Domain', 'BreachDate', 'PwnCount', 'SeverityScore']].head(10),
            column_config={
                "Name": "Breach Name",
                "Domain": "Domain",
                "BreachDate": st.column_config.DateColumn("Breach Date"),
                "PwnCount": st.column_config.NumberColumn("Users Affected", format="%d"),
                "SeverityScore": st.column_config.ProgressColumn(
                    "Severity Score",
                    min_value=0,
                    max_value=10,
                    format="%d/10"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No high-severity breaches found in the current filtered dataset.")
st.plotly_chart(fig_size, use_container_width=True)

# 7. Sensitive Data Breaches
st.markdown('<h2 class="sub-header">Sensitive Data Breaches</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Sensitivity status distribution
    sensitivity_counts = filtered_df['IsSensitive'].value_counts().reset_index()
    sensitivity_counts.columns = ['Status', 'Count']
    sensitivity_counts['Status'] = sensitivity_counts['Status'].map({True: 'Sensitive', False: 'Non-Sensitive'})
    
    fig_sensitivity = px.pie(
        sensitivity_counts,
        values='Count',
        names='Status',
        title='Breach Sensitivity Status Distribution',
        color='Status',
        color_discrete_map={'Sensitive': '#F44336', 'Non-Sensitive': '#2196F3'}
    )
    st.plotly_chart(fig_sensitivity, use_container_width=True)

with col2:
    # Data classes in sensitive breaches
    if True in filtered_df['IsSensitive'].values:
        sensitive_breaches = filtered_df[filtered_df['IsSensitive'] == True]
        sensitive_data_classes = data_classes_df[data_classes_df['Name'].isin(sensitive_breaches['Name'])]
        sensitive_class_counts = sensitive_data_classes['DataClasses'].value_counts().reset_index().head(10)
        sensitive_class_counts.columns = ['DataClass', 'Count']
        
        # Calculate percentage for sensitive data classes
        sensitive_class_counts = sensitive_class_counts.copy()  # Create a copy to avoid SettingWithCopyWarning
        sensitive_class_counts.loc[:, 'Percentage'] = (sensitive_class_counts['Count'] / sensitive_class_counts['Count'].sum() * 100).round(1)
        sensitive_class_counts.loc[:, 'Label'] = sensitive_class_counts['DataClass'] + ' (' + sensitive_class_counts['Percentage'].astype(str) + '%)'  
        
        # Sort by count for better visualization
        sensitive_class_counts = sensitive_class_counts.sort_values('Count', ascending=True)
        
        fig_sensitive_classes = px.bar(
            sensitive_class_counts,
            x='Count',
            y='Label',  # Use the new label that includes percentage
            orientation='h',
            title='Top Data Classes in Sensitive Breaches',
            color='Count',
            color_continuous_scale='Reds',
            labels={'Count': 'Number of Breaches', 'Label': 'Data Class'},
            text='Count'  # Display the count on the bars
        )
        
        # Improve the layout
        fig_sensitive_classes.update_traces(textposition='outside')
        fig_sensitive_classes.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis_title='Number of Breaches',
            margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            height=500  # Increase height for better readability
        )
        st.plotly_chart(fig_sensitive_classes, use_container_width=True)
    else:
        st.info("No sensitive breaches in the current filtered dataset.")

# 8. Recent Additions and Modifications
st.markdown('<h2 class="sub-header">Recent Additions and Modifications</h2>', unsafe_allow_html=True)

# Sort by added date
recent_additions = filtered_df.sort_values('AddedDate', ascending=False).head(10)

st.subheader("Recently Added Breaches")
st.dataframe(
    recent_additions[['Name', 'Domain', 'BreachDate', 'AddedDate', 'PwnCount', 'IsVerified', 'IsSensitive']],
    column_config={
        "Name": "Breach Name",
        "Domain": "Domain",
        "BreachDate": st.column_config.DateColumn("Breach Date"),
        "AddedDate": st.column_config.DateColumn("Date Added"),
        "PwnCount": st.column_config.NumberColumn("Users Affected", format="%d"),
        "IsVerified": st.column_config.CheckboxColumn("Verified"),
        "IsSensitive": st.column_config.CheckboxColumn("Sensitive")
    },
    hide_index=True,
    use_container_width=True
)

# 9. Geographic Distribution Analysis
st.markdown('<h2 class="sub-header">Geographic Distribution Analysis</h2>', unsafe_allow_html=True)

# Extract geographic information if available
geo_data = []
for _, row in filtered_df.iterrows():
    if 'Geographic locations' in row['DataClasses']:
        geo_data.append({
            'Name': row['Name'],
            'Domain': row['Domain'],
            'BreachDate': row['BreachDate'],
            'PwnCount': row['PwnCount']
        })

geo_df = pd.DataFrame(geo_data)

if not geo_df.empty:
    st.write(f"Found {len(geo_df)} breaches with geographic location data")
    
    # Create a map visualization
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Breaches with Geographic Data")
    st.dataframe(
        geo_df,
        column_config={
            "Name": "Breach Name",
            "Domain": "Domain",
            "BreachDate": st.column_config.DateColumn("Breach Date"),
            "PwnCount": st.column_config.NumberColumn("Users Affected", format="%d")
        },
        hide_index=True,
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a note about geographic data
    st.info("Geographic data in breaches often indicates that location information of users was compromised, which can pose significant privacy and security risks.")
else:
    st.info("No breaches with geographic location data found in the current filtered dataset.")

# 10. Actionable Insights & Recommendations
st.markdown('<h2 class="sub-header">Actionable Insights & Recommendations</h2>', unsafe_allow_html=True)

# Generate insights based on the data
st.markdown('<div class="card insight-card">', unsafe_allow_html=True)
st.subheader("Key Insights")

# Most common data class
most_common_data_class = data_class_counts.iloc[0]['DataClass'] if not data_class_counts.empty else "N/A"

# Largest breach
largest_breach = filtered_df.nlargest(1, 'PwnCount')['Name'].iloc[0] if not filtered_df.empty else "N/A"
largest_breach_count = filtered_df.nlargest(1, 'PwnCount')['PwnCount'].iloc[0] if not filtered_df.empty else 0

# Recent trend (last 2 years vs previous 2 years)
current_year = datetime.now().year
recent_years = filtered_df[filtered_df['BreachYear'] >= (current_year - 2)]
previous_years = filtered_df[(filtered_df['BreachYear'] < (current_year - 2)) & 
                           (filtered_df['BreachYear'] >= (current_year - 4))]

recent_count = len(recent_years)
previous_count = len(previous_years)

trend_text = "increasing" if recent_count > previous_count else "decreasing"

# Display insights
st.write(f"📊 **Most Common Data Compromised:** {most_common_data_class}")
st.write(f"🔍 **Largest Breach:** {largest_breach} with {largest_breach_count:,} affected users")
st.write(f"📈 **Breach Trend:** Data breaches are {trend_text} compared to previous years")

# Recommendations
st.subheader("Recommendations")
st.write("🔐 **Password Security:** Regularly change passwords, especially for accounts where email addresses and passwords were compromised")
st.write(f"⚠️ **Data Awareness:** Be cautious with sharing {most_common_data_class.lower()}, as it's the most commonly compromised data type")
st.write("🛡️ **Multi-Factor Authentication:** Enable MFA on all accounts to provide an additional layer of security")
st.write("🔍 **Monitor Accounts:** Regularly check for suspicious activities on your accounts, especially if your data was part of a verified breach")
st.markdown('</div>', unsafe_allow_html=True)

# Search functionality
st.markdown('<h2 class="sub-header">Search Breaches</h2>', unsafe_allow_html=True)

search_term = st.text_input("Search for breaches by name, domain, or data class:")

if search_term:
    # Search in name, domain, and data classes
    name_domain_matches = filtered_df[
        filtered_df['Name'].str.contains(search_term, case=False) | 
        filtered_df['Domain'].str.contains(search_term, case=False)
    ]
    
    # Search in data classes
    data_class_matches = data_classes_df[
        data_classes_df['DataClasses'].str.contains(search_term, case=False)
    ]
    
    # Combine results
    search_results = pd.concat([
        name_domain_matches,
        filtered_df[filtered_df['Name'].isin(data_class_matches['Name'])]
    ]).drop_duplicates()
    
    if not search_results.empty:
        st.write(f"Found {len(search_results)} breaches matching '{search_term}'")
        st.dataframe(
            search_results[['Name', 'Domain', 'BreachDate', 'PwnCount', 'IsVerified', 'IsSensitive']],
            column_config={
                "Name": "Breach Name",
                "Domain": "Domain",
                "BreachDate": st.column_config.DateColumn("Breach Date"),
                "PwnCount": st.column_config.NumberColumn("Users Affected", format="%d"),
                "IsVerified": st.column_config.CheckboxColumn("Verified"),
                "IsSensitive": st.column_config.CheckboxColumn("Sensitive")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info(f"No breaches found matching '{search_term}'")

# Enhanced footer with more information for professionals
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <div style="margin-bottom: 1rem;">
        <strong>Data Breach Dashboard</strong> | Designed for Cybersecurity Professionals and Industry Analysts
    </div>
    <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
        <div style="margin: 0 1rem;">📊 Data sourced from Have I Been Pwned</div>
        <div style="margin: 0 1rem;">🔄 Last updated: {datetime.now().strftime('%Y-%m-%d')}</div>
    </div>
    <div style="font-size: 0.8rem; color: #95a5a6; margin-top: 0.5rem;">
        This dashboard is intended for educational and analytical purposes. 
        For more information on data breach prevention and mitigation strategies, please consult with a cybersecurity professional.
    </div>
</div>""", unsafe_allow_html=True)