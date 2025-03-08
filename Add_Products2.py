import streamlit as st
import pandas as pd
import datetime
import time
import io
import re  # For regular expressions
from fuzzywuzzy import process, fuzz # Import fuzzywuzzy

def generate_product_handle(product_name): # Keep for category URL
    """Generates a URL-friendly product handle from the product name."""
    handle = product_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(",", "")
    return handle

def format_price_inr(price):
    """Formats the price as INR with two decimal places."""
    try:
        price_float = float(price)
        return f"INR {price_float:.2f}"
    except ValueError:
        return "INR -" # Handle non-numeric prices

def extract_package_weight_and_attribute(packing_string):
    """
    Extracts package weight in KG and determines attribute name from the packing string.
    Handles units like KG, gm, Litre, ml.
    """
    packing_string = packing_string.lower()
    weight_kg = 0.1 # Default package weight
    attribute_name = "Weight" # Default attribute

    num_match = re.search(r'(\d+\.?\d*)', packing_string) # Extract number
    unit_match = re.search(r'([a-z]+)', packing_string)    # Extract unit

    if num_match and unit_match:
        try:
            value = float(num_match.group(1))
            unit = unit_match.group(1)

            if unit in ['kg', 'kilogram', 'kgs']:
                weight_kg = value
                attribute_name = "Weight"
            elif unit in ['gm', 'gram', 'gms']:
                weight_kg = value / 1000.0
                attribute_name = "Weight"
            elif unit in ['litre', 'liter', 'ltr', 'l']:
                weight_kg = value # Approximation: 1 Litre ~ 1 KG for many liquids
                attribute_name = "Volume"
            elif unit in ['ml', 'millilitre', 'milliliter', 'mls']:
                weight_kg = value / 1000.0 # Approximation: 1 ml ~ 1 gram
                attribute_name = "Volume"
            else:
                weight_kg = 0.2 # Default if unit not recognized
                attribute_name = "Packing" # Default to weight
        except ValueError:
            pass # Keep default weight and attribute if parsing fails

    return max(0.0, weight_kg), attribute_name # Ensure non-negative weight


def transform_product_data(input_df, company_names_list, category_names_list, store_name): # Added store_name
    """Transforms the simplified input DataFrame into the desired product data format."""

    output_data = []
    input_df_lower_cols = {col.lower(): col for col in input_df.columns} # Lowercase column names for lookup

    for index, row in input_df.iterrows():
        product_name_simple = row[input_df_lower_cols.get('product name', input_df.columns[0])] # Case-insensitive column access
        brand_name_input = row[input_df_lower_cols.get('company', input_df.columns[1])] # Get company name from input
        category_name_input = row[input_df_lower_cols.get('type', input_df.columns[2])] # Get category name from input
        hsn_sac = str(row[input_df_lower_cols.get('hsn', input_df.columns[3])])
        gst_rate_str = str(row[input_df_lower_cols.get('gst', input_df.columns[4])]).replace('%','')
        packing = row[input_df_lower_cols.get('packing', input_df.columns[5])]
        selling_price_val = row[input_df_lower_cols.get('rate', input_df.columns[6])]
        label_price_val = row[input_df_lower_cols.get('lable prize', input_df_lower_cols.get('label prize', input_df.columns[7]))] # Handle both spellings

        try:
            gst_rate_decimal = float(gst_rate_str) / 100.0
            gst_rate_percent = int(float(gst_rate_str)) # Get percentage as integer
        except ValueError:
            gst_rate_decimal = 0.0
            gst_rate_percent = 0

        package_weight_kg, attribute_name_from_packing = extract_package_weight_and_attribute(packing)

        # Fuzzy matching for company name - using fuzz.partial_ratio
        best_company_match, company_score = process.extractOne(brand_name_input, company_names_list, scorer=fuzz.partial_ratio)
        if company_score >= 90:
            brand_name = best_company_match # Use standardized company name
        else:
            brand_name = brand_name_input # Keep original company name if no good match

        # Fuzzy matching for category name - using fuzz.partial_ratio
        best_category_match, category_score = process.extractOne(category_name_input, category_names_list, scorer=fuzz.partial_ratio)
        if category_score >= 90:
            category_name = best_category_match # Use standardized category name
        else:
            category_name = category_name_input # Keep original category name if no good match


        product_name = f"{product_name_simple} by {brand_name}"
        long_description = f"<div style=\"color:inherit\"><p><strong>{product_name}</strong></p><p>{product_name_simple} by {brand_name} in {packing} packing.</p></div>" # Original Store Description
        
        variant_name = f"{product_name}-{packing}"

        # SEO Fields
        seo_keywords = f"{product_name_simple}, {brand_name}, {category_name}, {packing}"
        seo_title = f"{product_name} | {store_name}" # Using store_name here
        seo_description = f"{product_name}. {product_name_simple} in {packing} packing. Buy online at {store_name}." # Using store_name here

        selling_price_formatted = format_price_inr(selling_price_val) # Format prices
        label_price_formatted = format_price_inr(label_price_val)

        intra_state_tax_name = f"GST{gst_rate_percent}"
        inter_state_tax_name = f"IGST{gst_rate_percent}"


        product_data_row = {
            "Product ID": "", # Blank Product ID as requested
            "Product Name": product_name,
            "Store Description": "", # Blank Store Description
            "Long Description": long_description,
            "Brand": brand_name, # Use fuzzy matched or original brand name
            "On Sale": "YES",
            "Variant ID": "", # Blank Variant ID as requested
            "Is Returnable Item": "TRUE",
            "SEO Keyword": seo_keywords,
            "SEO Title": seo_title,
            "SEO Description": seo_description,
            "Show In Store": "NO",
            "AttributeName1": attribute_name_from_packing, # Dynamic Attribute Name from Packing
            "AttributeType1": "Text",
            "AttributeName2": "",
            "AttributeType2": "",
            "AttributeName3": "",
            "AttributeType3": "",
            "Category Name": category_name, # Use fuzzy matched or original category name
            "Category URL": generate_product_handle(category_name),
            "Tags": f"{brand_name}, {product_name_simple}, {category_name}",
            "Item Type": "Inventory",
            "Variant Name": variant_name,
            "Selling Price": selling_price_formatted, # Formatted Price
            "Minimum Order Quantity": "",
            "Maximum Order Quantity": "",
            "Label Price": label_price_formatted, # Formatted Price
            "SKU": "",
            "AttributeOption1": packing,
            "AttributeOptionData1": "",
            "AttributeOption2": "",
            "AttributeOptionData2": "",
            "AttributeOption3": "",
            "AttributeOptionData3": "",
            "Opening Stock": "10",
            "Stock On Hand": "10",
            "HSN/SAC": hsn_sac,
            "UPC": "",
            "EAN": "",
            "ISBN": "",
            "Status": "Active",
            "Part Number": "",
            "Reorder Level": "5",
            "Package Weight": package_weight_kg, # Package weight from packing parsing
            "Package Width": "0",
            "Package Height": "0",
            "Package Length": "0",
            "Dimension Unit": "cm",
            "Weight Unit": "kg",
            "Created Time": "", # Blank Created Time
            "Modified Time": "", # Blank Modified Time
            "Product Handle": "", # Blank Product Handle
            "Variant Image URL": "",
            "Primary Product URL": "",
            "Taxable": "TRUE",
            "Exemption Reason": "",
            "Taxability Type": "",
            "Intra State Tax Name": intra_state_tax_name, # Dynamic Tax Name
            "Intra State Tax Rate": str(gst_rate_percent),    # Percentage as String
            "Intra State Tax Type": "Group",
            "Inter State Tax Name": inter_state_tax_name, # Dynamic Tax Name
            "Inter State Tax Rate": str(gst_rate_percent),    # Percentage as String
            "Inter State Tax Type": "Simple",
            "Item.CF.Expiry Date": (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%d/%m/%Y"),
            "Item.CF.Lot No": "1"
        }
        output_data.append(product_data_row)

    output_df = pd.DataFrame(output_data)
    return output_df

st.title("Product Data Transformer")

uploaded_file = st.file_uploader("Upload your product data file (Excel or CSV)", type=["csv", "xlsx"])

# Store Name - Define your store name here
store_name = "KrushiVista" # <---- SET YOUR STORE NAME HERE

# Standard company names list
company_names_list = [
    "Acsen Agriscience", "Adama", "Advanta", "Amar seeds", "Amar seeds", "Ankur", "BASF", "Bayer crop science",
    "Best Agrolife", "Corteva", "Crystal", "Dayal", "Dharti Seeds", "Dhanashree Crop Solutions", "Dharti Seeds",
    "Dharti Seeds", "FMC", "Godrej Agrovet", "Haldhighati seeds", "Hindustan Antibiotic", "ICL", "Insecticides India",
    "Insecticides India", "Jindal seeds", "Jivagro", "Kalash Seeds", "Kalash Seeds", "Knomatix Crop Science", "Krija",
    "Mahafeed", "Mahaganga", "Mahodaya", "Mahyco", "Mahyco", "Monsanto", "Monsoon Crop Science", "Nagarjuna",
    "Navlakha seeds", "Nethra Crop Sciences", "Nirmal Seeds", "Nunhems India", "Nuziveedu", "Panchaganga Seeds",
    "Pasura", "Phytotron Agro Products", "PI Industries", "Rallis India Limited", "Sagar seeds", "Sakata Seeds",
    "Samrudhi Kisan Biotek Pvt Ltd", "Seamon's Seeds", "Sharayu Seeds", "Sri Bio", "Sumitomo", "Syngenta",
    "T. Stanes and Company", "Triveni Chemicals", "Ultima", "United Genetics", "UPL", "US Agriseeds", "Valagro", "Welcome"
]

# Standard category names list
category_names_list = [
    "Seeds", "Insecticides", "Pest Control", "Herbicides", "Crop Nutrition", "Fungicides", "Traps and Lures"
]


if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == "csv":
        input_df = pd.read_csv(uploaded_file) # Header is used by default
    elif file_extension == "xlsx":
        input_df = pd.read_excel(uploaded_file) # Header is used by default
    else:
        st.error("Unsupported file format. Please upload CSV or XLSX.")
        st.stop()

    # Case-insensitive column check
    required_columns_lower = [col.lower() for col in ['Product Name', 'Company', 'Type', 'HSN', 'GST', 'Packing', 'Rate', 'Lable Prize']] # Lowercase required columns
    uploaded_columns_lower = [col.lower() for col in input_df.columns] # Lowercase uploaded columns

    missing_columns = [required_columns_lower[i] for i, col in enumerate(required_columns_lower) if col not in uploaded_columns_lower] # Check in lowercase

    if missing_columns:
        st.error(f"The uploaded file is missing the following required columns (case-insensitive): {', '.join(missing_columns)}")
        st.stop()


    st.subheader("First 5 rows of your uploaded data")
    st.dataframe(input_df.head())

    if st.button("Process Data"):
        start_time = time.time()
        transformed_df = transform_product_data(input_df, company_names_list, category_names_list, store_name) # Pass category_names_list
        end_time = time.time()
        processing_time = end_time - start_time

        st.success(f"Data transformation complete! (Processing time: {processing_time:.2f} seconds)")

        st.subheader("First 5 rows of Transformed Data")
        st.dataframe(transformed_df.head())

        # Download Button
        csv_buffer = io.StringIO()
        transformed_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="Download Transformed Data as CSV",
            data=csv_data,
            file_name="transformed_product_data.csv",
            mime="text/csv",
        )