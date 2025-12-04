# --- DISPLAY RESULTS (in app.py) ---
st.divider()
st.write("### 📋 Active Listings")

output_file = 'fsbo_map_data.csv'

if os.path.exists(output_file):
    try:
        df = pd.read_csv(output_file)
        
        # 1. MAP VIEW (Explicitly defining the columns for st.map)
        # We ensure only rows with lat/lon are passed to the map function
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
            st.info("No geocodable data found yet. Try running the hunt again.")

        # 2. LIST VIEW (Rest of the original display logic)
        st.subheader("📋 Listing Details")
        st.dataframe(
            df[['clean_address', 'price_text', 'link']],
            # ... rest of your display configuration ...
        )

    except Exception as e:
        st.error(f"Error reading or displaying data: {e}")
