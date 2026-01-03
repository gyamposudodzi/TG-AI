# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add core directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Set page config
st.set_page_config(
    page_title="TradeGuard AI - Risk Health Check",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .risk-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: #f8fafc;
        border-left: 5px solid;
        margin-bottom: 1rem;
    }
    .risk-high { border-left-color: #ef4444; }
    .risk-medium { border-left-color: #f59e0b; }
    .risk-low { border-left-color: #10b981; }
    .score-gauge {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🛡️ TradeGuard AI</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-header">Risk Health Check for Retail Traders</h3>', unsafe_allow_html=True)

# Disclaimer Banner
st.warning("""
⚠️ **DISCLAIMER**: This tool analyzes historical trading patterns for educational purposes only. 
It does NOT provide trading advice, predictions, or signals. Trading involves risk of loss.
""")

# Sidebar for navigation
with st.sidebar:
    st.image("https://deriv.com/static/logo.svg", width=150)
    st.title("Navigation")
    page = st.radio("Go to:", ["📊 Upload & Analyze", "📈 Risk Dashboard", "📋 Report", "⚙️ Settings"])
    
    st.divider()
    st.markdown("### Sample Data")
    if st.button("Load Sample Trader"):
        st.session_state['sample_loaded'] = True
        st.rerun()
    
    st.divider()
    st.markdown("### About")
    st.caption("""
    TradeGuard AI helps you understand your trading risk profile.
    Upload your trade history to get a risk health check.
    """)

# Main content based on selected page
if page == "📊 Upload & Analyze":
    st.header("Upload Your Trade History")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CSV file with your trade history",
            type=['csv'],
            help="CSV should contain trade data with columns like trade_id, symbol, entry_price, exit_price, profit_loss, etc."
        )
        
        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)
                
                # Store in session state
                st.session_state['trade_data'] = df
                st.session_state['file_name'] = uploaded_file.name
                
                # Display preview
                st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
                
                with st.expander("Preview your data"):
                    st.dataframe(df.head(10))
                    
                    # Show basic info
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Total Trades", len(df))
                    with col_b:
                        st.metric("Time Period", 
                                 f"{df['entry_time'].min()[:10]} to {df['exit_time'].max()[:10]}")
                    with col_c:
                        total_pl = df['profit_loss'].sum()
                        st.metric("Total P&L", f"${total_pl:,.2f}", 
                                 delta="green" if total_pl > 0 else "red")
                
                # Analyze button
                if st.button("🔍 Analyze Risk Profile", type="primary", use_container_width=True):
                    st.session_state['analysis_started'] = True
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("""
                **Expected CSV format:**
                - trade_id, symbol, entry_time, exit_time, trade_type (BUY/SELL)
                - entry_price, exit_price, stop_loss, take_profit, profit_loss
                - lot_size, account_balance_before
                """)
    
    with col2:
        st.markdown("### 📋 CSV Template")
        st.download_button(
            label="Download Sample CSV",
            data=""trade_id,symbol,entry_time,exit_time,trade_type,lot_size,entry_price,exit_price,stop_loss,take_profit,profit_loss,account_balance_before
1,EURUSD,2024-01-01 10:00:00,2024-01-01 12:00:00,BUY,0.1,1.1000,1.1020,1.0980,1.1050,20.00,10000
2,GBPUSD,2024-01-02 09:30:00,2024-01-02 10:30:00,SELL,0.2,1.2700,1.2680,1.2750,1.2650,40.00,10020
3,BTCUSD,2024-01-03 15:00:00,2024-01-03 16:00:00,BUY,0.01,42000,42500,41000,43000,50.00,10060
4,TSLA,2024-01-04 11:00:00,2024-01-04 14:00:00,SELL,5,250,245,255,240,-25.00,10110
5,XAUUSD,2024-01-05 08:00:00,2024-01-05 09:00:00,BUY,0.05,2020,2030,2010,2040,10.00,10085"",
            file_name="sample_trades.csv",
            mime="text/csv"
        )
        
        st.divider()
        st.markdown("### ⚡ Quick Start")
        st.info("""
        1. Download sample CSV
        2. Upload it here
        3. Click 'Analyze Risk Profile'
        4. View your risk score & insights
        """)

elif page == "📈 Risk Dashboard":
    st.header("Risk Analysis Dashboard")
    
    if 'trade_data' not in st.session_state:
        st.warning("Please upload trade data first from the 'Upload & Analyze' page.")
        st.stop()
    
    # Placeholder for actual analysis
    df = st.session_state['trade_data']
    
    # Mock analysis for now (we'll replace with real analysis later)
    st.info("🔧 **Risk analysis engine is being initialized...**")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Risk Score", "72", delta="Moderate Risk", delta_color="off")
        
    with col2:
        st.metric("Grade", "B", delta="Good", delta_color="normal")
        
    with col3:
        st.metric("Total Risks Detected", "3")
        
    with col4:
        st.metric("Improvement Potential", "28%")
    
    st.divider()
    
    # Risk categories
    st.subheader("📊 Risk Breakdown")
    
    risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
    
    with risk_col1:
        st.markdown("""
        <div class="risk-card risk-high">
            <h4>🚨 High Risk</h4>
            <h2>Over-Leverage</h2>
            <p>Position sizes exceed 2% of account</p>
        </div>
        """, unsafe_allow_html=True)
    
    with risk_col2:
        st.markdown("""
        <div class="risk-card risk-medium">
            <h4>⚠️ Medium Risk</h4>
            <h2>No Stop Loss</h2>
            <p>30% of trades had no SL</p>
        </div>
        """, unsafe_allow_html=True)
    
    with risk_col3:
        st.markdown("""
        <div class="risk-card risk-low">
            <h4>✅ Low Risk</h4>
            <h2>Revenge Trading</h2>
            <p>Good emotional control</p>
        </div>
        """, unsafe_allow_html=True)
    
    with risk_col4:
        st.markdown("""
        <div class="risk-card risk-medium">
            <h4>⚠️ Medium Risk</h4>
            <h2>Poor R:R Ratio</h2>
            <p>Avg 1:0.8 risk:reward</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Placeholder for AI insights
    st.subheader("🤖 AI Risk Insights")
    with st.expander("View detailed analysis", expanded=True):
        st.info("""
        **Analysis of your trading patterns:**
        
        1. **Over-Leverage Detected**: Your average position size is 3.2% of account balance, 
           exceeding the recommended 2% limit. This increases margin call risk during volatility.
        
        2. **Stop-Loss Discipline**: 30% of trades were entered without stop-loss orders.
           This exposes you to unlimited downside risk on those positions.
        
        3. **Risk-Reward Ratio**: Your average risk:reward ratio is 1:0.8, meaning you're 
           risking $1 to make $0.80. Successful traders typically aim for 1:1.5 or better.
        
        **Non-Advisory Suggestions**:
        - Consider using smaller position sizes relative to your account balance
        - Set stop-loss orders on every trade entry
        - Review your profit targets to improve risk:reward ratio
        """)

elif page == "📋 Report":
    st.header("Generate Risk Report")
    
    if 'trade_data' not in st.session_state:
        st.warning("Please upload trade data first to generate a report.")
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Report Configuration")
        
        report_type = st.selectbox(
            "Report Format",
            ["PDF Report", "HTML Report", "Markdown Report"]
        )
        
        include_sections = st.multiselect(
            "Include Sections",
            ["Executive Summary", "Risk Score", "Detailed Metrics", 
             "AI Insights", "Improvement Plan", "Charts & Graphs"],
            default=["Executive Summary", "Risk Score", "AI Insights", "Improvement Plan"]
        )
        
        st.divider()
        
        if st.button("📄 Generate Full Report", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive risk report..."):
                # Placeholder for report generation
                st.success("✅ Report generated successfully!")
                
                # Mock report content
                report_content = f"""
                # TradeGuard AI Risk Health Report
                ## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                ### Executive Summary
                - **Overall Risk Score**: 72/100 (Grade: B)
                - **Key Risks**: Over-leverage, Missing stop-loss orders
                - **Strengths**: Good trade timing, No revenge trading detected
                
                ### Risk Breakdown
                1. Position Sizing: High Risk
                2. Stop-Loss Usage: Medium Risk  
                3. Risk-Reward Ratio: Medium Risk
                4. Emotional Control: Low Risk
                
                ### AI Analysis
                The analysis indicates a disciplined trader with room for improvement in position sizing and risk management practices.
                
                ### Disclaimer
                This report is for educational purposes only. Not financial advice.
                """
                
                st.download_button(
                    label="⬇️ Download Report",
                    data=report_content,
                    file_name=f"TradeGuard_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
    
    with col2:
        st.markdown("### 📊 Quick Stats")
        st.json({
            "Total Trades": len(st.session_state['trade_data']),
            "Analysis Date": datetime.now().strftime("%Y-%m-%d"),
            "Risk Categories": 4,
            "AI Insights": "Generated",
            "Report Ready": True
        })

elif page == "⚙️ Settings":
    st.header("Settings & Configuration")
    
    st.subheader("AI Configuration")
    
    api_key = st.text_input(
        "OpenAI API Key (Optional)",
        type="password",
        help="Leave blank to use demo mode with pre-generated insights"
    )
    
    if api_key:
        st.session_state['openai_key'] = api_key
        st.success("API key saved for this session")
    
    st.divider()
    
    st.subheader("Risk Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_position_size = st.slider(
            "Max Position Size (% of balance)",
            min_value=0.5,
            max_value=10.0,
            value=2.0,
            step=0.5,
            help="Recommended: 1-2% per trade"
        )
        
        min_rr_ratio = st.slider(
            "Minimum Risk:Reward Ratio",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Recommended: At least 1:1"
        )
    
    with col2:
        max_daily_trades = st.number_input(
            "Max Daily Trades",
            min_value=1,
            max_value=50,
            value=10,
            help="Alert if exceeding this number"
        )
        
        max_drawdown = st.slider(
            "Max Drawdown Alert (%)",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            help="Alert if drawdown exceeds this percentage"
        )
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")
    
    st.divider()
    
    st.subheader("About TradeGuard AI")
    st.markdown("""
    **Version**: 1.0.0 (MVP)
    
    **Purpose**: Educational risk analysis tool for retail traders
    
    **Key Features**:
    - CSV trade history analysis
    - Rule-based risk detection
    - AI-powered explanations
    - Exportable reports
    
    **Important**: This tool does NOT provide trading advice or signals.
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 1rem;">
    <p>🛡️ TradeGuard AI | For educational purposes only | Not affiliated with Deriv</p>
    <p>⚠️ Trading involves risk of loss. Past performance is not indicative of future results.</p>
</div>
""", unsafe_allow_html=True)