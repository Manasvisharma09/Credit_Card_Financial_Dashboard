import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Credit Card Financial Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .filter-header {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
    
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess data with caching"""
    try:
        df = pd.read_csv("cc_add.csv", parse_dates=["Week_Start_Date"])
        # Data cleaning
        df.fillna(0, inplace=True)
        df['Month'] = df['Week_Start_Date'].dt.to_period('M').astype(str)
        df['Is_Delinquent'] = df['Delinquent_Acc'].apply(lambda x: 'Yes' if x == 1 else 'No')
        return df
    except FileNotFoundError:
        st.error("❌ Data file 'cc_add.csv' not found. Please upload the file to proceed.")
        return None

def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    col = st.container()
    with col:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">💳 Credit Card Financial Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown('<div class="filter-header">📊 Dashboard Filters</div>', unsafe_allow_html=True)
        
        # Filters with better organization
        st.markdown("### 📅 Time Period")
        month = st.multiselect(
            "Select Months", 
            sorted(df['Month'].unique()), 
            default=sorted(df['Month'].unique()),
            help="Choose specific months to analyze"
        )
        
        st.markdown("### 💳 Card Details")
        category = st.multiselect(
            "Card Category", 
            df['Card_Category'].unique(), 
            default=df['Card_Category'].unique()
        )
        
        st.markdown("### 💰 Transaction Details")
        exp_type = st.multiselect(
            "Expense Type", 
            df['Exp Type'].unique(), 
            default=df['Exp Type'].unique()
        )
        
        channel = st.multiselect(
            "Payment Channel", 
            df['Use Chip'].unique(), 
            default=df['Use Chip'].unique()
        )
        
        st.markdown("### ⚠️ Risk Analysis")
        delinquent = st.multiselect(
            "Delinquency Status", 
            ['Yes', 'No'], 
            default=['Yes', 'No']
        )
        
        # Add data info
        st.markdown("---")
        st.markdown("### 📈 Data Summary")
        st.info(f"**Total Records:** {len(df):,}\n\n**Date Range:** {df['Month'].min()} to {df['Month'].max()}")
    
    # Filter data
    filtered_df = df[
        df['Month'].isin(month) &
        df['Card_Category'].isin(category) &
        df['Exp Type'].isin(exp_type) &
        df['Use Chip'].isin(channel) &
        df['Is_Delinquent'].isin(delinquent)
    ]
    
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
        return
    
    # KPIs Section with enhanced layout
    st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_spending = filtered_df['Total_Trans_Amt'].sum()
        create_metric_card("Total Spending", f"${total_spending:,.0f}")
    with col2:
        num_transactions = filtered_df['Total_Trans_Ct'].sum()
        create_metric_card("Total Transactions", f"{num_transactions:,.0f}")
    with col3:
        avg_transaction = total_spending / num_transactions if num_transactions else 0
        create_metric_card("Avg Transaction Value", f"${avg_transaction:,.2f}")
    with col4:
        active_customers = filtered_df['Client_Num'].nunique()
        create_metric_card("Active Customers", f"{active_customers:,}")
    
    # Bottom row metrics
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        outstanding_balance = filtered_df['Total_Revolving_Bal'].sum()
        create_metric_card("Outstanding Balance", f"${outstanding_balance:,.0f}")
    with col6:
        credit_utilization = (outstanding_balance / filtered_df['Credit_Limit'].sum() * 100) if filtered_df['Credit_Limit'].sum() else 0
        create_metric_card("Credit Utilization", f"{credit_utilization:.2f}%")
    with col7:
        delinquency_rate = (filtered_df[filtered_df['Delinquent_Acc'] == 1]['Client_Num'].nunique() / active_customers * 100) if active_customers else 0
        create_metric_card("Delinquency Rate", f"{delinquency_rate:.2f}%")
    with col8:
        interest_earned = filtered_df['Interest_Earned'].sum()
        create_metric_card("Interest Earned", f"${interest_earned:,.0f}")
    
    st.markdown("---")
    
    # Charts Section
    st.markdown('<div class="section-header">📈 Financial Analytics</div>', unsafe_allow_html=True)
    
    # Row 1: Time series and top categories
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced monthly trend
        monthly_trend = filtered_df.groupby('Month')['Total_Trans_Amt'].sum().reset_index()
        fig1 = px.line(
            monthly_trend, 
            x='Month', 
            y='Total_Trans_Amt',
            title='📈 Monthly Spending Trend',
            markers=True
        )
        fig1.update_layout(
            title_font_size=16,
            xaxis_title="Month",
            yaxis_title="Total Spending ($)",
            hovermode='x unified'
        )
        fig1.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Enhanced top categories
        top_categories = filtered_df.groupby('Exp Type')['Total_Trans_Amt'].sum().sort_values(ascending=False).reset_index()
        fig2 = px.bar(
            top_categories, 
            x='Total_Trans_Amt', 
            y='Exp Type',
            orientation='h',
            title='💰 Top Expense Categories',
            color='Total_Trans_Amt',
            color_continuous_scale='viridis'
        )
        fig2.update_layout(
            title_font_size=16,
            xaxis_title="Total Spending ($)",
            yaxis_title="Expense Type"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Row 2: Pie charts
    col3, col4 = st.columns(2)
    
    with col3:
        # Enhanced pie chart for card categories
        card_spending = filtered_df.groupby('Card_Category')['Total_Trans_Amt'].sum().reset_index()
        fig3 = px.pie(
            card_spending, 
            names='Card_Category', 
            values='Total_Trans_Amt', 
            title='💳 Spending by Card Category',
            hole=0.4  # Donut chart
        )
        fig3.update_layout(title_font_size=16)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # Enhanced channel analysis
        channel_spending = filtered_df.groupby('Use Chip')['Total_Trans_Amt'].sum().reset_index()
        fig4 = px.pie(
            channel_spending, 
            names='Use Chip', 
            values='Total_Trans_Amt', 
            title='🏪 Spending by Payment Channel',
            hole=0.4
        )
        fig4.update_layout(title_font_size=16)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Advanced Analytics Section
    st.markdown('<div class="section-header">🔍 Advanced Analytics</div>', unsafe_allow_html=True)
    
    # Tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["👥 Customer Analysis", "📊 Risk Assessment", "💹 Utilization Analysis"])
    
    with tab1:
        st.subheader("Customer-wise Performance")
        customer_table = filtered_df.groupby(['Client_Num', 'Is_Delinquent']).agg(
            Total_Spending=('Total_Trans_Amt', 'sum'),
            Number_of_Transactions=('Total_Trans_Ct', 'sum'),
            Avg_Utilization_Ratio=('Avg_Utilization_Ratio', 'mean'),
            Credit_Limit=('Credit_Limit', 'first'),
            Outstanding_Balance=('Total_Revolving_Bal', 'sum')
        ).reset_index()
        
        # Format the dataframe
        customer_table['Total_Spending'] = customer_table['Total_Spending'].round(2)
        customer_table['Avg_Utilization_Ratio'] = (customer_table['Avg_Utilization_Ratio'] * 100).round(2)
        
        st.dataframe(customer_table, use_container_width=True)
        
        # Download button
        csv = customer_table.to_csv(index=False)
        st.download_button(
            label="📥 Download Customer Data",
            data=csv,
            file_name='customer_analysis.csv',
            mime='text/csv'
        )
    
    with tab2:
        st.subheader("Risk Assessment Dashboard")
        
        # Delinquency analysis
        col1, col2 = st.columns(2)
        
        with col1:
            delinq_by_category = filtered_df.groupby(['Card_Category', 'Is_Delinquent']).size().reset_index(name='Count')
            fig_risk1 = px.bar(
                delinq_by_category, 
                x='Card_Category', 
                y='Count', 
                color='Is_Delinquent',
                title='Delinquency by Card Category',
                barmode='group'
            )
            st.plotly_chart(fig_risk1, use_container_width=True)
        
        with col2:
            # Risk score calculation (example)
            risk_data = filtered_df.groupby('Client_Num').agg({
                'Avg_Utilization_Ratio': 'mean',
                'Delinquent_Acc': 'max',
                'Total_Trans_Amt': 'sum'
            }).reset_index()
            
            fig_risk2 = px.scatter(
                risk_data, 
                x='Avg_Utilization_Ratio', 
                y='Total_Trans_Amt',
                color='Delinquent_Acc',
                title='Risk Profile: Utilization vs Spending',
                color_continuous_scale='RdYlBu_r'
            )
            st.plotly_chart(fig_risk2, use_container_width=True)
    
    with tab3:
        st.subheader("Credit Utilization Analysis")
        
        if st.checkbox("Show Detailed Utilization Analysis", value=True):
            fig5 = px.scatter(
                filtered_df, 
                x='Credit_Limit', 
                y='Avg_Utilization_Ratio', 
                color='Is_Delinquent',
                size='Total_Trans_Amt',
                title='Credit Limit vs Average Utilization Ratio',
                hover_data=['Client_Num', 'Card_Category']
            )
            fig5.update_layout(
                xaxis_title="Credit Limit ($)",
                yaxis_title="Average Utilization Ratio",
                title_font_size=16
            )
            st.plotly_chart(fig5, use_container_width=True)
            
            # Utilization distribution
            fig6 = px.histogram(
                filtered_df, 
                x='Avg_Utilization_Ratio', 
                nbins=30,
                title='Distribution of Credit Utilization Ratios',
                color_discrete_sequence=['#1f77b4']
            )
            st.plotly_chart(fig6, use_container_width=True)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea, #764ba2); 
                    border-radius: 10px; color: white; margin: 1rem 0;">
            <h4>📊 Credit Card Financial Dashboard</h4>
            <p style="margin: 0;">Built with Streamlit & Plotly | Enhanced UI Design</p>
            <small>Created for Portfolio & Interview Purposes</small>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()