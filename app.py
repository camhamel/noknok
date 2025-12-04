import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def hunt_fsbo_deep():
    # --- CONFIGURATION ---
    # I have pre-filled your specific NDG/CDN French Link below:
    base_url = "https://duproprio.com/fr/rechercher/liste?search=true&cities%5B0%5D=1883&parent=1&sort=-published_at"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    properties = {}
    page_number = 1
    keep_hunting = True

    print(f"🚀 STARTING DEEP HUNT: NDG (Code 1883)")
    print("="*40)

    while keep_hunting:
        # Handle the ? vs & in the URL for pagination
        separator = "&" if "?" in base_url else "?"
        target_url = f"{base_url}{separator}pageNumber={page_number}"
        
        print(f"🔎 Scanning Page {page_number}...")
        
        try:
            response = requests.get(target_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.find_all('a', href=True)
            found_on_page = 0
            
            for link in links:
                href = link['href']
                text = link.get_text().strip()
                
                # FILTER: Look for English OR French listing keywords
                if ("for-sale" in href or "a-vendre" in href) and "search" not in href:
                    
                    if href.startswith("http"):
                        full_link = href
                    else:
                        full_link = f"https://duproprio.com{href}"
                    
                    if full_link not in properties:
                        # Extract Address Logic
                        try:
                            # The address is usually after the last slash and 'hab-' or 'prop-'
                            slug = full_link.split("/")[-1]
                            # Remove the listing ID numbers at the end
                            parts = slug.split("-")
                            
                            # Sometimes the slug starts with 'hab' or 'prop', we ignore that
                            if parts[0] in ['hab', 'prop']:
                                address_parts = parts[1:-1]
                            else:
                                address_parts = parts[:-1]
                                
                            clean_address = " ".join(address_parts).title()
                        except:
                            clean_address = "Address Unknown"

                        properties[full_link] = {
                            "Address": clean_address,
                            "Price_Text": text if "$" in text else "Voir Lien",
                            "Link": full_link
                        }
                        found_on_page += 1

            print(f"   found {found_on_page} new listings.")

            if found_on_page == 0:
                print("🛑 No more results found. Stopping.")
                keep_hunting = False
            else:
                page_number += 1
                # Sleep 2-4 seconds to be polite
                time.sleep(random.uniform(2.0, 4.0))
                
                # Safety Brake
                if page_number > 20: 
                    print("⚠️ Reached 20 page limit. Stopping for safety.")
                    keep_hunting = False

        except Exception as e:
            print(f"❌ ERROR on Page {page_number}: {e}")
            keep_hunting = False

    # SAVE RESULTS
    df = pd.DataFrame(properties.values())
    if not df.empty:
        df = df[df['Address'] != ""]
        df.to_csv("fsbo_listings.csv", index=False)
        print("="*40)
        print(f"🎉 GRAND TOTAL: Found {len(df)} listings in NDG.")
        print(f"💾 Saved to 'fsbo_listings.csv'")
    else:
        print("❌ No listings found.")

if __name__ == "__main__":
    hunt_fsbo_deep()