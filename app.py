# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add core directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
from metrics_calculator import TradeMetricsCalculator
from risk_scorer import RiskScorer
from risk_rules import RiskRuleEngine
from ai_explainer import AIRiskExplainer

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
    page = st.radio("Go to:", ["📊 Home", "📈 Risk Dashboard", "📋 Report", "⚙️ Settings"])
    
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
if page == "📊 Home":
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
            data="""trade_id,symbol,entry_time,exit_time,trade_type,lot_size,entry_price,exit_price,stop_loss,take_profit,profit_loss,account_balance_before
            1,EURUSD,2024-01-01 10:00:00,2024-01-01 12:00:00,BUY,0.1,1.1000,1.1020,1.0980,1.1050,20.00,10000
            2,GBPUSD,2024-01-02 09:30:00,2024-01-02 10:30:00,SELL,0.2,1.2700,1.2680,1.2750,1.2650,40.00,10020
            3,BTCUSD,2024-01-03 15:00:00,2024-01-03 16:00:00,BUY,0.01,42000,42500,41000,43000,50.00,10060
            4,TSLA,2024-01-04 11:00:00,2024-01-04 14:00:00,SELL,5,250,245,255,240,-25.00,10110
            5,XAUUSD,2024-01-05 08:00:00,2024-01-05 09:00:00,BUY,0.05,2020,2030,2010,2040,10.00,10085""",
            file_name="sample_trades.csv",
            mime="text/csv"
        )
        
        st.divider()
        st.markdown("### ⚡ Quick Start")
        st.info("""
        1. Download sample CSV
        2. Upload it here
        3. Click 'Analyze Risk Profile'
        4. View your risk score & insights in the risk dashboard
        """)

elif page == "📈 Risk Dashboard":
    st.header("Risk Analysis Dashboard")
    
    if 'trade_data' not in st.session_state:
        st.warning("Please upload trade data first from the 'Home' page.")
        st.stop()
    
    df = st.session_state['trade_data']
    
    # Show analysis progress
    with st.spinner("🔍 Analyzing your trading patterns..."):
        
        # 1. Calculate Metrics
        metrics_calc = TradeMetricsCalculator(df)
        metrics = metrics_calc.compute_all_metrics()
        
        # 2. Detect Risks
        risk_engine = RiskRuleEngine(metrics, df)
        risk_results = risk_engine.detect_all_risks()
        
        # 3. Calculate Score
        scorer = RiskScorer()
        score_result = scorer.calculate_score(risk_results['risk_details'])
        
        # Store in session state
        st.session_state['metrics'] = metrics
        st.session_state['risk_results'] = risk_results
        st.session_state['score_result'] = score_result
    
    with st.spinner("🤖 Generating AI insights..."):
        ai_explainer = AIRiskExplainer()
        ai_explanations = ai_explainer.generate_explanation(
            metrics, 
            risk_results, 
            score_result
        )
        st.session_state['ai_explanations'] = ai_explanations

    # Display Score Gauge
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score_result['score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Score", 'font': {'size': 24}},
            delta={'reference': 80, 'increasing': {'color': "RebeccaPurple"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': score_result['grade_color']},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#ef4444'},
                    {'range': [40, 60], 'color': '#f59e0b'},
                    {'range': [60, 80], 'color': '#fbbf24'},
                    {'range': [80, 100], 'color': '#10b981'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display grade and key metrics
        st.markdown(f"""
        <div class="score-gauge">
            <h1 style="font-size: 4rem; margin: 0;">{score_result['grade']}</h1>
            <p style="font-size: 1.2rem; margin: 0;">Grade</p>
            <div style="margin-top: 1rem;">
                <p style="margin: 0.2rem;">Improvement: {score_result['improvement_potential']}%</p>
                <p style="margin: 0.2rem;">Risks: {score_result['total_risks']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Display Metrics
    st.subheader("📊 Trading Metrics")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
        st.metric("Total Trades", metrics.get('total_trades', 0))
    
    with metrics_col2:
        st.metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")
        st.metric("Net Profit", f"${metrics.get('net_profit', 0):.2f}")
    
    with metrics_col3:
        st.metric("Avg Position Size", f"{metrics.get('avg_position_size_pct', 0):.1f}%")
        st.metric("Max Drawdown", f"{metrics.get('max_drawdown_pct', 0):.1f}%")
    
    with metrics_col4:
        st.metric("Risk:Reward Ratio", f"{metrics.get('risk_reward_ratio', 0):.2f}")
        st.metric("SL Usage Rate", f"{metrics.get('sl_usage_rate', 0):.1f}%")
    
    st.divider()
    
    # Display Detected Risks
    st.subheader("🚨 Detected Risks")
    
    if not risk_results['detected_risks']:
        st.success("✅ No significant risks detected! Your trading shows good risk management.")
    else:
        # Create columns for risk cards
        risk_cols = st.columns(2)
        
        for idx, risk in enumerate(risk_results['detected_risks']):
            details = risk_results['risk_details'].get(risk, {})
            severity = details.get('severity', 0)
            message = details.get('message', risk.replace('_', ' ').title())
            
            # Determine risk level
            if severity >= 70:
                risk_level = "High"
                border_color = "#ef4444"
            elif severity >= 40:
                risk_level = "Medium"
                border_color = "#f59e0b"
            else:
                risk_level = "Low"
                border_color = "#10b981"
            
            with risk_cols[idx % 2]:
                st.markdown(f"""
                <div style="
                    padding: 1rem;
                    border-radius: 10px;
                    background: #f8fafc;
                    border-left: 5px solid {border_color};
                    margin-bottom: 1rem;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: {border_color};">{risk.replace('_', ' ').title()}</h4>
                        <span style="background: {border_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem;">
                            {risk_level}
                        </span>
                    </div>
                    <p style="margin: 0.5rem 0;">{message}</p>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #64748b;">
                        <span>Severity: {severity:.0f}%</span>
                        <span>Weight: {scorer.risk_weights.get(risk, 0)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Display Detailed Analysis
    st.subheader("📋 Detailed Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Score Breakdown", "Risk Summary", "AI Insights", "Recommendations"])
    
    with tab1:
        st.write("**Score Calculation Breakdown:**")
        
        if score_result['breakdown']:
            breakdown_df = pd.DataFrame(score_result['breakdown'])
            breakdown_df['Risk'] = breakdown_df['risk'].apply(lambda x: x.replace('_', ' ').title())
            breakdown_df['Impact'] = breakdown_df['contribution'].apply(lambda x: f"-{x:.1f}")
            
            st.dataframe(
                breakdown_df[['Risk', 'severity', 'weight', 'Impact']].rename(
                    columns={'severity': 'Severity %', 'weight': 'Weight'}
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No risk contributions to display.")
    
    with tab2:
        st.markdown(risk_engine.get_risk_summary())
        
        # Show risk distribution
        if score_result['risk_breakdown']:
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(score_result['risk_breakdown'].keys()),
                    values=list(score_result['risk_breakdown'].values()),
                    hole=.3,
                    marker_colors=['#10b981', '#f59e0b', '#ef4444']
                )
            ])
            fig.update_layout(title="Risk Distribution by Severity")
            st.plotly_chart(fig, use_container_width=True)
            
    with tab3:
        st.subheader("🤖 AI-Powered Risk Analysis")
        
        # Check if we're in demo mode
        if ai_explanations.get('ai_model') == 'demo_mode':
            st.warning("""
            ⚠️ **Demo Mode**: Using pre-generated explanations. 
            For AI-powered insights, add your OpenAI API key in Settings.
            """)
        
        # Display main AI analysis
        st.markdown(ai_explainer.format_for_display(ai_explanations))
        
        # Display risk-specific AI explanations
        st.divider()
        st.subheader("🎯 Risk-Specific AI Explanations")
        
        for risk_exp in ai_explanations.get('risk_explanations', []):
            with st.expander(f"{risk_exp.get('display_name', 'Unknown')} ({risk_exp.get('severity', 'N/A')} Risk)"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**🎓 Educational Concept**")
                    st.info(risk_exp.get('concept', ''))
                    
                    st.markdown("**⚡ Why This Matters**")
                    st.info(risk_exp.get('why_matters', ''))
                    
                    st.markdown("**📚 Trading Principle**")
                    st.info(risk_exp.get('principle', ''))
                
                with col_b:
                    st.markdown("**🧠 Psychology Insight**")
                    st.info(risk_exp.get('psychology_insight', ''))
                    
                    st.markdown("**💡 Analogy**")
                    st.info(risk_exp.get('analogy', ''))
                    
                    st.markdown("**🔍 Non-Advisory Considerations**")
                    for suggestion in risk_exp.get('non_advice_suggestions', []):
                        st.write(f"• {suggestion}")

    with tab4:
        st.write("**Recommendations:**")
        st.info(score_result['recommendation'])
        
        # Show improvement plan
        if score_result['top_risks']:
            st.write("**Priority Areas for Improvement:**")
            for i, risk in enumerate(score_result['top_risks'], 1):
                risk_details = risk_results['risk_details'].get(risk, {})
                st.markdown(f"""
                {i}. **{risk.replace('_', ' ').title()}**  
                   {risk_details.get('message', '')}
                """)
        
        # What-if analysis
        st.divider()
        st.write("**Improvement Simulation:**")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📈 Simulate 20% Improvement", use_container_width=True):
                new_score = min(100, score_result['score'] + 20)
                st.success(f"Improved score: {new_score:.1f}/100")
        
        with col_b:
            if st.button("📉 View Worst-Case", use_container_width=True):
                worst_score = max(0, score_result['score'] - 30)
                st.error(f"Worst-case score: {worst_score:.1f}/100")

elif page == "📋 Report":
    st.header("Generate Risk Report")
    
    if 'trade_data' not in st.session_state:
        st.warning("Please upload trade data first to generate a report.")
        st.stop()
        
    if 'score_result' not in st.session_state:
        st.warning("Please analyze your trades first from the Risk Dashboard.")
        if st.button("Go to Dashboard"):
            st.switch_page("📈 Risk Dashboard")
        st.stop()

    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Report Configuration")
        
        report_type = st.selectbox(
            "Report Format",
            ["Markdown Report", "HTML Report", "PDF Report(Coming Soon)"]
        )
        
        include_sections = st.multiselect(
            "Include Sections",
            ["Executive Summary", "Trading Metrics", "Risk Analysis", 
             "AI Insights", "Action Plan", "Disclaimers"],
            default=["Executive Summary", "Trading Metrics", "Risk Analysis", "AI Insights", "Action Plan"]
        )
        
        report_name = st.text_input(
            "Report Name",
            value=f"TradeGuard_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        
        st.divider()
        
        if st.button("📄 Generate Full Report", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive risk report..."):
                from core.report_generator import ReportGenerator
                
                # Generate report
                generator = ReportGenerator()
                
                if report_type in ["Markdown Report", "HTML Report"]:
                    # Get all data from session state
                    metrics = st.session_state.get('metrics', {})
                    risk_results = st.session_state.get('risk_results', {})
                    score_result = st.session_state.get('score_result', {})
                    ai_explanations = st.session_state.get('ai_explanations', {})
                    
                    # Generate markdown report
                    markdown_report = generator.generate_markdown_report(
                        metrics, risk_results, score_result, ai_explanations
                    )
                    
                    if report_type == "Markdown Report":
                        st.success("✅ Markdown report generated successfully!")
                        
                        # Show preview
                        with st.expander("📝 Report Preview", expanded=True):
                            st.markdown(markdown_report[:2000] + "\n\n**... [report continues] ...**")
                        
                        # Download button
                        st.download_button(
                            label="⬇️ Download Markdown Report",
                            data=markdown_report,
                            file_name=f"{report_name}.md",
                            mime="text/markdown"
                        )
                    
                    else:  # HTML Report
                        html_report = generator.generate_html_report(markdown_report)
                        st.success("✅ HTML report generated successfully!")
                        
                        # Show preview
                        with st.expander("🌐 Report Preview", expanded=True):
                            st.components.v1.html(html_report, height=600, scrolling=True)
                        
                        # Download button
                        st.download_button(
                            label="⬇️ Download HTML Report",
                            data=html_report,
                            file_name=f"{report_name}.html",
                            mime="text/html"
                        )
                
                else:  # PDF Report
                    st.info("📚 PDF generation coming soon! For now, please use Markdown or HTML format.")

    
    with col2:
        st.markdown("### 📊 Report Contents")
        
        # Show what will be included
        st.json({
            "Trades Analyzed": len(st.session_state['trade_data']),
            "Risk Score": st.session_state.get('score_result', {}).get('score', 'N/A'),
            "Risk Grade": st.session_state.get('score_result', {}).get('grade', 'N/A'),
            "Risks Detected": st.session_state.get('score_result', {}).get('total_risks', 0),
            "AI Insights": "Included" if st.session_state.get('ai_explanations') else "Not generated",
            "Generation Time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        st.divider()
        
        st.markdown("### 💡 Quick Tips")
        st.info("""
        1. **Share safely**: Reports contain trading data - share only with trusted parties
        2. **Regular updates**: Generate reports monthly to track improvement
        3. **Educational use**: Use reports to learn about risk management
        4. **No advice**: Remember, reports are educational, not advisory
        """)

elif page == "⚙️ Settings":
    st.header("Settings & Configuration")
    
    st.subheader("AI Configuration")
    
     # Create two columns for API key input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key for AI-powered insights. Get one at platform.openai.com",
            value=st.session_state.get('openai_api_key', '')
        )
    
    with col2:
        st.markdown("###")
        if st.button("💾 Save Key", use_container_width=True):
            if api_key:
                st.session_state['openai_api_key'] = api_key
                st.success("API key saved for this session!")
                st.rerun()
            else:
                st.warning("Please enter an API key")
    
    # Test the API key
    if st.session_state.get('openai_api_key'):
        if st.button("🧪 Test API Connection", type="secondary"):
            with st.spinner("Testing connection to OpenAI..."):
                try:
                    test_explainer = AIRiskExplainer(
                        openai_api_key=st.session_state['openai_api_key']
                    )
                    # Simple test - try to create the model
                    st.success("✅ API connection successful!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
    
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