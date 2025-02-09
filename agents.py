import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import time
import random

# --- Gemini API Setup ---
genai.configure(api_key='AIzaSyB9ZnGupol-xHM9Yt_XCkQHXUMB7DHYLmk')


generation_config = {
    "temperature": 0.7,  # Lower temperature for more factual output
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,  # Increased for potentially large tables
}

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
)

# --- Utility Functions ---

def call_gemini_with_retry(model, prompt, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            st.error(f"Error calling Gemini API: {e}")
            retries += 1
            wait_time = 2 ** retries + random.uniform(0, 1)  # Exponential backoff
            time.sleep(wait_time)

    st.error("Failed Gemini API call after multiple retries.")
    return None

def get_competitor_analysis(company_name, industry, geographic_focus=None, specific_product=None):
    prompt = f"""
You are a highly skilled competitor analyst. Your task is to identify and analyze the main competitors of a given company, presenting your findings in a tabular format.

**Input:**
*   **Company Name:** {company_name}
*   **Industry:** {industry}
*   **Optional - Geographic Focus (if any):** {geographic_focus or "Not specified"}
*   **Optional - Specific Product/Service (if any):** {specific_product or "Not specified"}

**Output:**

1. **Competitor Identification Table:**

    *   Create a table listing the top 5-7 direct competitors.
    *   Include columns for:
        *   **Competitor Name**
        *   **Reason for Competition:** (Briefly explain why each company is a competitor)

2. **Competitor Analysis Table:**

    *   Create a comprehensive table comparing the competitors across various aspects.
    *   Include columns for:
        *   **Competitor Name**
        *   **Company Overview:** (Brief description, size, market position)
        *   **Product/Service:** (Key offerings, features, pricing - if available)
        *   **Strengths**
        *   **Weaknesses**
        *   **Marketing/Sales Strategy** (Channels, messaging)
        *   **Recent News/Developments**

3. **Overall Competitive Landscape:**

    *   Provide a brief summary (in a few bullet points or a short paragraph) of the overall competitive landscape in the given industry and the input company's position within it. 
"""
    response = call_gemini_with_retry(model, prompt)
    return response

# --- Streamlit App ---
st.title("Competitor Analysis Tool")

st.sidebar.header("Input Parameters")
company_name = st.sidebar.text_input("Company Name")
industry = st.sidebar.text_input("Industry")
geographic_focus = st.sidebar.text_input("Geographic Focus (Optional)")
specific_product = st.sidebar.text_input("Specific Product/Service (Optional)")

if st.sidebar.button("Get Analysis"):
    if not company_name or not industry:
        st.error("Please provide both the Company Name and Industry.")
    else:
        with st.spinner("Generating analysis... this may take a moment"):
            result = get_competitor_analysis(company_name, industry, geographic_focus, specific_product)

        if result:
            st.markdown(result, unsafe_allow_html=True)
        else:
            st.error("Failed to retrieve competitor analysis. Please try again later.")

st.sidebar.info("This tool uses the Gemini AI API to provide insights.")

