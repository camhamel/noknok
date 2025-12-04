import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import re
import sys

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = 'fsbo_listings.csv'
OUTPUT_FILE = 'fsbo_map_data.csv'
CITY_SUFFIX = ", Montreal, QC"

# ==========================================
# CLEANING LOGIC
# ==========================================
def clean_address(raw_address):
    if not isinstance(raw_address, str) or not raw_address.strip():
        return None

    address = raw_address.strip()

    # 1. Filter out Junk Data
    if "vendu" in address.lower() or not address[0].isdigit():
        return None

    # 2. Montreal Specific Fixes
    replacements = {
        "Montp": "Montpetit",
        "Mountain Sight": "Mountain Sights",
        "Mountain Sightss": "Mountain Sights", 
        "Ch.": "Chemin",
        "Boul.": "Boulevard",
        "Ave.": "Avenue",
        " Av ": " Avenue ",
        "Avenue De Marlowe": "Avenue Marlowe",
        "Chemin De La Cote Saint": "Chemin de la Côte-Saint-Luc" 
    }
    
    for bad, good in replacements.items():
        if address.endswith(bad): 
            address = address[:-len(bad)] + good
        elif bad in address:
            address = address.replace(bad, good)

    # 3. Remove Trailing Unit Numbers (e.g., "Marquette 4")
    address = re.sub(r'\s+\d{1,3}$', '', address)

    # 4. Remove Leading Unit Numbers (e.g., "5 3239")
    match_start = re.search(r'^\d{1,5}\s+(\d{3,5}\s+.*)', address)
    if match_start:
        address = match_start.group(1)

    return address.strip()

# ==========================================
# MAIN EXECUTION
# ==========================================
def run_geocoder():
    # We remove 'print' statements here as they conflict with Streamlit's internal logging
    # and use the Streamlit status box in app.py instead.
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        return

    # Normalize Column Names
    df.columns = df.columns.str.strip().str.lower()
    
    # Find address column
    possible_names = ['address', 'location', 'title', 'addr']
    address_col = None
    
    for name in possible_names:
        if name in df.columns:
            address_col = name
            break
            
    if address_col is None:
        sys.exit()

    geolocator = Nominatim(user_agent="my_montreal_fsbo_project", timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.5)

    latitudes = []
    longitudes = []
    clean_addresses = []

    for index in df.index:
        raw_addr = df.at[index, address_col]
        clean_addr = clean_address(raw_addr)

        if clean_addr is None:
            latitudes.append(None)
            longitudes.append(None)
            clean_addresses.append(None)
            continue

        try:
            # Try with City Suffix
            location = geocode(clean_addr + CITY_SUFFIX)
            
            # Retry without suffix if failed
            if location is None:
                location = geocode(clean_addr)

            if location:
                latitudes.append(location.latitude)
                longitudes.append(location.longitude)
                clean_addresses.append(clean_addr)
            else:
                latitudes.append(None)
                longitudes.append(None)
                clean_addresses.append(clean_addr)

        except Exception:
            latitudes.append(None)
            longitudes.append(None)
            clean_addresses.append(clean_addr)

    # Save Results
    df['latitude'] = latitudes
    df['longitude'] = longitudes
    df['clean_address'] = clean_addresses

    df_clean = df.dropna(subset=['latitude', 'longitude'])
    
    df_clean.to_csv(OUTPUT_FILE, index=False)
