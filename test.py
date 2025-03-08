import streamlit as st
import google.generativeai as genai
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import numpy as np
from newspaper import Article
import concurrent.futures
import re
import plotly.express as px
from difflib import get_close_matches
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
data_path = "GemDataEXTR"  # Adjust this path to where your data files are stored

# Configure page settings
st.set_page_config(page_title="Global Economic Analysis Agent", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

# Enhanced CSS styling
st.markdown("""
<style>
    .analysis-container { border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; background-color: #fff; margin-bottom: 20px; }
    .analysis-header { font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #1f2937; }
    .analysis-content { line-height: 1.6; color: #374151; }
    .footer { text-align: center; padding: 10px; color: #6b7280; font-size: 14px; }
    .footer a { color: #3b82f6; text-decoration: none; }
    .footer a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# App header with timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<h1>🌍 Global Economic Analysis Agent</h1>
<p style='text-align: center; color: #6b7280;'>Last Updated: {current_time}</p>
""", unsafe_allow_html=True)

# Country normalization functions
def normalize_country(text):
    return "".join(ch for ch in text.lower() if ch.isalnum())

def get_matching_country(country, country_list):
    norm_input = normalize_country(country)
    country_variants = {
        "us": "United States", "usa": "United States", "unitedstatesofamerica": "United States",
        "u.s.a": "United States", "unitedstates": "United States", "uk": "United Kingdom", "u.k.": "United Kingdom"
    }
    normalized_variants = {normalize_country(k): v for k, v in country_variants.items()}
    if norm_input in normalized_variants:
        return normalized_variants[norm_input]
    normalized_list = [normalize_country(name) for name in country_list]
    matches = get_close_matches(norm_input, normalized_list, n=1, cutoff=0.6)
    if matches:
        for official in country_list:
            if normalize_country(official) == matches[0]:
                return official
    return None

# Data loading function
def load_data(file_path, sheet_name, country, indicator_name):
    try:
        logging.info(f"Loading data from {file_path} ({sheet_name}) for {country}")
        xls = pd.ExcelFile(file_path)
        if sheet_name not in xls.sheet_names:
            logging.error(f"Worksheet '{sheet_name}' not found in {file_path}. Available: {xls.sheet_names}")
            return None
        df = pd.read_excel(xls, sheet_name=sheet_name).dropna(how="all")
        df.columns = df.columns.str.strip()
        if 'Unnamed: 0' not in df.columns:
            logging.error("Expected 'Unnamed: 0' column for years not found.")
            return None
        df.rename(columns={"Unnamed: 0": "Year"}, inplace=True)
        matched_country = get_matching_country(country, df.columns)
        if not matched_country:
            logging.error(f"{indicator_name} data not found for {country}. Available: {df.columns[1:].tolist()}")
            return None
        try:
            data = df[["Year", matched_country]].dropna()
        except KeyError:
            return None
        data.columns = ["Year", indicator_name]
        if sheet_name == "monthly":
            data["Year"] = data["Year"].apply(
                lambda x: pd.to_datetime(x.replace("M", "-"), format='%Y-%m') if isinstance(x, str) else x
            )
        else:
            data["Year"] = data["Year"].astype(int)
        return data
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return None

# Compute data summary for inclusion in the prompt
def compute_data_summary(data, indicator_name):
    if data is None or data.empty:
        return f"{indicator_name}: Data not available"
    latest_data = data.iloc[-1]
    latest_value = latest_data[indicator_name]
    latest_year = latest_data["Year"]
    yoy_change = ((latest_value - data.iloc[-2][indicator_name]) / data.iloc[-2][indicator_name]) * 100 if len(data) >= 2 and data.iloc[-2][indicator_name] != 0 else np.nan
    five_year_avg = data.tail(5)[indicator_name].mean()
    trend = "increasing" if yoy_change > 0 else "decreasing" if yoy_change < 0 else "stable"
    return f"{indicator_name}: Latest ({latest_year}): {latest_value:.2f}, YoY change: {yoy_change:.2f}%, 5-yr avg: {five_year_avg:.2f}, Trend: {trend}"

# Plot graph with source annotation
def plot_graph(data, indicator_name, country):
    if data is not None:
        title = f"{indicator_name} Trend for {country}"
        fig = px.line(data, x="Year", y=indicator_name, title=title)
        fig.update_traces(mode="lines+markers")
        fig.add_annotation(
            text="Source: World Bank",
            xref="paper", yref="paper", x=0, y=-0.1, showarrow=False, font=dict(size=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Data not available for {indicator_name} in {country}.")

# News fetching functions
def fetch_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text, article.summary
    except Exception:
        return "Could not fetch article details.", "No summary available"

def fetch_news_from_url(url, query, headers):
    news_items = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.select('div.SoaBEf') or soup.select('div.Gx5Zad') or soup.select('g-card')
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_article = {}
            for article in articles:
                title_elem = article.select_one('.vvjwJb') or article.select_one('.n0jPhd') or article.select_one('.mCBkyc')
                link_elem = article.select_one('a')
                metadata_elem = article.select_one('.UPmit') or article.select_one('.LfVVr') or article.select_one('.CEMjEf')
                time_elem = article.select_one('time') or article.select_one('.ZE0LJd') or article.select_one('.jJzYv')
                summary_elem = article.select_one('.GI74Re') or article.select_one('.VwiC3b') or article.select_one('.s3v9rd')
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href', '')
                    source = metadata_elem.get_text().strip() if metadata_elem else "News Source"
                    published_time = time_elem.get_text().strip() if time_elem else "Recent"
                    summary = summary_elem.get_text().strip() if summary_elem else "No summary available"
                    if url:
                        future = executor.submit(fetch_article_content, url)
                        future_to_article[future] = {
                            'index': len(news_items), 'title': title, 'source': source, 'time': published_time,
                            'summary': summary, 'url': url, 'query': query
                        }
                        news_items.append(None)
            for future in concurrent.futures.as_completed(future_to_article):
                article_data = future_to_article[future]
                article_index = article_data['index']
                full_text, full_summary = future.result()
                if article_index < len(news_items):
                    news_items[article_index] = {**article_data, 'full_text': full_text, 'full_summary': full_summary}
        return news_items
    except Exception:
        return []

def fetch_economic_news(country, num_articles=10):
    try:
        base_url = "https://www.google.com/search?q="
        search_queries = [
            f"{country}+economy+financial+news", f"{country}+economic+outlook", f"{country}+financial+stability",
            f"{country}+economic+indicators", f"{country}+fiscal+policy", f"{country}+monetary+policy",
            f"{country}+trade+balance", f"{country}+inflation+rate", f"{country}+interest+rates",
            f"{country}+unemployment+rate", f"{country}+consumer+confidence", f"{country}+business+sentiment",
            f"{country}+bond+market+news", f"{country}+stock+market+news", f"{country}+yield+curve+news",
            f"{country}+exchange+rate+news", f"{country}+economic+growth+news", f"{country}+sovereign+debt+news",
            f"{country}+credit+rating+news", f"{country}+banking+sector+news"
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8"
        }
        all_news_items = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_articles = {executor.submit(fetch_news_from_url, f"{base_url}{query}&tbm=nws", query, headers): query for query in search_queries}
            for future in concurrent.futures.as_completed(future_to_articles):
                all_news_items.extend(future.result())
        gdp_news_items = [item for item in all_news_items if any(keyword.lower() in item['full_text'].lower() for keyword in ["GDP", "growth rate", "economic growth", "GDP growth", "percent growth", "% growth", "gdp percentage", "growth percentage"])]
        bond_news_items = [item for item in all_news_items if "bond" in item['query'].lower()]
        stock_news_items = [item for item in all_news_items if "stock" in item['query'].lower()]
        yield_news_items = [item for item in all_news_items if "yield" in item['query'].lower()]
        other_news_items = [item for item in all_news_items if item not in gdp_news_items + bond_news_items + stock_news_items + yield_news_items]
        combined_news_items = (
            gdp_news_items[:num_articles] + bond_news_items[:num_articles] + stock_news_items[:num_articles] +
            yield_news_items[:num_articles] + other_news_items[:max(0, num_articles - len(gdp_news_items) - len(bond_news_items) - len(stock_news_items) - len(yield_news_items))]
        )
        return combined_news_items
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

# Analysis prompt
def get_analysis_prompt(country, news_items, data_summaries):
    news_summary_list = [f"{i + 1}. {item['summary']} (Source: {item['source']}, Published: {item['time']})" for i, item in enumerate(news_items)] if news_items else ["No recent news available."]
    news_summary = "\n".join(news_summary_list)
    data_summary_text = "\n".join(data_summaries)
    return f"""
You are a senior economic analyst providing a comprehensive economic analysis for {country}.

Incorporate the following latest economic, bond market, stock market, and yield curve news headlines and summaries in your analysis:

{news_summary}

Additionally, consider the following key economic indicators data:

{data_summary_text}

**Important: Do not include a "References" or "Bibliography" section in your analysis text. A references section will be added programmatically.**

Provide a detailed analysis covering:

**Executive Summary:** Briefly summarize the current economic situation, key challenges, and outlook.

**Macroeconomic Indicators:** Analyze key macroeconomic indicators such as GDP growth, inflation, unemployment, interest rates, and exchange rates. Provide current figures and trends.

**Sector Analysis:** Examine the performance of key economic sectors (e.g., manufacturing, services, agriculture, technology).

**Policy Environment:** Discuss relevant government policies and regulations impacting the economy.

**Financial Market Analysis:** Analyze the current conditions of the bond market, stock market, and yield curve.

**Risks and Opportunities:** Identify potential economic risks and opportunities for growth.

**Economic Outlook:** Provide a forward-looking perspective on the country's economic prospects for the next 1-3 years.

Format the report in markdown with clear headers and subheaders. Be concise and data-driven. Highlight key findings using bold or italic text. When referencing news items, use superscript bracketed numbers like [1], [2], etc., corresponding to the news items listed above. Aim for a detailed output.
"""

# Sidebar configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        genai.configure(api_key=api_key)
        st.success("API Key set successfully!", icon="✅")
        st.markdown("### 🔧 Advanced Settings")
        model_options = ["gemini-2.0-flash"]  # Update with actual model name if different
        selected_model = st.selectbox("Model Version", model_options, index=0, help="Select the Gemini model version")
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, help="Adjust creativity level")
        max_tokens = st.select_slider("Output Length", options=[4096, 8192, 16384, 32768], value=8192, help="Maximum length of the generated analysis")
    else:
        st.warning("Please enter your Gemini API Key to use the analysis features.")

# Main content area
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 🔍 Country Analysis")
    country_name = st.text_input("", placeholder="Enter country name (e.g., India, USA, Germany)", help="Enter the country name for analysis")
with col2:
    pass

if country_name:
    if not api_key:
        st.error("Please set your Gemini API Key in the sidebar.", icon="🔑")
    else:
        tabs = st.tabs(["📈 Economic Analysis"])
        with tabs[0]:
            # Define datasets
            datasets = {
                "GDP": {"file": f"{data_path}/GDP at market prices, current US$, millions, seas. adj..xlsx", "sheet": "annual"},
                "CPI": {"file": f"{data_path}/CPI Price, % y-o-y, nominal, seas. adj..xlsx", "sheet": "annual"},
                "Unemployment Rate": {"file": f"{data_path}/Unemployment Rate, seas. adj..xlsx", "sheet": "annual"},
                "Exchange Rate": {"file": f"{data_path}/Exchange rate, new LCU per USD extended backward, period average.xlsx", "sheet": "annual"},
                "Stock Markets": {"file": f"{data_path}/Stock Markets, US$.xlsx", "sheet": "annual"}
            }
            indicator_keywords = {
                "GDP": ["GDP", "Gross Domestic Product", "economic growth"],
                "CPI": ["CPI", "Consumer Price Index", "inflation"],
                "Unemployment Rate": ["unemployment", "jobless rate"],
                "Exchange Rate": ["exchange rate", "currency"],
                "Stock Markets": ["stock market", "equity"]
            }

            # Load data and compute summaries
            data_summaries = []
            data_dict = {}
            for indicator, params in datasets.items():
                data = load_data(params["file"], params["sheet"], country_name, indicator)
                data_dict[indicator] = data
                summary = compute_data_summary(data, indicator)
                data_summaries.append(summary)

            # Fetch news
            status_placeholder = st.empty()
            status_placeholder.info("Fetching latest economic news...", icon="🔍")
            news_items = fetch_economic_news(country_name)
            status_placeholder.success("News fetched successfully!" if news_items else "No news fetched. Proceeding with analysis.", icon="✅")

            # Generate analysis
            generation_config = {"temperature": temperature, "top_p": 0.95, "top_k": 64, "max_output_tokens": max_tokens}
            model = genai.GenerativeModel(model_name=selected_model, generation_config=generation_config)
            status_placeholder.info("Generating economic analysis...", icon="🤖")
            progress_bar = st.progress(0)

            try:
                response_stream = model.generate_content(get_analysis_prompt(country_name, news_items, data_summaries), stream=True)
                full_response_text = ""
                for i, chunk in enumerate(response_stream):
                    full_response_text += chunk.text if chunk.text else ""
                    progress_bar.progress(min(100, (i + 1) * 5))

                status_placeholder.success("Analysis generated!", icon="✅")
                status_placeholder.info("Processing and displaying analysis...", icon="✍️")

                # Process and display analysis with graphs
                sections = full_response_text.split("## ")
                formatted_response = ""
                news_source_mapping = {i+1: news for i, news in enumerate(news_items) if news}

                for section in sections:
                    if not section.strip():
                        continue
                    lines = section.split("\n")
                    section_title = lines[0].strip()
                    section_content = "\n".join(lines[1:]).strip()

                    def replace_references(match):
                        ref_numbers = [num.strip() for num in match.group(0)[1:-1].split(',')]
                        superscript_refs = [
                            f"<a href='{news_source_mapping[int(num)]['url']}' target='_blank' style='text-decoration:none;'><sup>[{num}]</sup></a>"
                            if int(num) in news_source_mapping else f"<sup>[{num}]</sup>" for num in ref_numbers
                        ]
                        return ', '.join(superscript_refs)

                    section_content = re.sub(r'\[\d+(?:,\s*\d+)*\]', replace_references, section_content)
                    formatted_response += f"## {section_title}\n{section_content}\n"

                    # Dynamically insert graphs
                    section_text = section_title.lower() + " " + section_content.lower()
                    st.markdown(f"## {section_title}")
                    st.markdown(section_content, unsafe_allow_html=True)
                    for indicator, keywords in indicator_keywords.items():
                        if any(keyword.lower() in section_text for keyword in keywords):
                            plot_graph(data_dict[indicator], indicator, country_name)

                # Add references
                if news_source_mapping:
                    formatted_response += "\n### References\n<ol>\n" + "".join(
                        f"  <li><b>[{index}]</b>: {news['title']}. <i>{news['source']}, {news['time']}</i>. <a href='{news['url']}'>[Link]</a></li>\n"
                        for index, news in news_source_mapping.items()
                    ) + "</ol>\n"

                st.markdown(f"""
                    <div class="analysis-container">
                        <div class="analysis-header">Economic Analysis of {country_name}</div>
                        <div class="analysis-content">{formatted_response}</div>
                    </div>
                """, unsafe_allow_html=True)
                status_placeholder.success("Analysis displayed!", icon="✅")

            except Exception as e:
                status_placeholder.error(f"Analysis failed: {str(e)}", icon="❌")

# Footer
st.markdown("""
<div class="footer">
    <p>Developed with ❤️ by Akash Doifode | <a href="https://www.linkedin.com/in/akash-doifode-0784b826/" target="_blank">Connect on Linkedin</a></p>
</div>
""", unsafe_allow_html=True)