import os
import json
from dotenv import load_dotenv
from google import genai
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def read_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def metric_extraction_agent(metric_extraction_prompt, startup_information, client):
    full_input = (
        f"{metric_extraction_prompt}\n\n"
        "Here is the startup summary data in JSON format:\n"
        f"{json.dumps(startup_information, indent=2)}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [{"text": full_input}]
            }
        ]
    )
    metrics_json_str = response.text
    try:
        metrics_json_obj = json.loads(metrics_json_str)
    except json.JSONDecodeError:
        st.warning("Model output could not be parsed as JSON. Showing synthetic data for demo.")
        metrics_json_obj = None
    return metrics_json_obj

def generate_synthetic_from_llm(llm_metrics):
    synthetic = {}
    rng = np.random.default_rng(seed=42)
    for k, v in llm_metrics.items():
        if isinstance(v, (int, float)):
            noise = rng.uniform(0.9, 1.1)
            synthetic[k] = round(v * noise, 2)
        elif isinstance(v, list) and all(isinstance(i, (int, float)) for i in v):
            synthetic[k] = [round(i * rng.uniform(0.9, 1.1), 2) for i in v]
        elif isinstance(v, dict) and all(isinstance(val, (int, float)) for val in v.values()):
            synthetic[k] = {kk: round(val * rng.uniform(0.9, 1.1), 2) for kk, val in v.items()}
        else:
            synthetic[k] = v
    return synthetic

def display_metrics(metrics, st):
    st.markdown("<h2 style='color:#1976d2'>📊 Startup Metrics Analysis</h2>", unsafe_allow_html=True)

    # If metrics is None, show synthetic demo data only
    if not metrics:
        st.info("No metrics available from the model. Showing synthetic data for demo.")
        # Synthetic data: metrics for Nario and Market
        data = {
            "Metric": ["Revenue ($K)", "Active Users", "Growth Rate (%)", "Retention (%)"],
            "Nario": [120, 1500, 35, 82],
            "Market": [90, 1800, 28, 88]
        }
        df = pd.DataFrame(data)
        # Pie chart data
        pie_data = pd.DataFrame({
            "Type": ["Nario", "Market"],
            "Users": [1500, 1800]
        })
        # Horizontal bar chart data
        bar_data = pd.DataFrame({
            "Type": ["Nario", "Market"],
            "Retention": [82, 88]
        })
        # Side by side plotly charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='color:#ff8f00'>User Distribution Pie Chart</h3>", unsafe_allow_html=True)
            fig_pie = px.pie(pie_data, names="Type", values="Users", title="Active Users by Type")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(legend_title="Type")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.markdown("<h3 style='color:#388e3c'>Retention Rate Bar Chart</h3>", unsafe_allow_html=True)
            fig_bar = px.bar(bar_data, x="Retention", y="Type", orientation='h', 
                             color="Type", title="Retention Rate (%) by Type")
            fig_bar.update_layout(legend_title="Type")
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("<h3 style='color:#388e3c'>Bar Chart Comparison</h3>", unsafe_allow_html=True)
        st.bar_chart(df.set_index("Metric"))
        months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
        revenue_trend = pd.DataFrame({
            "Month": months,
            "Nario": [20, 25, 30, 25, 10, 10],
            "Market": [15, 20, 20, 18, 8, 9]
        })
        revenue_trend = revenue_trend.set_index("Month")
        st.markdown("<h3 style='color:#ff8f00'>Trend Over 6 Months (Revenue)</h3>", unsafe_allow_html=True)
        st.line_chart(revenue_trend)
        st.success("Synthetic metrics visualized for demo!")
        return

    # If metrics is a dict, generate synthetic data based on the same keys/structure
    synthetic_metrics = generate_synthetic_from_llm(metrics)

    # --- PIE CHART: Let's try "Active Users" or whatever key fits ---
    pie_llm = None
    pie_syn = None
    pie_key = None
    for k, v in metrics.items():
        if isinstance(v, dict) and all(isinstance(val, (int, float)) for val in v.values()):
            pie_key = k
            # Remap keys to 'Nario' and 'Market' if only two items
            startups_llm = list(v.keys())
            startups_syn = list(synthetic_metrics[k].keys())
            if len(startups_llm) == 2:
                startups_llm = ["Nario", "Market"]
                startups_syn = ["Nario", "Market"]
            pie_llm = pd.DataFrame({"Type": startups_llm, "Users": list(v.values())})
            pie_syn = pd.DataFrame({"Type": startups_syn, "Users": list(synthetic_metrics[k].values())})
            break
    if pie_llm is None:
        for k, v in metrics.items():
            if isinstance(v, list) and all(isinstance(i, (int, float)) for i in v):
                pie_key = k
                pie_llm = pd.DataFrame({"Type": ["Nario", "Market"], "Users": v[:2]})
                pie_syn = pd.DataFrame({"Type": ["Nario", "Market"], "Users": synthetic_metrics[k][:2]})
                break

    # --- BAR CHART: Try another key of similar shape ---
    bar_llm = None
    bar_syn = None
    bar_key = None
    for k, v in metrics.items():
        if k != pie_key and isinstance(v, dict) and all(isinstance(val, (int, float)) for val in v.values()):
            bar_key = k
            startups_llm = list(v.keys())
            startups_syn = list(synthetic_metrics[k].keys())
            if len(startups_llm) == 2:
                startups_llm = ["Nario", "Market"]
                startups_syn = ["Nario", "Market"]
            bar_llm = pd.DataFrame({"Type": startups_llm, "Value": list(v.values())})
            bar_syn = pd.DataFrame({"Type": startups_syn, "Value": list(synthetic_metrics[k].values())})
            break
    if bar_llm is None:
        for k, v in metrics.items():
            if k != pie_key and isinstance(v, list) and all(isinstance(i, (int, float)) for i in v):
                bar_key = k
                bar_llm = pd.DataFrame({"Type": ["Nario", "Market"], "Value": v[:2]})
                bar_syn = pd.DataFrame({"Type": ["Nario", "Market"], "Value": synthetic_metrics[k][:2]})
                break

    # --- SIDE BY SIDE CHARTS ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<h3 style='color:#ff8f00'>{pie_key or 'Pie Chart'}: LLM vs Synthetic</h3>", unsafe_allow_html=True)
        if pie_llm is not None and pie_syn is not None:
            fig_pie_llm = px.pie(pie_llm, names="Type", values="Users", title=f"{pie_key} (LLM Generated)")
            fig_pie_llm.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie_llm.update_layout(legend_title="Type")
            fig_pie_syn = px.pie(pie_syn, names="Type", values="Users", title=f"{pie_key} (Synthetic)")
            fig_pie_syn.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie_syn.update_layout(legend_title="Type")
            st.plotly_chart(fig_pie_llm, use_container_width=True)
            st.plotly_chart(fig_pie_syn, use_container_width=True)
        else:
            st.info("No suitable pie chart data found.")

    with col2:
        st.markdown(f"<h3 style='color:#388e3c'>{bar_key or 'Bar Chart'}: LLM vs Synthetic</h3>", unsafe_allow_html=True)
        if bar_llm is not None and bar_syn is not None:
            fig_bar_llm = px.bar(bar_llm, x="Value", y="Type", orientation='h', color="Type", title=f"{bar_key} (LLM)")
            fig_bar_llm.update_layout(legend_title="Type")
            fig_bar_syn = px.bar(bar_syn, x="Value", y="Type", orientation='h', color="Type", title=f"{bar_key} (Synthetic)")
            fig_bar_syn.update_layout(legend_title="Type")
            st.plotly_chart(fig_bar_llm, use_container_width=True)
            st.plotly_chart(fig_bar_syn, use_container_width=True)
        else:
            st.info("No suitable bar chart data found.")

    # --- LINE CHART: Show LLM vs Synthetic for a list metric if available ---
    for k, v in metrics.items():
        if isinstance(v, list) and all(isinstance(i, (int, float)) for i in v):
            st.markdown(f"<h3 style='color:#ff8f00'>Trend Comparison: {k} (LLM vs Synthetic)</h3>", unsafe_allow_html=True)
            trend_df = pd.DataFrame({
                "Index": list(range(len(v))),
                "LLM": v,
                "Synthetic": synthetic_metrics[k]
            })
            trend_df = trend_df.set_index("Index")
            st.line_chart(trend_df)
            break

    # --- Display raw metrics ---
    st.markdown("<h3 style='color:#388e3c'>Raw Metrics (LLM and Synthetic)</h3>", unsafe_allow_html=True)
    st.json({"LLM": metrics, "Synthetic": synthetic_metrics})

def metric_generation_agent():
    load_dotenv()
    client = genai.Client()
    current_directory = os.getcwd()
    prompts_path = os.path.join(current_directory, "config/prompt")
    metric_prompt_path = os.path.join(prompts_path, "metric_generation.md")
    file_path = "C:\\Agent GCP\\all_extracted_data.json"

    with open(metric_prompt_path, "r", encoding='utf-8') as file:
        metric_extraction_prompt = file.read()
    startup_information = read_data(file_path)

    st.markdown("<h1 style='color:#1976d2;'>📊 Metric Generation & Visualization</h1>", unsafe_allow_html=True)
    st.markdown("<span style='color:#388e3c'>Extract and visualize startup metrics. If unavailable, synthetic data will be shown.</span>", unsafe_allow_html=True)

    if st.button("Generate and Show Metrics", key="metrics_btn"):
        metrics = metric_extraction_agent(metric_extraction_prompt, startup_information, client)
        display_metrics(metrics, st)