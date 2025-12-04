import streamlit as st
import pandas as pd
import subprocess
import os
import time
import pandas as pd # KEEP THIS LINE
import streamlit as st 
# ... rest of the app.py code

# --- PAGE SETTINGS ---
st.set_page_config(page_title="MTL FSBO Hunter", page_icon="🏡", layout="centered")

# --- HEADER ---
st.title("🏡 FSBO Hunter v.0.1")
st.write("Montreal / NDG / CDN")

# --- ACTION SECTION ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### 🚀 Update Listings")
    st.caption("Runs Scraper + Geocoder")

with col2:
    start_btn = st.button("START HUNT", type="primary")

# --- EXECUTION LOGIC ---
if start_btn:
    status_box = st.status("Starting the hunt...", expanded=True)
    
    # 1. RUN SCRAPER
    status_box.write("🕷️ Hunting on DuProprio (scraper.py)...")
    try:
        # Run scraper.py
        result_scraper = subprocess.run(["python", "scraper.py"], capture_output=True, text=True)
        # Check if it worked
        if result_scraper.returncode == 0:
            status_box.write("✅ Scraper finished.")
        else:
            status_box.error("❌ Scraper failed.")
            st.code(result_scraper.stderr) # Show error details
    except Exception as e:
        status_box.error(f"Could not run scraper: {e}")

    # 2. RUN GEOCODER
    status_box.write("📍 Finding GPS Coordinates (geocoder.py)...")
    try:
        # Run geocoder.py
        result_geo = subprocess.run(["python", "geocoder.py"], capture_output=True, text=True)
        if result_geo.returncode == 0:
            status_box.write("✅ Geocoding finished.")
        else:
            status_box.error("❌ Geocoder failed.")
            st.code(result_geo.stderr)
    except Exception as e:
        status_box.error(f"Could not run geocoder: {e}")

    status_box.update(label="🎉 Hunt Complete!", state="complete", expanded=False)
    time.sleep(1)
    st.rerun()

# --- DISPLAY RESULTS ---
st.divider()
st.write("### 📋 Active Listings")

output_file = 'fsbo_map_data.csv' 

if os.path.exists(output_file):
    try:
        df = pd.read_csv(output_file)
        
        # 1. MAP VIEW
        if 'latitude' in df.columns and 'longitude' in df.columns:
            st.map(df.dropna(subset=['latitude', 'longitude']), zoom=12)
        else:
            st.warning("Map data missing (lat/lon).")

        # 2. LIST VIEW
        display_cols = ['clean_address', 'price_text', 'link']
        # Filter to exist columns only
        valid_cols = [c for c in display_cols if c in df.columns]

        st.dataframe(
            df[valid_cols],
            column_config={
                "link": st.column_config.LinkColumn("Listing Link"),
                "clean_address": "Address",
                "price_text": "Price"
            },
            hide_index=True,
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
else:
    st.info("No data found yet. Click 'START HUNT' above.")
