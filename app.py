import streamlit as st
import pandas as pd
import subprocess
import os
import time

# --- DIRECTLY IMPORT THE FUNCTIONS ---
# This bypasses the shell/subprocess execution entirely.
try:
    from scraper import hunt_fsbo_deep
    from geocoder import run_geocoder
    SUCCESSFUL_IMPORT = True
except ModuleNotFoundError as e:
    st.error(f"FATAL: One of your helper files failed to import. Check scraper.py or geocoder.py for errors. Details: {e}")
    SUCCESSFUL_IMPORT = False


# --- PAGE SETTINGS ---
st.set_page_config(page_title="MTL FSBO Hunter", page_icon="🏡", layout="centered")

# --- UI HEADER ---
st.title("🏡 FSBO Hunter v1.1") 
st.write("Montreal / NDG / CDN")
st.divider()

# --- EXECUTION LOGIC ---
if SUCCESSFUL_IMPORT:
    if st.button("START HUNT", type="primary"):
        status_box = st.status("Starting the hunt...", expanded=True)
        
        # 1. RUN SCRAPER (Direct Call)
        status_box.write("🕷️ Hunting on DuProprio...")
        # Your scraper function should now save to 'fsbo_listings.csv'
        hunt_fsbo_deep() 
        status_box.write("✅ Scraper finished. (Check logs for DuProprio errors)")

        # 2. RUN GEOCODER (Direct Call)
        status_box.write("📍 Finding GPS Coordinates...")
        # Your geocoder function should now read that CSV and save to 'fsbo_map_data.csv'
        run_geocoder()
        status_box.write("✅ Geocoding finished.")

        status_box.update(label="🎉 Hunt Complete!", state="complete", expanded=False)
        st.rerun()
else:
    st.warning("Cannot start the app due to helper file errors. Please check GitHub console.")


# --- DISPLAY RESULTS ---
st.divider()
st.write("### 📋 Active Listings")

output_file = 'fsbo_map_data.csv'

if os.path.exists(output_file):
    try:
        df = pd.read_csv(output_file)
        st.map(df.dropna(subset=['latitude', 'longitude']), zoom=12)
        
        st.dataframe(
            df[['clean_address', 'price_text', 'link']],
            column_config={"link": st.column_config.LinkColumn("Listing Link")},
            hide_index=True,
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
else:
    st.info("No data found yet. Click 'START HUNT' above.")
