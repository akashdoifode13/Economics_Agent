import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from newspaper import Article
import concurrent.futures

def fetch_article_content(url):
    """
    Fetch article content using newspaper3k
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text # Fetching full article text now
    except Exception as e:
        return "Could not fetch article details."

def fetch_economic_news(country, num_articles=15): # Increased default to 15 articles
    """
    Improved news scraping function with detailed article content and GDP filtering
    """
    try:
        url = f"https://www.google.com/search?q={country}+economy+financial+news&tbm=nws"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        news_items = []
        gdp_news_items = [] # List to store GDP related news
        other_news_items = [] # List for other news

        # Find all news article containers
        articles = soup.select('div.SoaBEf') or \
                  soup.select('div.Gx5Zad') or \
                  soup.select('g-card')

        # Keywords for GDP and growth related articles
        gdp_keywords = ["GDP", "growth rate", "economic growth", "GDP growth", "percent growth", "% growth", "gdp percentage", "growth percentage"]

        # Create a thread pool for parallel article fetching
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
                            }
                            news_items.append(None) # Placeholder, will be filled after thread completion


                            # Break if we have enough articles (initial fetch target, can be more than displayed finally)
                            if len(news_items) >= num_articles * 2: # Fetching more initially to filter
                                break

                except Exception as e:
                    continue

            # Collect results from threads and filter for GDP content
            for future in concurrent.futures.as_completed(future_to_article):
                article_data_placeholder = future_to_article[future]
                article_index = article_data_placeholder['index']
                try:
                    full_text = future.result()
                    if article_index < len(news_items):
                        news_items[article_index] = {**article_data_placeholder, 'full_text': full_text} # Fill in the placeholder

                        is_gdp_news = any(keyword.lower() in full_text.lower() for keyword in gdp_keywords)
                        if is_gdp_news:
                            gdp_news_items.append(news_items[article_index])
                        else:
                            other_news_items.append(news_items[article_index])

                except Exception as e:
                    if article_index < len(news_items):
                        if news_items[article_index] is None: # in case placeholder is still None
                            news_items[article_index] = article_data_placeholder # to avoid key error
                        news_items[article_index]['full_text'] = "Error fetching article content."
                        other_news_items.append(news_items[article_index]) # Consider as other news if fetching fails

        # Combine GDP news and other news, prioritize GDP news
        combined_news_items = gdp_news_items[:num_articles] + other_news_items[:max(0, num_articles - len(gdp_news_items))] # Prioritize GDP news, then fill with others
        return combined_news_items

    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def display_economic_news(country):
    """
    Enhanced news display with collapsible detailed content
    """
    # Custom CSS for news display (same as before)
    st.markdown("""
        <style>
            .news-container {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .news-header {
                color: #1a365d;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e2e8f0;
            }
            .news-item {
                background: #f8fafc;
                border-left: 4px solid #3b82f6;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 0 8px 8px 0;
            }
            .news-title {
                color: #1e40af;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 8px;
                line-height: 1.4;
            }
            .news-summary {
                color: #334155;
                font-size: 14px;
                margin: 10px 0;
                line-height: 1.6;
            }
            .news-full-text {
                color: #1f2937;
                font-size: 14px;
                margin: 15px 0;
                padding: 15px;
                background: #ffffff;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                line-height: 1.6;
            }
            .news-metadata {
                color: #64748b;
                font-size: 14px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #e2e8f0;
            }
            .news-source {
                font-weight: 500;
                color: #475569;
            }
            .news-time {
                color: #94a3b8;
            }
             .gdp-news-item {
                border-left: 4px solid #22c55e; /* Green border for GDP news */
            }
        </style>
    """, unsafe_allow_html=True)

    # Display news with loading animation
    with st.spinner(f"🔍 Fetching latest economic news for {country}..."):
        news_items = fetch_economic_news(country)
        time.sleep(0.5)  # Smooth transition

    if news_items:
        st.markdown(f"""
            <div class="news-container">
                <div class="news-header">
                    📰 Latest Economic News for {country}
                    <span style="float: right; font-size: 14px; color: #64748b;">
                        {datetime.now().strftime("%B %d, %Y %H:%M")}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for i, item in enumerate(news_items):
            is_gdp_related = any(keyword.lower() in item['full_text'].lower() for keyword in ["GDP", "growth rate", "economic growth", "GDP growth", "percent growth", "% growth", "gdp percentage", "growth percentage"]) if item['full_text'] else False
            news_item_class = "news-item"
            if is_gdp_related:
                news_item_class += " gdp-news-item" # Add class for GDP related news

            st.markdown(f"""
                <div class="{news_item_class}">
                    <div class="news-title">{item['title']}</div>
                    <div class="news-summary">{item['summary']}</div>
                </div>
            """, unsafe_allow_html=True)

            # Add collapsible full text section
            with st.expander("Read more"):
                if item['full_text']:
                    # Displaying full text with line breaks for better readability
                    formatted_full_text = item['full_text'].replace("\n", "<br>")
                    st.markdown(f"""
                        <div class="news-full-text">
                            {formatted_full_text}
                        </div>
                    """, unsafe_allow_html=True)
                    if item['url']:
                        st.markdown(f"[Read original article]({item['url']})")
                else:
                    st.info("Full article text not available.")

            # Add metadata after expander
            st.markdown(f"""
                <div class="news-metadata">
                    <span class="news-source">🗞️ {item['source']}</span>
                    <span class="news-time">⏰ {item['time']}</span>
                </div>
            """, unsafe_allow_html=True)

    else:
        st.info("Fetching news... If no results appear, try refreshing the page.", icon="ℹ️")

# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="Economic News Dashboard", layout="wide")

    # Add requirements warning
    st.sidebar.warning("""
        This app requires the newspaper3k library.
        Install it using:
        ```
        pip install newspaper3k
        ```
    """)

    # Add the header
    st.markdown("""
        <h1 style='text-align: center; color: #1a365d; padding: 20px 0;'>
            🌍 Global Economic News Tracker
        </h1>
    """, unsafe_allow_html=True)

    # Add the country input
    country = st.text_input("Enter country name:", value="India",
                           help="Enter a country name to see its latest economic news")

    if country:
        display_economic_news(country)