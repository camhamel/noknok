import streamlit as st
import pandas as pd
import os
import time

# --- IMPORT HELPER FUNCTIONS ---
# This must happen after st is defined, but before any UI calls.
try:
    from scraper import hunt_fsbo_deep
    from geocoder import run_geocoder
    SUCCESSFUL_IMPORT = True
except ModuleNotFoundError as e:
    st.error(f"FATAL: One of your helper files failed to import. Details: {e}")
    SUCCESSFUL_IMPORT = False


# --- PAGE SETTINGS ---
st.set_page_config(page_title="MTL FSBO Hunter", page_icon="🏡", layout="wide")

# --- HEADER ---
st.title("🏡 FSBO Hunter v1.2") 
st.write("Montreal / NDG / CDN")
st.divider()

# --- EXECUTION LOGIC ---
if SUCCESSFUL_IMPORT:
    if st.button("START HUNT", type="primary"):
        status_box = st.status("Starting the hunt...", expanded=True)
        
        # 1. RUN SCRAPER 
        status_box.write("🕷️ Hunting on DuProprio...")
        hunt_fsbo_deep() 
        status_box.write("✅ Scraper finished.")

        # 2. RUN GEOCODER 
        status_box.write("📍 Finding GPS Coordinates...")
        run_geocoder()
        status_box.write("✅ Geocoding finished.")

        status_box.update(label="🎉 Hunt Complete! Found 29 locations.", state="complete", expanded=False)
        st.rerun() # Forces the display section to reload and show the new CSV

# --- DISPLAY RESULTS ---
st.divider()
st.write("### 📋 Active Listings")

output_file = 'fsbo_map_data.csv'

if os.path.exists(output_file):
    try:
        df = pd.read_csv(output_file)
        
        # 1. MAP VIEW (Explicitly defining the columns for st.map)
        map_df = df.dropna(subset=['latitude', 'longitude']) 
        
        if not map_df.empty:
            st.subheader(f"📍 Map View ({len(map_df)} Listings)")
            st.map(
                map_df, 
                latitude='latitude', 
                longitude='longitude', 
                zoom=12
            )
        else:
            st.warning("No geocodable data found yet. Try running the hunt again.")

        # 2. LIST VIEW (Data Table)
        st.subheader("📋 Listing Details")
        st.dataframe(
            df[['clean_address', 'price_text', 'link']],
            column_config={
                "link": st.column_config.LinkColumn("Listing Link"),
                "clean_address": "Address",
                "price_text": "Price"
            },
            hide_index=True,
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error reading or displaying data: {e}")
else:
    st.info("No data found yet. Click 'START HUNT' above.")
