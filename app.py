import pandas as pd
import streamlit as st
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Air Crashes Analysis",
    page_icon="✈️",
    layout="wide"
)

# Title
st.title("✈️ Air Crashes Analysis ")
st.markdown("---")

# Load data with caching
@st.cache_data
def load_data():
    
    df = pd.read_csv('aircrashesFullData.csv')
    return df

# Preprocess data
@st.cache_data
def preprocess_data(df):
    # Convert (year, month, day) to 'date'
    if 'Year' in df.columns and 'Month' in df.columns and 'Day' in df.columns:
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']], errors='coerce')
    
    # fill missing values (if any)
    df = df.fillna(method='ffill')
    
    return df

# Load and preprocess data
df = load_data()
df = preprocess_data(df)

#SIDEBAR FILTERS 
st.sidebar.header("🔍 Filters")

# Year range filter
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Operator filter
if 'Operator' in df.columns:
    operators = ['All'] + sorted(df['Operator'].dropna().unique().tolist())
    selected_operator = st.sidebar.selectbox("Select Operator", operators)
else:
    selected_operator = 'All'

# Country/Location filter
if 'Country' in df.columns or 'Location' in df.columns:
    location_col = 'Country' if 'Country' in df.columns else 'Location'
    locations = ['All'] + sorted(df[location_col].dropna().unique().tolist())
    selected_location = st.sidebar.selectbox(f"Select {location_col}", locations)
else:
    selected_location = 'All'

# Apply filters
filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

if 'Operator' in df.columns and selected_operator != 'All':
    filtered_df = filtered_df[filtered_df['Operator'] == selected_operator]

if ('Country' in df.columns or 'Location' in df.columns) and selected_location != 'All':
    location_col = 'Country' if 'Country' in df.columns else 'Location'
    filtered_df = filtered_df[filtered_df[location_col] == selected_location]

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Showing **{len(filtered_df):,}** of **{len(df):,}** records")

# STATISTICS SUMMARY 
st.header("📊 Statistics Summary")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Crashes", f"{len(filtered_df):,}")

with col2:
    years_span = year_range[1] - year_range[0] + 1
    avg_per_year = len(filtered_df) / years_span if years_span > 0 else 0
    st.metric("Avg Crashes/Year", f"{avg_per_year:.1f}")

with col3:
    if 'Fatalities' in filtered_df.columns:
        total_fatalities = filtered_df['Fatalities'].sum()
        st.metric("Total Fatalities", f"{total_fatalities:,.0f}")
    else:
        st.metric("Total Fatalities", "N/A")

with col4:
    if 'Fatalities' in filtered_df.columns:
        avg_fatalities = filtered_df['Fatalities'].mean()
        st.metric("Avg Fatalities/Crash", f"{avg_fatalities:.1f}")
    else:
        st.metric("Avg Fatalities/Crash", "N/A")

st.markdown("---")

# VISUALIZATIONS 
st.header("📈 Air Crashes Trends")

# Row 1: Two charts side by side
col1, col2 = st.columns(2)

with col1:
    st.subheader("Crashes Over Time")
    crashes_per_year = filtered_df['Year'].value_counts().sort_index()
    
    # Using Plotly for chart
    fig = px.line(
        x=crashes_per_year.index,
        y=crashes_per_year.values,
        labels={'x': 'Year', 'y': 'Number of Crashes'},
        title='Annual Air Crashes Trend'
    )
    fig.update_traces(line_color='#1f77b4', line_width=2)
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Crashes by Decade")
    if 'Decade' not in filtered_df.columns:
        filtered_df['Decade'] = (filtered_df['Year'] // 10) * 10
    
    crashes_by_decade = filtered_df['Decade'].value_counts().sort_index()
    
    fig = px.bar(
        x=crashes_by_decade.index,
        y=crashes_by_decade.values,
        labels={'x': 'Decade', 'y': 'Number of Crashes'},
        title='Crashes by Decade',
        color=crashes_by_decade.values,
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Row 2: Two more charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Operators")
    if 'Operator' in filtered_df.columns:
        top_operators = filtered_df['Operator'].value_counts().head(10)
        
        fig = px.bar(
            x=top_operators.values,
            y=top_operators.index,
            orientation='h',
            labels={'x': 'Number of Crashes', 'y': 'Operator'},
            title='Top 10 Operators by Crashes',
            color=top_operators.values,
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Operator column not found in dataset")

with col2:
    if 'Country' in filtered_df.columns or 'Location' in filtered_df.columns:
        location_col = 'Country' if 'Country' in filtered_df.columns else 'Location'
        st.subheader(f"Top 10 {location_col}s")
        Top_locations = filtered_df[location_col].value_counts().head(10)
        
        fig = px.bar(
            x=Top_locations.values,
            y=Top_locations.index,
            orientation='h',
            labels={'x': 'Number of Crashes', 'y': location_col},
            title=f'Top 10 {location_col}s by Crashes',
            color=Top_locations.values,
            color_continuous_scale='Reds'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Country/Location column not found in dataset")

st.markdown("---")

# ========== DATA TABLES ==========
st.header("📋 Data Tables")

tab1, tab2, tab3 = st.tabs(["📊 Summary Statistics", "🔝 Top Rankings", "📄 Data Sample"])

with tab1:
    st.subheader("Dataset Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**General Information:**")
        summary_info = pd.DataFrame({
            'Metric': ['Total Rows', 'Total Columns', 'Date Range', 'Memory Usage'],
            'Value': [
                f"{len(filtered_df):,}",
                len(filtered_df.columns),
                f"{filtered_df['Year'].min()} - {filtered_df['Year'].max()}",
                f"{filtered_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
            ]
        })
        st.dataframe(summary_info, hide_index=True, use_container_width=True)
    
    with col2:
        st.write("**Missing Values:**")
        missing_values = filtered_df.isnull().sum()
        missing_values = missing_values[missing_values > 0].sort_values(ascending=False)
        
        if len(missing_values) > 0:
            missing_df = pd.DataFrame({
                'Column': missing_values.index,
                'Missing Count': missing_values.values,
                'Percentage': (missing_values.values / len(filtered_df) * 100).round(2)
            })
            st.dataframe(missing_df, hide_index=True, use_container_width=True)
        else:
            st.success("✅ No missing values!")

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Operator' in filtered_df.columns:
            st.subheader("Top 15 Operators")
            top_operators = filtered_df['Operator'].value_counts().head(15)
            operator_df = pd.DataFrame({
                'Rank': range(1, len(top_operators) + 1),
                'Operator': top_operators.index,
                'Crashes': top_operators.values
            })
            st.dataframe(operator_df, hide_index=True, use_container_width=True)
    
    with col2:
        if 'Country' in filtered_df.columns or 'Location' in filtered_df.columns:
            location_colocation_col = 'Country' if 'Country' in filtered_df.columns else 'Location'
            st.subheader(f"Top 15 {location_col}s")
            top_locations = filtered_df[location_col].value_counts().head(15)
            location_df = pd.DataFrame({
                'Rank': range(1, len(top_locations) + 1),
                location_col: top_locations.index,
                'Crashes': top_locations.values
            })
            st.dataframe(location_df, hide_index=True, use_container_width=True)

with tab3:
    st.write(f"Showing first 100 rows of {len(filtered_df):,} records")
    st.dataframe(filtered_df.head(100), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Air Crashes Analysis Dashboard** | Data: 1908-2023| Built with Streamlit by Rahimat Ajoke (2026)")

