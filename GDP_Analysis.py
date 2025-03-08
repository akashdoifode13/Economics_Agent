import pandas as pd
import streamlit as st
from difflib import get_close_matches
import logging
import plotly.express as px
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
data_path =  "GemDataEXTR"
def normalize_country(text):
    # Remove all non-alphanumeric characters and convert to lower case.
    return "".join(ch for ch in text.lower() if ch.isalnum())

def get_matching_country(country, country_list):
    norm_input = normalize_country(country)
    
    # Original mapping: keys will be normalized.
    country_variants = {
    "us":"United States",   
    "usa": "United States",
    "unitedstatesofamerica": "United States",
    "u.s.a": "United States",
    "unitedstates": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "britain": "United Kingdom",
    "greatbritain": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "northernireland": "United Kingdom",
    "uae": "United Arab Emirates",
    "emirates": "United Arab Emirates",
    "southkorea": "Korea, Rep.",
    "republicofkorea": "Korea, Rep.",
    "northkorea": "Korea, Dem. People’s Rep.",
    "dprk": "Korea, Dem. People’s Rep.",
    "russia": "Russian Federation",
    "ussr": "Russian Federation",
    "sovietunion": "Russian Federation",
    "czechia": "Czech Republic",
    "czechrepublic": "Czech Republic",
    "slovakrepublic": "Slovakia",
    "slovakia": "Slovakia",
    "egypt": "Egypt, Arab Rep.",
    "world": "World (WBG members)",
    "emergingmarkets": "Emerging Market and Developing Economies (EMDEs)",
    "advancedeconomies": "Advanced Economies",
    "lowincomecountries": "Low-Income Countries (LIC)",
    "middleincomecountries": "Middle-Income Countries (MIC)",
    "southafrica": "South Africa",
    "rsa": "South Africa",
    "taiwan": "Taiwan, China",
    "roc": "Taiwan, China",
    "venezuela": "Venezuela, RB",
    "ivorycoast": "Côte d’Ivoire",
    "bolivia": "Bolivia",
    "iran": "Iran, Islamic Rep.",
    "persia": "Iran, Islamic Rep.",
    "vietnam": "Viet Nam",
    "vietnam": "Viet Nam",
    "hongkong": "Hong Kong SAR, China",
    "hk": "Hong Kong SAR, China",
    "india": "India",
    "bharat": "India",
    "australia": "Australia",
    "oz": "Australia",
    "canada": "Canada",
    "ca": "Canada",
    "germany": "Germany",
    "deutschland": "Germany",
    "france": "France",
    "frenchrepublic": "France",
    "japan": "Japan",
    "nippon": "Japan",
    "brazil": "Brazil",
    "brasil": "Brazil",
    "mexico": "Mexico",
    "méxico": "Mexico",
    "peru": "Peru",
    "chile": "Chile",
    "colombia": "Colombia",
    "argentina": "Argentina",
    "algeria": "Algeria",
    "algérie": "Algeria",
    "morocco": "Morocco",
    "maroc": "Morocco",
    "nigeria": "Nigeria",
    "ghana": "Ghana",
    "kenya": "Kenya",
    "ethiopia": "Ethiopia",
    "tanzania": "Tanzania, United Rep.",
    "uganda": "Uganda",
    "southsudan": "South Sudan",
    "sudan": "Sudan",
    "lebanon": "Lebanon",
    "jordan": "Jordan",
    "iraq": "Iraq",
    "kuwait": "Kuwait",
    "qatar": "Qatar",
    "oman": "Oman",
    "bahrain": "Bahrain",
    "cyprus": "Cyprus",
    "croatia": "Croatia",
    "hrvatska": "Croatia",
    "bosniaandherzegovina": "Bosnia and Herzegovina",
    "bih": "Bosnia and Herzegovina",
    "serbia": "Serbia",
    "srbija": "Serbia",
    "bulgaria": "Bulgaria",
    "българия": "Bulgaria",
    "romania": "Romania",
    "românia": "Romania",
    "hungary": "Hungary",
    "magyarország": "Hungary",
    "greece": "Greece",
    "hellas": "Greece",
    "italy": "Italy",
    "italia": "Italy",
    "spain": "Spain",
    "españa": "Spain",
    "portugal": "Portugal",
    "portugueserepublic": "Portugal",
    "poland": "Poland",
    "polska": "Poland",
    "sweden": "Sweden",
    "sverige": "Sweden",
    "switzerland": "Switzerland",
    "suisse": "Switzerland",
    "schweiz": "Switzerland",
    "svizzera": "Switzerland",
    "austria": "Austria",
    "österreich": "Austria",
    "belgium": "Belgium",
    "belgique": "Belgium",
    "belgië": "Belgium",
    "netherlands": "Netherlands",
    "holland": "Netherlands",
    "denmark": "Denmark",
    "danmark": "Denmark",
    "norway": "Norway",
    "norge": "Norway",
    "finland": "Finland",
    "suomi": "Finland",
    "ireland": "Ireland",
    "éire": "Ireland",
    "newzealand": "New Zealand",
    "nz": "New Zealand",
    "singapore": "Singapore",
    "singapura": "Singapore",
    "malaysia": "Malaysia",
    "malaisie": "Malaysia",
    "thailand": "Thailand",
    "siam": "Thailand",
    "indonesia": "Indonesia",
    "philippines": "Philippines",
    "brunei": "Brunei Darussalam",
    "macau": "Macau SAR, China",
    "mongolia": "Mongolia",
    "монголулс": "Mongolia",
    "costarica": "Costa Rica",
    "panama": "Panama",
    "dominicanrepublic": "Dominican Rep.",
    "haiti": "Haiti",
    "jamaica": "Jamaica",
    "trinidadandtobago": "Trinidad & Tobago",
    "barbados": "Barbados",
    "bahamas": "Bahamas",
    "cuba": "Cuba",
    "guyana": "Guyana",
    "suriname": "Suriname",
    "belize": "Belize",
    "guatemala": "Guatemala",
    "honduras": "Honduras",
    "elsalvador": "El Salvador",
    "nicaragua": "Nicaragua",
    "ecuador": "Ecuador",
    "paraguay": "Paraguay",
    "uruguay": "Uruguay",
    "turkey": "Turkey",
    "turkiye": "Turkey",
    "saudiarabia": "Saudi Arabia",
    "ksa": "Saudi Arabia",
    "israel": "Israel",
    "israelistate": "Israel",
    "palestine": "Palestine",
    "jordan": "Jordan",
    "lebanon": "Lebanon",
    "iraq": "Iraq",
    "kuwait": "Kuwait",
    "qatar": "Qatar",
    "oman": "Oman",
    "bahrain": "Bahrain",
    "cyprus": "Cyprus",
    "croatia": "Croatia",
    "hrvatska": "Croatia",
    "bosniaandherzegovina": "Bosnia and Herzegovina",
    "bih": "Bosnia and Herzegovina",
    "serbia": "Serbia",
    "srbija": "Serbia",
    "bulgaria": "Bulgaria",
    "българия": "Bulgaria",
    "romania": "Romania",
    "românia": "Romania",
    "hungary": "Hungary",
    "magyarország": "Hungary",
    "greece": "Greece",
    "hellas": "Greece",
    "italy": "Italy",
    "italia": "Italy",
    "spain": "Spain",
    "españa": "Spain",
    "portugal": "Portugal",
    "portugueserepublic": "Portugal",
    "poland": "Poland",
    "polska": "Poland",
    "sweden": "Sweden",
    "sverige": "Sweden",
    "switzerland": "Switzerland",
    "suisse": "Switzerland",
    "schweiz": "Switzerland",
    "svizzera": "Switzerland",
    "austria": "Austria",
    "österreich": "Austria",
    "belgium": "Belgium",
    "belgique": "Belgium",
    "belgië": "Belgium",
    "netherlands": "Netherlands",
    "holland": "Netherlands",
    "denmark": "Denmark",
    "danmark": "Denmark",
    "norway": "Norway",
    "norge": "Norway",
    "finland": "Finland",
    "suomi": "Finland",
    "ireland": "Ireland",
    "éire": "Ireland",
    "newzealand": "New Zealand",
    "nz": "New Zealand",
    "singapore": "Singapore",
    "singapura": "Singapore",
    "malaysia": "Malaysia",
    "malaisie": "Malaysia",
    "thailand": "Thailand",
    "siam": "Thailand",
    "indonesia": "Indonesia",
    "philippines": "Philippines",
    "brunei": "Brunei Darussalam",
    "macau": "Macau SAR, China",
    "mongolia": "Mongolia",
    "монголулс": "Mongolia",
    "costarica": "Costa Rica",
    "panama": "Panama",
    "dominicanrepublic": "Dominican Rep.",
    "haiti": "Haiti",
    "jamaica": "Jamaica",
    "trinidadandtobago": "Trinidad & Tobago",
    "barbados": "Barbados",
    "bahamas": "Bahamas",
    "cuba": "Cuba",
    "guyana": "Guyana",
    "suriname": "Suriname",
    "belize": "Belize",
    "guatemala": "Guatemala",
    "honduras": "Honduras",
    "elsalvador": "El Salvador",
    "nicaragua": "Nicaragua",
    "ecuador": "Ecuador",
    "paraguay": "Paraguay",
    "uruguay": "Uruguay",
    "turkey": "Turkey",
    "turkiye": "Turkey",
    "saudiarabia": "Saudi Arabia",
    "ksa": "Saudi Arabia",
    "israel": "Israel",
    "israelistate": "Israel",
    "palestine": "Palestine",
    "jordan": "Jordan",
    "lebanon": "Lebanon",
    "iraq": "Iraq",
    "kuwait": "Kuwait",
    "qatar": "Qatar",
    "oman": "Oman",
    "bahrain": "Bahrain",
    "cyprus": "Cyprus",
    "croatia": "Croatia",
    "hrvatska": "Croatia",
    "bosniaandherzegovina": "Bosnia and Herzegovina",
    "bih": "Bosnia and Herzegovina",
    "serbia": "Serbia",
    "srbija": "Serbia",
    "bulgaria": "Bulgaria",
    "българия": "Bulgaria",
    "romania": "Romania",
    "românia": "Romania",
    "hungary": "Hungary",
    "magyarország": "Hungary",
    "greece": "Greece",
    "hellas": "Greece",
    "italy": "Italy",
    "italia": "Italy",
    "spain": "Spain",
    "españa": "Spain",
    "portugal": "Portugal",
    "portugueserepublic": "Portugal",
    "poland": "Poland",
    "polska": "Poland",
    "sweden": "Sweden",
    "sverige": "Sweden",
    "switzerland": "Switzerland",
    "suisse": "Switzerland",
    "schweiz": "Switzerland",
    "svizzera": "Switzerland",
    "austria": "Austria",
    "österreich": "Austria",
    "belgium": "Belgium",
    "belgique": "Belgium",
    "belgië": "Belgium",
    "netherlands": "Netherlands",
    "holland": "Netherlands"
}
    
    # Normalize the keys in the variants mapping.
    normalized_variants = {normalize_country(k): v for k, v in country_variants.items()}
    if norm_input in normalized_variants:
        return normalized_variants[norm_input]
    
    # If no direct mapping, use difflib to search for a close match in the provided country_list.
    normalized_list = [normalize_country(name) for name in country_list]
    from difflib import get_close_matches
    matches = get_close_matches(norm_input, normalized_list, n=1, cutoff=0.6)
    if matches:
        # Return the original version from country_list matching the normalized value.
        for official in country_list:
            if normalize_country(official) == matches[0]:
                return official
    return None

def load_data(file_path, sheet_name, country, indicator_name):
    try:
        logging.info(f"Loading data from {file_path} ({sheet_name}) for {country}")
        xls = pd.ExcelFile(file_path)
        if sheet_name not in xls.sheet_names:
            logging.error(f"Worksheet named '{sheet_name}' not found in {file_path}. Available sheets: {xls.sheet_names}")
            return None
        df = pd.read_excel(xls, sheet_name=sheet_name).dropna(how="all")
        df.columns = df.columns.str.strip()
        if 'Unnamed: 0' not in df.columns:
            logging.error("Expected 'Unnamed: 0' column for years not found.")
            return None
        df.rename(columns={"Unnamed: 0": "Year"}, inplace=True)
        # Match country name
        matched_country = get_matching_country(country, df.columns)
        if not matched_country:
            logging.error(f"{indicator_name} data not found for {country}. Available: {df.columns[1:].tolist()}")
            return None
        try:
            data = df[["Year", matched_country]].dropna()
        except KeyError:
            return None
        data.columns = ["Year", indicator_name]
        # Convert "Year" differently based on sheet type
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

def analyze_country(country, data_path):
    datasets = {
        "GDP": {"file": f"{data_path}/GDP at market prices, current US$, millions, seas. adj..xlsx", "sheet": "annual"},
        "CPI": {"file": f"{data_path}/CPI Price, % y-o-y, nominal, seas. adj..xlsx", "sheet": "annual"},
        "Unemployment Rate": {"file": f"{data_path}/Unemployment Rate, seas. adj..xlsx", "sheet": "annual"},
        "Exchange Rate": {"file": f"{data_path}/Exchange rate, new LCU per USD extended backward, period average.xlsx", "sheet": "annual"},
        "Foreign Reserves": {"file": f"{data_path}/Foreign Reserves, Months Import Cover, Goods.xlsx", "sheet": "annual"},
        "Stock Markets": {"file": f"{data_path}/Stock Markets, US$.xlsx", "sheet": "annual"},
        "Terms of Trade": {"file": f"{data_path}/Terms of Trade.xlsx", "sheet": "monthly"},
        "Exports Merchandise Volume": {"file": f"{data_path}/Exports Merchandise, Customs, current US$, millions, seas. adj..xlsx", "sheet": "annual"},
        "Imports Merchandise Volume": {"file": f"{data_path}/Imports Merchandise, Customs, current US$, millions, seas. adj..xlsx", "sheet": "annual"},
        "Industrial Production": {"file": f"{data_path}/Industrial Production, constant 2010 US$, seas. adj..xlsx", "sheet": "annual"},
        "Retail Sales Volume Index": {"file": f"{data_path}/Retail Sales Volume Index, seas. adj..xlsx", "sheet": "annual"}
    }
    
    for indicator, params in datasets.items():
        data = load_data(params["file"], params["sheet"], country, indicator)
        dataset_title = os.path.basename(params["file"]).replace(".xlsx", "")
        if data is not None:
            title = f"{dataset_title} Trend for {country}"
            fig = px.line(data, x="Year", y=indicator, title=title)
            fig.update_traces(mode="lines+markers")
            st.plotly_chart(fig, use_container_width=True)
        # If data is missing, do nothing.

def main():
    st.title("GDP Analysis Tool")
    
    country = st.text_input("Country", "USA")
    if st.button("Analyze"):
        analyze_country(country, data_path)

if __name__ == "__main__":
    main()
