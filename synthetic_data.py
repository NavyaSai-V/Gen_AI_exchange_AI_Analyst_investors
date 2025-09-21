import streamlit as st
import pandas as pd

def display_synthetic_metrics():
    st.markdown("<h2 style='color:#1976d2'>📊 Startup Metrics Comparison</h2>", unsafe_allow_html=True)
    
    # Synthetic data: metrics for two startups or periods
    data = {
        "Metric": ["Revenue ($K)", "Active Users", "Growth Rate (%)", "Retention (%)"],
        "Startup A": [120, 1500, 35, 82],
        "Startup B": [90, 1800, 28, 88]
    }
    df = pd.DataFrame(data)
    
    # Bar chart for side-by-side comparison
    st.markdown("<h3 style='color:#388e3c'>Bar Chart Comparison</h3>", unsafe_allow_html=True)
    st.bar_chart(df.set_index("Metric"))
    
    # Line chart for trend comparison
    st.markdown("<h3 style='color:#ff8f00'>Trend Over 6 Months (Revenue)</h3>", unsafe_allow_html=True)
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
    revenue_trend = pd.DataFrame({
        "Month": months,
        "Startup A": [20, 25, 30, 25, 10, 10],
        "Startup B": [15, 20, 20, 18, 8, 9]
    })
    revenue_trend = revenue_trend.set_index("Month")
    st.line_chart(revenue_trend)

    st.success("Synthetic metrics visualized for demo!")

def synthetic_data():
    st.markdown("<h1 style='color:#d32f2f;'>🚀 Synthetic Deal Notes & Metrics Demo</h1>", unsafe_allow_html=True)
    st.markdown("<span style='color:#388e3c'>Below is synthetic data for demonstration purposes.</span>", unsafe_allow_html=True)
    display_synthetic_metrics()

