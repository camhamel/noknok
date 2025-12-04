import requests
import bs4 import BeautifulSoup
import pandas as pd
import time
import random

def hunt_fsbo_deep():
    # --- CONFIGURATION ---
    # NDG / CDN (Code 1883)
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
        # Pagination Logic
        separator = "&" if "?" in base_url else "?"
        target_url = f"{base_url}{separator}pageNumber={page_number}"
        
        print(f"🔎 Scanning Page {page_number}...")
        
        try:
            response = requests.get(target_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- NEW STRATEGY: Find the Listing CARDS first ---
            cards = soup.find_all('li', class_='search-results-listings-list__item')
            
            found_on_page = 0
            
            for card in cards:
                try:
                    # 1. FIND THE LINK
                    link_tag = card.find('a', href=True)
                    if not link_tag:
                        continue
                        
                    href = link_tag['href']
                    
                    # Construct full link
                    if href.startswith("http"):
                        full_link = href
                    else:
                        full_link = f"https://duproprio.com{href}"

                    # Filter: Only want 'a-vendre' or 'for-sale'
                    if "a-vendre" not in full_link and "for-sale" not in full_link:
                        continue

                    if full_link not in properties:
                        # 2. FIND THE PRICE
                        price_text = "Price Unknown"
                        
                        # Strategy A: Look for the specific price class
                        price_tag = card.find(class_='search-results-listings-list__item-description__price')
                        if price_tag:
                            price_text = price_tag.get_text(strip=True).replace('\xa0', ' ')
                        else:
                            # Strategy B: Fallback - Scan all text in card for a '$'
                            for s in card.stripped_strings:
                                if '$' in s:
                                    price_text = s.replace('\xa0', ' ')
                                    break
