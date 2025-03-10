from fuzzywuzzy import process
import re

def normalize_country_name(input_country, countries_list, threshold=80):
    """
    Maps input country names to standard country names using fuzzy matching.
    
    Args:
        input_country (str): The country name input by the user
        countries_list (list): List of standard country names
        threshold (int): Minimum score required for a match (0-100)
        
    Returns:
        str: The matched standard country name or None if no good match
    """
    # Clean input: remove special characters, extra spaces
    cleaned_input = re.sub(r'[^\w\s]', ' ', input_country)
    cleaned_input = re.sub(r'\s+', ' ', cleaned_input).strip()
    
    # Handle common abbreviations and alternative names
    common_mappings = {
        'usa': 'United States',
        'us': 'United States',
        'u.s.': 'United States',
        'u.s.a.': 'United States',
        'america': 'United States',
        'uk': 'United Kingdom',
        'u.k.': 'United Kingdom',
        'great britain': 'United Kingdom',
        'uae': 'United Arab Emirates',
        'china': 'China',
        'prc': 'China',
        'russia': 'Russian Federation',
        'skorea': 'Korea, Rep.',
        'south korea': 'Korea, Rep.',
        'nkorea': 'Korea, Dem. Peoples Rep.',
        'north korea': 'Korea, Dem. Peoples Rep.',
        'hk': 'Hong Kong SAR, China',
        'hong kong': 'Hong Kong SAR, China',
        'czech': 'Czech Republic',
        'czechia': 'Czech Republic',
    }
    
    # Check direct mapping first
    lower_input = cleaned_input.lower()
    if lower_input in common_mappings:
        mapped_name = common_mappings[lower_input]
        # Ensure the mapped name is in our list
        if mapped_name in countries_list:
            return mapped_name
    
    # Use fuzzy matching for more complex cases
    match, score = process.extractOne(cleaned_input, countries_list)
    
    if score >= threshold:
        return match
    else:
        return None

# Example usage
def main():
    # Your list of countries
    countries = [
"Albania", "Argentina", "Armenia", "Australia", "Austria", "Belgium",
"Bulgaria", "Bahrain", "Bosnia and Herzegovina", "Belarus", "Bolivia",
"Brazil", "Botswana", "Canada", "Switzerland", "Chile", "China",
"Cameroon", "Colombia", "Costa Rica", "Cyprus", "Czech Republic",
"Germany", "Denmark", "Ecuador", "Egypt, Arab Rep.", "Spain", "Estonia",
"Finland", "France", "United Kingdom", "Georgia", "Ghana", "Greece",
"Guatemala", "Hong Kong SAR, China", "Honduras", "Croatia", "Hungary",
"Indonesia", "India", "Ireland", "Iceland", "Israel", "Italy", "Jamaica",
"Jordan", "Japan", "Kazakhstan", "Kenya", "Korea, Rep.", "Kuwait",
"Sri Lanka", "Lithuania", "Luxembourg", "Latvia", "Morocco", "Moldova, Rep.",
"Mexico", "North Macedonia", "Malta", "Mongolia", "Mauritius", "Malaysia",
"Nigeria", "Nicaragua", "Netherlands", "Norway", "New Zealand", "Peru",
"Philippines", "Poland", "Portugal", "Paraguay", "Romania", "Russian Federation",
"Saudi Arabia", "Singapore", "El Salvador", "Serbia", "Slovakia", "Slovenia",
"Sweden", "Thailand", "Tunisia", "Turkey", "Taiwan, China", "Ukraine",
"Uruguay", "United States", "Uzbekistan", "South Africa", "Oman", "Venezuela",
"Bermuda", "St. Vincent and the Grenadines", "Barbados", "Aruba", "Bahamas, The",
"Antigua and Barbuda", "Belize", "Dominica", "Suriname", "Haiti", "St. Kitts and Nevis",
"Cayman Islands", "St. Lucia", "Panama", "Guyana", "Cuba", "Dominican Republic",
"Grenada", "San Marino", "Greenland", "Faroe Islands", "Virgin Islands, US",
"Tanzania", "Chad", "Central African Republic", "Gabon", "Togo", "Congo, Republic of",
"Eritrea", "Cabo Verde", "Niger", "Gambia, The", "Comoros", "Lesotho", "Sudan",
"Sierra Leone", "Seychelles", "Madagascar", "Mali", "Mauritania", "Senegal",
"Somalia", "Namibia", "Guinea", "Mozambique", "Equatorial Guinea", "Rwanda",
"Guinea-Bissau", "Malawi", "Eswatini", "Liberia", "Ethiopia", "Benin",
"Burkina Faso", "Zimbabwe", "Congo, Democratic Republic of", "Burundi", "Angola",
"Uganda", "Zambia", "Samoa", "Macao SAR, China", "Kiribati", "Cambodia",
"Myanmar", "Vanuatu", "Solomon Islands", "Lao People's Democratic Republic",
"French Polynesia", "Tonga", "Timor-Leste", "Brunei Darussalam", "Papua New Guinea",
"Viet Nam", "New Caledonia", "Fiji", "Bhutan", "Pakistan", "Nepal", "Bangladesh",
"Maldives", "Afghanistan", "Azerbaijan", "Tajikistan", "Turkiye", "Turkmenistan",
"Czechia", "Isle of Man", "Qatar", "Yemen, People's Democratic Republic of",
"Syrian Arab Republic", "Iraq", "Djibouti", "Iran, Islamic Republic of",
"United Arab Emirates", "Lebanon", "Libya", "Algeria"
]
    
    # Test cases
    test_inputs = [
        "USA", "U.S.A.", "America", "UK", "Great Britain", "Deutschland", 
        "Czech", "PRC", "South Korea", "Hong Kong", "HK", "Nippon",
        "UAE", "Holland", "Russia", "Brasil", "México", "Bangalore","Mumbai","Bangkok","US"
    ]
    
    for input_name in test_inputs:
        match = normalize_country_name(input_name, countries)
        print(f"Input: '{input_name}' → Matched: '{match}'")

if __name__ == "__main__":
    main()