import streamlit as st
import pandas as pd
import os
import time

# --- IMPORT HELPER FUNCTIONS ---
# This must happen first to ensure the app can access the logic in the other files.
try:
    # Ensure scraper.py and geocoder.py are in the main repository folder
    from scraper import hunt_fsbo_deep
    from geocoder import run_geocoder
    SUCCESSFUL_IMPORT = True
except ModuleNotFoundError as e:
    st.error(f"FATAL: One of your helper files failed to import. Please check that 'scraper.py' and 'geocoder.py' are committed to the main repository folder. Details: {e}")
    SUCCESSFUL_IMPORT = False


# --- PAGE SETTINGS ---
# v1.3 is the final fix version for the title.
st.set_page_config(page_title="MTL FSBO Hunter v1.3", page_icon="🏡", layout="wide")

# --- HEADER ---
st.title("🏡 FSBO Hunter v1.3") 
st.write("Montreal / NDG / CDN")
st.divider()

# --- EXECUTION LOGIC ---
if SUCCESSFUL_IMPORT:
    if st.button("START HUNT", type="primary"):
        status_box = st.status("Starting the hunt...", expanded=True)
        
        # 1. RUN SCRAPER 
        status_box.write("🕷️ Hunting on DuProprio...")
        try:
            hunt_fsbo_deep() 
            status_box.write("✅ Scraper finished.")
        except Exception as e:
            status_box.error(f"❌ Scraper Execution Failed. Check scraper.py logic or site blocking. Error: {e}")
            st.stop() # Stop execution if scraping failed
        

        # 2. RUN GEOCODER 
        status_box.write("📍 Finding GPS Coordinates...")
        try:
            run_geocoder()
            status_box.write("✅ Geocoding finished.")
        except Exception as e:
            status_box.error(f"❌ Geocoding Failed. Check geocoder.py logic. Error: {e}")
            st.stop() # Stop execution if geocoding failed

        status_box.update(label="🎉 Hunt Complete!", state="complete", expanded=False)
        st.rerun() # Forces the display section to reload and show the new CSV
        

# --- DISPLAY RESULTS ---
st.divider()
st.write("### 📋 Active Listings")

output_file = 'fsbo_map_data.csv'

if os.path.exists(output_file):
    try:
        df = pd.read_csv(output_file)
        
        # 1. MAP VIEW (Robust Map Display)
        # Explicitly converts columns to numeric and drops any NaN rows for the map
        map_df = df.copy()
        map_df['latitude'] = pd.to_numeric(map_df['latitude'], errors='coerce')
        map_df['longitude'] = pd.to_numeric(map_df['longitude'], errors='coerce')
        map_df.dropna(subset=['latitude', 'longitude'], inplace=True)
        
        if not map_df.empty:
            st.subheader(f"📍 Map View ({len(map_df)} Geocoded Listings)")
            
            st.map(
                map_df, 
                latitude='latitude', 
                longitude='longitude', 
                zoom=11, # Forced zoom for local visibility
                use_container_width=True
            )
        else:
            st.warning("All addresses failed geocoding. Data saved, but map cannot be drawn
