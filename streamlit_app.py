import streamlit as st
from deal_notes_generation import (
    read_docx, save_to_docx, read_data, display_deal_notes, generate_deal_notes
)
from metric_generation_agent import (
    metric_extraction_agent, display_metrics
)
import os
from dotenv import load_dotenv
from google import genai

def main():
    load_dotenv()
    client = genai.Client()
    current_directory = os.getcwd()
    prompts_path = os.path.join(current_directory, "config/prompt")
    deal_notes_prompt_path = os.path.join(prompts_path, "deal_notes_generation.md")
    metric_prompt_path = os.path.join(prompts_path, "metric_generation.md")
    file_path = "all_extracted_data.json"
    docx_path = "deal_notes_generation.docx"

    with open(deal_notes_prompt_path, "r", encoding='utf-8') as file:
        deal_notes_prompt = file.read()
    with open(metric_prompt_path, "r", encoding='utf-8') as file:
        metric_extraction_prompt = file.read()
    startup_information = read_data(file_path)

    st.markdown("<h1 style='color:#d32f2f;'>🚀 Startup Deal Notes & Metrics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<span style='color:#388e3c'>Generate and review your deal notes and metrics with colorful, sectioned analysis and interactive graphs.</span>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Deal Notes", "Metrics"])

    with tab1:
        st.subheader("Deal Notes Generation and Review")
        if st.button("Generate and Show Deal Notes", key="deal_notes_btn"):
            summary = generate_deal_notes(deal_notes_prompt, startup_information, client)
            if summary is None:
                st.warning("No deal notes could be generated. Please check your prompt or model response.")
            else:
                save_to_docx(summary, docx_path)
                notes = read_docx(docx_path)
                display_deal_notes(notes, st)

        if os.path.exists(docx_path):
            with open(docx_path, "rb") as f:
                st.download_button("Download Deal Notes DOCX", f, file_name="deal_notes_generation.docx")

    with tab2:
        st.subheader("Metric Extraction and Visualization")
        if st.button("Generate and Show Metrics", key="metrics_btn"):
            metrics = metric_extraction_agent(metric_extraction_prompt, startup_information, client)
            display_metrics(metrics,st)

if __name__ == "__main__":
    main()