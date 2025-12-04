import streamlit as st
import pandas as pd
import os
import time

# --- IMPORT HELPER FUNCTIONS ---
# This structure imports the functions directly, bypassing the problematic 'subprocess' calls.
try:
    from scraper import hunt_fsbo_deep
    from geocoder import run_geocoder
    SUCCESSFUL_IMPORT = True
except Exception:
    SUCCESSFUL_IMPORT = False


# --- PAGE SETTINGS ---
st.set_page_config(page_title="MTL FSBO Hunter v1.3", page_icon="🏡", layout="wide")

# --- HEADER ---
st.title("🏡 FSBO Hunter v1.3") 
st.write("Montreal / NDG / CDN")
st.divider()

# --- EXECUTION LOGIC ---
if SUCCESSFUL_IMPORT:
    # Use st.session_state to prevent the search from running every time the page refreshes
    if 'data_status' not in st.session_state:
        st.session_state.data_status = "READY"

    if st.button("START HUNT", type="primary"):
        st.session_state.data_status = "RUNNING"
        
        # Display the status box
        with st.status("Starting the hunt...", expanded=True) as status_box:
            
            # 1. RUN SCRAPER 
            status_box.write("🕷️ Hunting on DuProprio...")
            try:
                hunt_fsbo_deep() 
                status_box.write("✅ Scraper finished.")
            except Exception as e:
                status_box.error(f"❌ Scraper Execution Failed. Error: {e}")
                st.session_state.data_status = "FAILED"
                st.stop()
            
            # 2. RUN GEOCODER 
            status_box.write("📍 Finding GPS Coordinates...")
            try:
                run_geocoder()
                status_box.write("✅ Geocoding finished.")
            except Exception as e:
                status_box.error(f"❌ Geocoding Failed. Error: {e}")
                st.session_state.data_status = "FAILED"
                st.stop()
            
            st.session_state.data_status = "SUCCESS"
            status_box.update(label="🎉 Hunt Complete!", state="complete", expanded=False)
            time.sleep(1)
            st.rerun() # Forces the app to reload and display the new CSV

# --- DISPLAY RESULTS ---
st.divider()
st.write("### 📋 Active Listings")

output_file = 'fsbo_map_data.csv'

if not SUCCESSFUL_IMPORT:
    st.error("CRITICAL ERROR: Application files (scraper.py or geocoder.py) could not be loaded. Please re-commit the latest clean versions.")
elif os.path.exists(output_file):
    try:
        df = pd.read_csv(output_file)
        
        # 1. MAP VIEW (Robust Map Display)
        map_df = df.copy()
        # Convert columns to numeric, coercing errors to NaN
        map_df['latitude'] = pd.to_numeric(map_df['latitude'], errors='coerce')
        map_df['longitude'] = pd.to_numeric(map_df['longitude'], errors='coerce')
        map_df.dropna(subset=['latitude', 'longitude'], inplace=True)
        
        if not map_df.empty:
            st.subheader(f"📍 Map View ({len(map_df)} Geocoded Listings)")
            
            # This map configuration ensures a good view of Montreal and uses the correct column names
            st.map(
                map_df, 
                latitude='latitude', 
                longitude='longitude', 
                zoom=11, 
                use_container_width=True
            )
        else:
            # FIX FOR SYNTAX ERROR: The string is properly closed with a quote mark
            st.warning("All addresses failed geocoding. Data saved, but map cannot be drawn.") 

        # 2. LIST VIEW (Data Table with Clickable Links)
        st.subheader("📋 Listing Details")
        st.dataframe(
            df,
            column_config={
                "link": st.column_config.LinkColumn(
                    "Listing Link",
                    help="Click to view DuProprio listing",
                    display_text="View Listing" 
                ),
                "clean_address": "Address",
                "price_text": "Price"
            },
            hide_index=True,
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error reading or displaying data. Try running 'START HUNT' again. Error: {e}")
else:
    st.info("No data found yet. Click 'START HUNT' above.")
