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
import io
import re
import logging
import plotly.express as px
from difflib import get_close_matches

# Configure logging for chart plotting functions
logging.basicConfig(level=logging.INFO)
data_path_input = "GemDataEXTR"

# Define country variants mapping at the module level so it's accessible for testing
country_variants = {
    "us": "United States",
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
    "northkorea": "Korea, Dem. People's Rep.",
    "dprk": "Korea, Dem. People's Rep.",
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
    "ivorycoast": "Côte d'Ivoire",
    "bolivia": "Bolivia",
    "iran": "Iran, Islamic Rep.",
    "persia": "Iran, Islamic Rep.",
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
    "palestine": "Palestine"
}

def normalize_country(text):
    # Remove all non-alphanumeric characters and convert to lower case.
    return "".join(ch for ch in text.lower() if ch.isalnum())

def get_matching_country(country, country_list):
    norm_input = normalize_country(country)

    # Normalize the keys in the variants mapping.
    normalized_variants = {normalize_country(k): v for k, v in country_variants.items()}
    if norm_input in normalized_variants:
        return normalized_variants[norm_input]

    # If no direct mapping, use difflib to search for a close match in the provided country_list.
    normalized_list = [normalize_country(name) for name in country_list]
    matches = get_close_matches(norm_input, normalized_list, n=1, cutoff=0.2)
    if matches:
        # Return the original version from country_list matching the normalized value.
        for official in country_list:
            if normalize_country(official) == matches[0]:
                return official
    return None

# --- Terminal Testing ---
if __name__ == "__main__":
    # Get unique official country names from the mapping
    official_country_names = list(set(country_variants.values()))
    
    print("Welcome to the Country Name Mapper!")
    print("This tool maps common country name variants to their official names.")
    print("Type 'exit' to quit.\n")
    
    while True:
        country_input = input("Enter a country name to test mapping: ").strip()
        if country_input.lower() == 'exit':
            print("Goodbye!")
            break

        if country_input:
            mapped_country = get_matching_country(country_input, official_country_names)

            print("\n### Input Country:")
            print(f"{country_input}")

            print("\n### Mapped Country:")
            if mapped_country:
                print(f"{mapped_country}")
            else:
                print("No mapping found for this country.")
        print("-" * 30 + "\n") # Separator for clarity