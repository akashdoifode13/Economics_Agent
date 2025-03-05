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
import re  # Import the regular expression module

# Configure page settings
st.set_page_config(
    page_title="Company Research Agent",
    page_icon="🏢",
    layout="wide",
)

# Enhanced CSS styling (same as before)
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }

    /* Header styling */
    .stApp h1 {
        color: #1E3A8A;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f3f4f6 0%, #ffffff 50%, #f3f4f6 100%);
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

     /* Search Bar Styling - Modified for rectangular input */
    .stTextInput > div > div > input {
        background-color: #f5f5f5; /* Light background */
        border: 2px solid #0078D4; /* Prominent border */
        border-radius: 5px; /* Slightly rounded corners for rectangular look */
        padding: 10px 20px; /* Spacious padding */
        font-size: 1.2rem; /* Larger font size */
        transition: border-color 0.3s ease; /* Smooth transition for focus */
    }

    .stTextInput > div > div > input:focus {
        border-color: #005A9E; /* Darker border on focus */
        box-shadow: 0 0 5px rgba(0, 120, 212, 0.5); /* Subtle glow effect */
    }
     /* Button styling */
    .stButton > button {
        background-color: #0078D4; /* Blue background */
        color: white;
        padding: 10px 20px;
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        border-radius: 20px; /* Rounded corners */
        box-shadow: 0 2px 4px rgba(0,0,0,0.2); /* Subtle shadow */
        transition: all 0.3s ease; /* Smooth transition */
    }

    .stButton > button:hover {
        background-color: #005A9E; /* Darker blue on hover */
        box-shadow: 0 4px 8px rgba(0,0,0,0.3); /* More pronounced shadow */
    }

    .stButton > button:active {
        transform: translateY(1px); /* Slight press effect */
        box-shadow: none;
    }

    /* Analysis Styling */
    .analysis-container {
        background-color: #f9f9f9; /* Very light grey background */
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        margin-bottom: 30px;
    }

    .analysis-header {
        color: #004A7F;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 3px solid #0078D4;
    }

    .analysis-section {
        margin-bottom: 25px;
    }

    .analysis-section-title {
        color: #0078D4;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 15px;
        border-left: 4px solid #0078D4;
        padding-left: 10px;
    }

    .analysis-content {
        color: #333;
        font-size: 1rem;
        line-height: 1.6;
        text-align: justify;
    }

    .analysis-highlight {
        background-color: #FFF8E1;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: 600;
        color: #856404;
    }
    .analysis-content p {
            margin-bottom: 15px; /* Spacing between paragraphs */
        }

    .analysis-content ul, .analysis-content ol {
        margin-bottom: 15px; /* Spacing for lists */
    }

    .analysis-content li {
        margin-bottom: 8px; /* Spacing between list items */
    }

    .analysis-content strong {
        color: #004A7F; /* Highlight key points or terms */
    }

    .analysis-content em {
        font-style: italic;
        color: #222; /* Emphasize text */
    }
    /* Card styling */
    .stCard {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }


    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: 600;
    }

    /* News section styling */
    .news-container {
        background-color: #f9f9f9; /* Very light grey background */
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        margin-bottom: 30px;
        padding: 0; /* Remove padding to allow full-width title */
    }

    /* News header styling */
    .news-header {
        background-color: #0078D4; /* Blue background for title */
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        padding: 20px;
        border-top-left-radius: 15px;
        border-top-right-radius: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .news-date {
        font-size: 1rem;
        color: #E1E8ED; /* Light gray for date */
    }
   /* News item styling */
    .news-item {
        padding: 20px;
        border-bottom: 1px solid #E1E8ED; /* Subtle separator */
        transition: background-color 0.3s ease; /* Smooth transition on hover */
    }

    .news-item:last-child {
        border-bottom: none; /* Remove separator from last item */
    }

    .news-item:hover {
        background-color: #F5F8FA; /* Light blue on hover */
    }

    /* News title styling */
    .news-title {
        color: #14171A; /* Dark gray for title */
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        line-height: 1.3;
    }

    /* News summary styling */
    .news-summary {
        color: #657786; /* Medium gray for summary */
        font-size: 1rem;
        line-height: 1.5;
        margin-bottom: 15px;
    }

    /* News source styling */
    .news-source {
        color: #AAB8C2; /* Light gray for source */
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* News time styling */
    .news-time {
        color: #AAB8C2; /* Light gray for time */
        font-size: 0.9rem;
        float: right;
    }

    /* Full article text styling */
    .news-full-text {
        color: #292F33; /* Dark gray for full text */
        font-size: 1rem;
        line-height: 1.6;
        margin-top: 15px;
    }

    /* Link to original article styling */
    .news-full-text a {
        color: #1DA1F2; /* Blue for link */
        text-decoration: none;
    }

    .news-full-text a:hover {
        text-decoration: underline;
    }
     .gdp-news-item {
        border-left: 4px solid #22c55e; /* Green border for GDP news */
    }
      .bond-news-item {
        border-left: 4px solid #0ea5e9; /* Sky blue border for bond news */
    }

      .stock-news-item {
            border-left: 4px solid #facc15; /* Yellow border for stock market news */
        }
       .yield-news-item {
            border-left: 4px solid #a855f7; /* Purple border for yield curve news */
        }
    /* Reference styling (numbered) - Removed for simplification */


    /* Modal styling - Removed for simplification */


    /* News source link styling */
    .news-source-link {
        color: #0078D4; /* Blue color for links */
        text-decoration: none; /* No underline */
        transition: color 0.3s ease; /* Smooth color transition on hover */
    }

    .news-source-link:hover {
        color: #005A9E; /* Darker blue on hover */
        text-decoration: underline; /* Underline on hover */
    }

    /* Alert styling */
    .stAlert {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: #2563eb;
    }

    /* Markdown text styling */
    .stMarkdown {
        font-size: 1rem;
        line-height: 1.6;
    }
     /* Footer Styling */
    .footer {
        text-align: center;
        color: #6b7280;
        padding: 20px;
        font-size: 0.9rem;
        border-top: 1px solid #e5e7eb; /* Subtle top border */
    }

    /* Footer Link Styling */
    .footer a {
        color: #0078D4; /* Blue for links */
        text-decoration: none; /* No underline */
        transition: color 0.3s ease; /* Smooth transition for hover effect */
    }

    .footer a:hover {
        color: #005A9E; /* Darker blue on hover */
        text-decoration: underline; /* Underline on hover */
    }
</style>
""", unsafe_allow_html=True)

# App header with timestamp (same as before)
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<h1>🏢 Company Research Agent</h1>
<p style='text-align: center; color: #6b7280;'>Last Updated: {current_time}</p>
""", unsafe_allow_html=True)

# Helper function to fetch article content using newspaper3k (same as before)
def fetch_article_content(url):
    """
    Fetch article content using newspaper3k
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text, article.summary # Return both text and summary
    except Exception as e:
        return "Could not fetch article details.", "No summary available"

# News scraping function (enhanced for more articles and keywords)
def fetch_company_news(company_name, num_articles=20): # Increased default to 20
    """
    Improved news scraping function with detailed article content and more articles.
    Enhanced with more diverse search queries for comprehensive news coverage.
    """
    try:
        base_url = "https://www.google.com/search?q="
        search_queries = [
            f"{company_name}+company+news",
            f"{company_name}+financial+news",
            f"{company_name}+stock+news",
            f"{company_name}+business+news",
            f"{company_name}+industry+news",
            f"{company_name}+market+updates",
            f"{company_name}+product+announcements",
            f"{company_name}+leadership+changes",
            f"{company_name}+mergers+acquisitions",
            f"{company_name}+market+analysis",
            f"{company_name}+competitor+analysis",

            # **Added Keywords for Broader Analysis:**
            f"{company_name}+strategy+news",
            f"{company_name}+innovation+news",
            f"{company_name}+growth+opportunities",
            f"{company_name}+challenges+risks",
            f"{company_name}+economic+impact",
            f"{company_name}+regulatory+news",
            f"{company_name}+sustainability+initiatives", # ESG aspects
            f"{company_name}+technology+developments",
            f"{company_name}+future+outlook",
            f"{company_name}+analyst+ratings", # Market sentiment
            f"{company_name}+customer+feedback", # Customer perspective
            f"{company_name}+supply+chain+news", # Operational aspects
            f"{company_name}+corporate+social+responsibility", # Broader impact
            f"{company_name}+awards+recognition", # Positive indicators
            f"{company_name}+setbacks+failures", # Negative/risk indicators
            f"{company_name}+positive+developments", # Overall sentiment
            f"{company_name}+negative+developments", # Risk identification

        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8"
        }

        all_news_items = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_articles = {}
            for query in search_queries:
                url = f"{base_url}{query}&tbm=nws"
                future = executor.submit(fetch_news_from_url, url, query, headers)
                future_to_articles[future] = query

            for future in concurrent.futures.as_completed(future_to_articles):
                query = future_to_articles[future]
                try:
                    news_items = future.result()
                    all_news_items.extend(news_items)

                except Exception as e:
                    st.error(f"Error fetching news for {query}: {str(e)}")

        return all_news_items[:num_articles]  # Return top N articles

    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def fetch_news_from_url(url, query, headers):
    """Fetches news from a given URL and returns a list of news items."""
    news_items = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        articles = soup.select('div.SoaBEf') or \
                   soup.select('div.Gx5Zad') or \
                   soup.select('g-card')

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_article = {}

            for article in articles:
                try:
                    # Extract title and URL
                    title_elem = article.select_one('.vvjwJb') or \
                               article.select_one('.n0jPhd') or \
                               article.select_one('.mCBkyc')

                    link_elem = article.select_one('a')

                    # Extract source and time
                    metadata_elem = article.select_one('.UPmit') or \
                                  article.select_one('.LfVVr') or \
                                  article.select_one('.CEMjEf')

                    time_elem = article.select_one('time') or \
                               article.select_one('.ZE0LJd') or \
                               article.select_one('.jJzYv')

                    # Extract summary
                    summary_elem = article.select_one('.GI74Re') or \
                                 article.select_one('.VwiC3b') or \
                                 article.select_one('.s3v9rd')

                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        url = link_elem.get('href', '')

                        # Extract source and time if available
                        source = metadata_elem.get_text().strip() if metadata_elem else "News Source"
                        published_time = time_elem.get_text().strip() if time_elem else "Recent"

                        # Extract summary if available
                        summary = summary_elem.get_text().strip() if summary_elem else "No summary available"

                        # Submit article fetching task to thread pool
                        if url:
                            future = executor.submit(fetch_article_content, url)
                            future_to_article[future] = {
                                'index': len(news_items),
                                'title': title,
                                'source': source,
                                'time': published_time,
                                'summary': summary,
                                'url': url,
                                'query': query
                            }
                            news_items.append(None) # Placeholder, will be filled after thread completion

                except Exception as e:
                    continue

            # Collect results from threads
            for future in concurrent.futures.as_completed(future_to_article):
                article_data_placeholder = future_to_article[future]
                article_index = article_data_placeholder['index']
                try:
                    full_text, full_summary = future.result()
                    if article_index < len(news_items):
                        news_items[article_index] = {**article_data_placeholder, 'full_text': full_text, 'full_summary':full_summary} # Fill in the placeholder
                except Exception as e:
                     if article_index < len(news_items):
                        if news_items[article_index] is None: # in case placeholder is still None
                            news_items[article_index] = article_data_placeholder # to avoid key error
                        news_items[article_index]['full_text'] = "Error fetching article content."
                        news_items[article_index]['full_summary'] = "Could not fetch the summary"
        return news_items
    except Exception as e:
        return []

# Yahoo Finance Scraping Function (Fixed Selectors - same as before)
def fetch_yahoo_finance_data(company_ticker):
    """
    Scrapes key financial data from Yahoo Finance for a given ticker symbol.
    """
    try:
        url = f"https://finance.yahoo.com/quote/{company_ticker}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract current stock price (using a more robust selector)
        price_element = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}) or soup.find('span', {'data-reactid': '31'}) # Added fallback
        current_price = price_element.text.strip() if price_element else "N/A"

        # Extract Market Cap (using more specific selector)
        market_cap_element = soup.find('td', {'data-test': 'MARKET_CAP-value'})
        market_cap = market_cap_element.text.strip() if market_cap_element else "N/A"

        # Extract P/E Ratio (TTM) (using more specific selector)
        pe_ratio_element = soup.find('td', {'data-test': 'PE_RATIO-value'})
        pe_ratio = pe_ratio_element.text.strip() if pe_ratio_element else "N/A"

        # Extract Dividend Yield (using more specific selector)
        dividend_yield_element = soup.find('td', {'data-test': 'DIVIDEND_YIELD-value'})
        dividend_yield = dividend_yield_element.text.strip() if dividend_yield_element else "N/A"

        financial_data = {
            "source": "Yahoo Finance",
            "Current Price": current_price,
            "Market Cap": market_cap,
            "P/E Ratio (TTM)": pe_ratio,
            "Dividend Yield": dividend_yield
        }
        return financial_data

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Yahoo Finance data: {e}"}
    except Exception as e:
        return {"error": f"Error parsing Yahoo Finance data: {e}"}

# Google Finance Scraping Function
def fetch_google_finance_data(company_ticker):
    """
    Scrapes key financial data from Google Finance for a given ticker symbol.
    """
    try:
        url = f"https://www.google.com/finance/quote/{company_ticker}" # Google Finance Quote URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract current stock price (using updated selector for Google Finance)
        price_element = soup.find('div', {'class': 'kf1m0'}) # Selector for price
        current_price = price_element.text.strip() if price_element else "N/A"

        # Extract Market Cap (Google Finance uses different structure, may need to adjust selector)
        market_cap_element = soup.find('div', {'class': 'P6K39c'}) # Placeholder - may need refinement
        market_cap_span = market_cap_element.find_all('span') if market_cap_element else None # Get all spans within
        market_cap_text = market_cap_span[1].text.strip() if market_cap_span and len(market_cap_span) > 1 else "N/A" # Second span often contains value

        # Extract P/E Ratio (TTM) (Google Finance structure may vary, selector might need adjustment)
        pe_ratio_element = soup.find('div', {'class': 'P6K39c'}) # Placeholder - may need refinement
        pe_ratio_spans = pe_ratio_element.find_all('span') if pe_ratio_element else None
        pe_ratio_text = pe_ratio_spans[1].text.strip() if pe_ratio_spans and len(pe_ratio_spans) > 1 else "N/A"

        # Extract Dividend Yield (Google Finance structure may vary, selector might need adjustment)
        dividend_yield_element = soup.find('div', {'class': 'P6K39c'}) # Placeholder - may need refinement
        dividend_yield_spans = dividend_yield_element.find_all('span') if dividend_yield_element else None
        dividend_yield_text = dividend_yield_spans[1].text.strip() if dividend_yield_spans and len(dividend_yield_spans) > 1 else "N/A"


        financial_data = {
            "source": "Google Finance",
            "Current Price": current_price,
            "Market Cap": market_cap_text,
            "P/E Ratio (TTM)": pe_ratio_text,
            "Dividend Yield": dividend_yield_text
        }
        return financial_data

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Google Finance data: {e}"}
    except Exception as e:
        return {"error": f"Error parsing Google Finance data: {e}"}


# Web Search for Ticker Symbol (same as before)
def fetch_company_ticker(company_name):
    """
    Searches Google to find the stock ticker symbol for a given company name.
    """
    try:
        url = f"https://www.google.com/search?q={company_name}+stock+ticker"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find the ticker in different HTML elements (adjust as needed)
        ticker_element = soup.find('div', {'class': 'BNeawe tAd8D AP7Wnd'}) or \
                         soup.find('span', {'class': 'BNeawe s3v9rd AP7Wnd'}) or \
                         soup.find('div', {'class': 'rpHNPb'}) # Added more potential selectors

        if ticker_element:
            ticker = ticker_element.text.split(":")[0].strip() # Extract ticker if found, handle potential ":"
            return ticker.upper()  # Return ticker in uppercase
        else:
            return None  # Ticker not found

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching ticker symbol: {e}")
        return None
    except Exception as e:
        st.error(f"Error parsing ticker symbol from search results: {e}")
        return None


# Web Search for Transcripts (same as before)
def fetch_company_transcripts(company_name, num_transcripts=5):
    """
    Searches for recent company transcripts (earnings calls, investor calls) using Google Search.
    """
    try:
        base_url = "https://www.google.com/search?q="
        search_queries = [
            f"{company_name}+earnings+call+transcript+recent",
            f"{company_name}+investor+call+transcript+recent",
            f"{company_name}+financial+results+transcript+recent",
            f"{company_name}+quarterly+report+transcript+recent",
            f"{company_name}+conference+call+transcript+recent"
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8"
        }

        transcript_items = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_transcript = {}
            for query in search_queries:
                url = f"{base_url}{query}&tbm=nws"  # Using news tab for potentially faster updates
                future = executor.submit(fetch_news_from_url_transcript, url, query, headers) # Reusing fetch_news_from_url framework
                future_to_transcript[future] = query

            for future in concurrent.futures.as_completed(future_to_transcript):
                query = future_to_transcript[future]
                try:
                    news_items = future.result() # Reusing news item structure for transcripts for simplicity
                    transcript_items.extend(news_items)

                except Exception as e:
                    st.error(f"Error fetching transcripts for {query}: {str(e)}")

        return transcript_items[:num_transcripts] # Return top N transcripts

    except Exception as e:
        st.error(f"Error fetching transcripts: {str(e)}")
        return []


def fetch_news_from_url_transcript(url, query, headers): # Reusing news fetching but adapting for transcripts
    """Fetches news/transcript snippets from a given URL and returns a list of items."""
    news_items = [] # Reusing news_items list structure
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        articles = soup.select('div.SoaBEf') or \
                   soup.select('div.Gx5Zad') or \
                   soup.select('g-card')

        for article in articles:
            try:
                # Extract title and URL
                title_elem = article.select_one('.vvjwJb') or \
                           article.select_one('.n0jPhd') or \
                           article.select_one('.mCBkyc')

                link_elem = article.select_one('a')

                # Extract source and time
                metadata_elem = article.select_one('.UPmit') or \
                              article.select_one('.LfVVr') or \
                              article.select_one('.CEMjEf')

                time_elem = article.select_one('time') or \
                           article.select_one('.ZE0LJd') or \
                           article.select_one('.jJzYv')

                # Extract summary
                summary_elem = article.select_one('.GI74Re') or \
                             article.select_one('.VwiC3b') or \
                             article.select_one('.s3v9rd')

                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href', '')

                    # Extract source and time if available
                    source = metadata_elem.get_text().strip() if metadata_elem else "Source"
                    published_time = time_elem.get_text().strip() if time_elem else "Recent"

                    # Extract summary if available
                    summary = summary_elem.get_text().strip() if summary_elem else "No summary available"

                    news_items.append({ # Keep news_items structure
                        'title': title,
                        'source': source,
                        'time': published_time,
                        'summary': summary,
                        'url': url,
                        'full_text': "Transcript - Full text not fetched", # Indicate not full article
                        'full_summary': "Transcript Snippet" # Indicate snippet
                    })

            except Exception as e:
                continue # Ignore errors and proceed to next article

        return news_items
    except Exception as e:
        return []


# Helper function to generate analysis prompt - Modified to integrate Google Finance Data
def get_analysis_prompt(company_name, news_items, yahoo_finance_data, google_finance_data, transcript_items):
    news_summary_list = []
    reference_list = []
    if news_items:
        for i, item in enumerate(news_items):
            news_summary_list.append(f"{i + 1}. {item['summary']} (Source: {item['source']}, Published: {item['time']})") # Simplified summary format
            reference_list.append(f"**[{i + 1}]**: *{item['title']}*. {item['source']}, {item['time']}. URL: {item['url']}")

        news_summary = "\n".join(news_summary_list) # Markdown line breaks

    else:
        news_summary = "No recent news available."

    yahoo_financial_summary = ""
    if yahoo_finance_data and not yahoo_finance_data.get("error"):
        yahoo_financial_summary = f"""
**Key Financial Data (Yahoo Finance):**
* **Current Price:** {yahoo_finance_data.get('Current Price', 'N/A')}
* **Market Cap:** {yahoo_finance_data.get('Market Cap', 'N/A')}
* **P/E Ratio (TTM):** {yahoo_finance_data.get('P/E Ratio (TTM)', 'N/A')}
* **Dividend Yield:** {yahoo_finance_data.get('Dividend Yield', 'N/A')}
        """
    elif yahoo_finance_data and yahoo_finance_data.get("error"):
        yahoo_financial_summary = f"Error fetching Yahoo Finance data: {yahoo_finance_data['error']}"
    else:
        yahoo_financial_summary = "No Yahoo Finance data available."

    google_financial_summary = ""
    if google_finance_data and not google_finance_data.get("error"):
        google_financial_summary = f"""
**Key Financial Data (Google Finance):**
* **Current Price:** {google_finance_data.get('Current Price', 'N/A')}
* **Market Cap:** {google_finance_data.get('Market Cap', 'N/A')}
* **P/E Ratio (TTM):** {google_finance_data.get('P/E Ratio (TTM)', 'N/A')}
* **Dividend Yield:** {google_finance_data.get('Dividend Yield', 'N/A')}
        """
    elif google_finance_data and google_finance_data.get("error"):
        google_financial_summary = f"Error fetching Google Finance data: {google_finance_data['error']}"
    else:
        google_financial_summary = "No Google Finance data available."


    transcript_summary_list = []
    if transcript_items:
        transcript_summary_list = [f"* {item['title']} (Source: {item['source']}, Published: {item['time']}, URL: {item['url']})" for item in transcript_items]
        transcript_summary_text = "\n".join(transcript_summary_list)
        transcript_section = f"""
**Recent Transcripts (Web Search Snippets):**
{transcript_summary_text}

*Note: These are snippets from web search; full transcripts may require further access.*
        """
    else:
        transcript_section = "No recent transcripts found in web search."


    return f"""
You are a senior company research analyst providing a comprehensive analysis for {company_name}.

Incorporate the following information into your analysis, weaving it into the different sections as relevant:

**Latest News Headlines and Summaries:**
{news_summary}

**Financial Data from Yahoo Finance:**
{yahoo_financial_summary}

**Financial Data from Google Finance:**
{google_financial_summary}

**Recent Transcripts (Web Search Snippets):**
{transcript_section}


**Important: Do not include a "References" or "Bibliography" section in your analysis text.  A references section for news will be added programmatically by the application.**

Provide a detailed analysis covering:

**Overview:** Briefly describe the company, its industry, and its core business model.  *Incorporate relevant overview information from any available data sources.*

**Financial Performance:** Analyze the company's revenue, profit, market capitalization, **current stock price (from Yahoo & Google Finance)**, recent earnings reports, key financial trends, and **P/E ratio (from Yahoo & Google Finance)**. *Integrate key financial data points from both Yahoo Finance and Google Finance directly into this section, compare data if available from both sources.*

**Market Position & Competition:** Identify the company's major competitors, market share, and unique value proposition. *Use news and transcripts to inform this section if relevant.*

**Recent Developments:** Summarize recent news, including funding rounds, product launches, acquisitions, partnerships, and **insights from recent transcripts (if available)**. *Focus on recent news and transcript snippets for this section.*

**Leadership & Team:** Discuss the company's CEO, key executives, and their strategic direction. *Look for any leadership changes or strategic direction mentioned in news or transcripts.*

**Challenges & Risks:** Identify potential threats, regulatory issues, or market risks facing the company. *News and transcripts can be valuable for identifying current challenges and risks.*

**Future Outlook:** Provide a forward-looking perspective on the company's growth opportunities, industry trends, and analyst predictions, **considering the financial data and recent transcripts from all sources**. *Synthesize information from all sources to create a comprehensive future outlook.*

**For each section, aim to identify and discuss:**

*   **Strengths:** What are the company's key advantages and positive aspects?
*   **Weaknesses:** What are the company's shortcomings or areas for improvement?
*   **Opportunities:** What external factors or internal initiatives can the company leverage for growth and success?
*   **Threats:** What external challenges or risks does the company face?

*While not explicitly required to structure the output as a SWOT table, please consider these dimensions when analyzing each section to provide a balanced and insightful perspective.*


Format the report in markdown with clear headers and subheaders. Be concise and data-driven. Highlight key findings and important data points using bold or italic text. When referencing news items, please use bracketed numbers like [1], [2], etc., corresponding to the news items listed above. The news references will be listed at the end of the analysis. Aim for a substantial and detailed output.
"""


# API Key retrieval from environment variable (same as before)
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("🔑 Gemini API Key not found! Please set the `GEMINI_API_KEY` environment variable.")


# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔍 Company Analysis")
    company_name = st.text_input(
        "",
        placeholder="Enter company name (e.g., Apple, Google, Tesla)",
        help="Enter the company name for detailed research analysis"
    )

# with col2:  No more ticker input field

# Function to display news (removed separate news tab display)
# def display_company_news(company_name): ...  removed

# Function to display transcripts (removed separate transcripts tab display)
# def display_company_transcripts(transcript_items): ... removed

# Function to display financial data (removed separate financial data tab display)
# def display_company_financial_data(yahoo_finance_data, company_name, company_ticker): ... removed


if company_name:
    if not api_key:
        st.stop()
    else:
        # No more tabs, only Analysis Tab
        # tabs = st.tabs(["📈 Company Analysis", "📰 News", "🎤 Transcripts", "📊 Financial Data"])  removed tabs

        # with tabs[0]: # Company Analysis Tab  No more tabs, directly in main flow
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }

        model_options = [
            "gemini-2.0-flash",
        ]
        selected_model = "gemini-2.0-flash"

        model = genai.GenerativeModel(
            model_name=selected_model,
            generation_config=generation_config,
        )

        status_placeholder = st.empty()
        status_placeholder.info("Fetching latest company news...", icon="🔍")
        news_for_analysis = fetch_company_news(company_name)
        if news_for_analysis:
            status_placeholder.success("News fetched successfully!", icon="✅")
        else:
            status_placeholder.warning("Could not fetch company news. Analysis will proceed without news context.", icon="⚠️")

        status_placeholder.info("Fetching recent transcripts...", icon="🎤")
        transcripts_for_analysis = fetch_company_transcripts(company_name)
        if transcripts_for_analysis:
            status_placeholder.success("Transcripts fetched successfully!", icon="✅")
        else:
            status_placeholder.warning("Could not fetch company transcripts. Analysis will proceed without transcript context.", icon="⚠️")

        company_ticker = fetch_company_ticker(company_name) # Fetch ticker automatically
        yahoo_finance_data = {}
        google_finance_data = {}
        if company_ticker:
            status_placeholder.info(f"Ticker found: {company_ticker}. Fetching financial data from Yahoo Finance...", icon="📊")
            yahoo_finance_data = fetch_yahoo_finance_data(company_ticker)
            if yahoo_finance_data and not yahoo_finance_data.get("error"):
                status_placeholder.success("Yahoo Finance data fetched!", icon="✅")
            else:
                status_placeholder.warning(f"Could not fetch Yahoo Finance data: {yahoo_finance_data.get('error', 'Unknown error')}", icon="⚠️")

            status_placeholder.info(f"Fetching financial data from Google Finance...", icon="📊")
            google_finance_data = fetch_google_finance_data(company_ticker)
            if google_finance_data and not google_finance_data.get("error"):
                status_placeholder.success("Google Finance data fetched!", icon="✅")
            else:
                status_placeholder.warning(f"Could not fetch Google Finance data: {google_finance_data.get('error', 'Unknown error')}", icon="⚠️")

        else:
            status_placeholder.warning("Could not automatically find ticker symbol. Financial data from Yahoo and Google Finance will be unavailable.", icon="⚠️")


        status_placeholder.info("Generating company analysis using Gemini...", icon="🤖")
        progress_bar = st.progress(0)

        try:
            response_stream = model.generate_content(
                get_analysis_prompt(company_name, news_for_analysis, yahoo_finance_data, google_finance_data, transcripts_for_analysis),
                stream=True
            )

            full_response_text = ""
            for i, chunk in enumerate(response_stream):
                full_response_text += chunk.text if chunk.text else ""
                progress_percent = min(100, (i + 1) * 5)
                progress_bar.progress(progress_percent)

            status_placeholder.success("Analysis generated!", icon="✅")

            status_placeholder.info("Processing and displaying analysis...", icon="✍️")
            # Process and display response
            if full_response_text:
                sections = full_response_text.split("## ")
                formatted_response = ""
                news_source_mapping = {i+1: news for i, news in enumerate(news_for_analysis) if news}

                for section in sections:
                    if not section.strip():
                        continue
                    lines = section.split("\n")
                    section_title = lines[0]
                    section_content = "\n".join(lines[1:])

                    # Index news sources
                    def replace_references(match):
                        ref_numbers_str = match.group(0)[1:-1]
                        ref_numbers = [num.strip() for num in ref_numbers_str.split(',')]
                        superscript_refs = []
                        for num in ref_numbers:
                            try:
                                ref_index = int(num)
                                if ref_index in news_source_mapping:
                                    article_url = news_source_mapping[ref_index]['url']
                                    superscript_refs.append(f"<a href='{article_url}' target='_blank' style='text-decoration:none;'><sup>[{num}]</sup></a>")
                                else:
                                    superscript_refs.append(f"<sup>[{num}]</sup>")
                            except ValueError:
                                superscript_refs.append(f"<sup>[{num}]</sup>")
                        return ', '.join(superscript_refs)

                    section_content = re.sub(r'\[\d+(?:,\s*\d+)*\]', replace_references, section_content)

                    formatted_response += f"## {section_title}\n{section_content}\n"

                # References Section
                if news_source_mapping:
                    formatted_response += "\n### References\n"
                    formatted_response += "<ol>\n"
                    for index, news in news_source_mapping.items():
                        formatted_response += f"  <li><b>[{index}]</b>: {news['title']}. <i>{news['source']}, {news['time']}</i>. <a href='{news['url']}'>[Link to Article]</a></li>\n"
                    formatted_response += "</ol>\n"


                formatted_response = formatted_response.rstrip()
                formatted_response = formatted_response.rstrip('</div> </div>')
                while formatted_response.endswith('</div>'):
                    formatted_response = formatted_response[:-6].rstrip()


                st.markdown(f"""
                    <div class="analysis-container">
                        <div class="analysis-header">
                            Company Analysis of {company_name}
                        </div>
                        <div class="analysis-content">
                            {formatted_response}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                status_placeholder.success("Analysis displayed!", icon="✅")


        except Exception as e:
            status_placeholder.error(f"Analysis generation failed: {str(e)}", icon="❌")


# Footer (same as before)
st.markdown("""
<div class="footer">
    <p>
        Developed with ❤️ by Akash Doifode |
        <a href="https://www.linkedin.com/in/akash-doifode-0784b826/" target="_blank">Connect on Linkedin</a>
    </p>
</div>
""", unsafe_allow_html=True)