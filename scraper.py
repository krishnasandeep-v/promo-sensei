from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time
import random

# For stealth plugin (install: pip install playwright-stealth)
from playwright_stealth import stealth_sync

# Function to simulate human-like scrolling
def scroll_down_page(page, scroll_attempts=3):
    for i in range(scroll_attempts):
        print(f"Scrolling down... Attempt {i+1}")
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        page.wait_for_timeout(random.randint(2000, 4000)) # Wait for content to load after scroll

def scrape_flipkart():
    print("Scraping Flipkart...")
    offers = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, # Keep headless True for deployment, False for debugging
            args=["--no-sandbox", "--disable-setuid-sandbox"] # Recommended for some environments
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", # Slightly updated UA
            viewport={"width": 1920, "height": 1080}, # Set a common viewport size
            locale="en-GB"
        )
        stealth_sync(page) # Apply stealth settings

        try:
            print("Navigating to Flipkart...")
            page.goto("https://www.flipkart.com/offers-store", timeout=90000, wait_until="domcontentloaded")
            # Changed wait_until to domcontentloaded - faster initial load, then wait for specific elements
            print("Waiting for Flipkart content...")
            # We'll try to wait for common elements, and then scroll if necessary
            page.wait_for_selector("div[data-tracking-id], ._2pYq6y, ._3CuAg8, ._1MRP_S", timeout=45000) # Wait for broader element
            scroll_down_page(page, scroll_attempts=2) # Scroll to load more dynamic content
            page.wait_for_timeout(random.randint(3000, 7000)) # Random delay

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Flipkart specific selectors - often dynamic or nested
            # Look for common offer card patterns or specific sections
            blocks = soup.find_all("div", class_="_2pYq6y") # Primary offer card
            if not blocks:
                blocks = soup.find_all("a", class_="_3CuAg8") # Another common card/link
            if not blocks:
                # Look for generic promo banners or sections if individual cards are hard to find
                blocks = soup.find_all("div", class_="_1MRP_S") # A common module class for various content

            for block in blocks:
                title = block.find("div", class_="_3LU4EM")
                description = block.find("div", class_="_2TVI3u")
                link_tag = block.find("a", href=True)

                if title and description:
                    offers.append({
                        "title": title.get_text(strip=True),
                        "description": description.get_text(strip=True),
                        "expiry_date": None,
                        "brand": "Flipkart",
                        "link": "https://www.flipkart.com" + link_tag['href'] if link_tag and link_tag['href'].startswith('/') else (link_tag['href'] if link_tag else "https://www.flipkart.com/offers-store")
                    })
                # If the above didn't find, try a more generic approach for titles and descriptions within a block
                elif title and not description: # Sometimes only title is prominent
                    offers.append({
                        "title": title.get_text(strip=True),
                        "description": "See offer for details",
                        "expiry_date": None,
                        "brand": "Flipkart",
                        "link": "https://www.flipkart.com" + link_tag['href'] if link_tag and link_tag['href'].startswith('/') else (link_tag['href'] if link_tag else "https://www.flipkart.com/offers-store")
                    })
                elif not title and link_tag: # Sometimes only link text acts as title
                    text_content = block.get_text(separator=" ", strip=True)
                    if text_content:
                        offers.append({
                            "title": text_content[:100], # Take first 100 chars as title
                            "description": "Details on offer page",
                            "expiry_date": None,
                            "brand": "Flipkart",
                            "link": "https://www.flipkart.com" + link_tag['href'] if link_tag and link_tag['href'].startswith('/') else (link_tag['href'] if link_tag else "https://www.flipkart.com/offers-store")
                        })
        except Exception as e:
            print(f"Flipkart page load or scraping failed: {type(e).__name__}: {e}")
        finally:
            browser.close()
    print(f"Flipkart offers found: {len(offers)}")
    return offers

def scrape_nykaa():
    print("Scraping Nykaa...")
    offers = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-GB"
        )
        stealth_sync(page)

        try:
            print("Navigating to Nykaa...")
            # For HTTP2_PROTOCOL_ERROR, sometimes retrying or ensuring a clean start helps.
            # No easy code fix for this network error; often external (IP/server)
            page.goto("https://www.nykaa.com/offers", timeout=90000, wait_until="domcontentloaded")
            print("Waiting for Nykaa content...")
            page.wait_for_selector(".offer-card, .css-1h7lj8m, [data-prod-id]", timeout=45000)
            scroll_down_page(page, scroll_attempts=2)
            page.wait_for_timeout(random.randint(3000, 7000))

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            blocks = soup.find_all("div", class_="offer-card")
            if not blocks:
                blocks = soup.find_all("div", class_="css-1h7lj8m")
            if not blocks: # More generic search for products or sections if cards fail
                blocks = soup.find_all("div", attrs={"data-prod-id": True})


            for block in blocks:
                title_elem = block.find(["h3", "h4", "div"], class_=re.compile(r'title|heading', re.I)) # More flexible title
                desc_elem = block.find("p", class_=re.compile(r'description|text', re.I)) # More flexible description
                link_elem = block.find("a", href=True)

                title = title_elem.get_text(strip=True) if title_elem else "No Title"
                description = desc_elem.get_text(strip=True) if desc_elem else "No Description"
                link = "https://www.nykaa.com" + link_elem['href'] if link_elem and link_elem['href'].startswith('/') else (link_elem['href'] if link_elem else "https://www.nykaa.com/offers")

                expiry = None
                text = block.get_text(separator=" ").strip()
                expiry_match = re.search(r'valid\s+till\s+(\d{1,2}\s+\w+\s+\d{4})', text, re.IGNORECASE)
                if expiry_match:
                    expiry = expiry_match.group(1)
                elif re.search(r'expires\s+on\s+(\d{1,2}\s+\w+\s+\d{4})', text, re.IGNORECASE):
                    expiry = re.search(r'expires\s+on\s+(\d{1,2}\s+\w+\s+\d{4})', text, re.IGNORECASE).group(1)


                if title != "No Title" or description != "No Description": # Only add if some content is found
                    offers.append({
                        "title": title,
                        "description": description,
                        "expiry_date": expiry,
                        "brand": "Nykaa",
                        "link": link
                    })
        except Exception as e:
            print(f"Nykaa page load or scraping failed: {type(e).__name__}: {e}")
        finally:
            browser.close()
    print(f"Nykaa offers found: {len(offers)}")
    return offers

def scrape_puma():
    print("Scraping Puma...")
    offers = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-GB"
        )
        stealth_sync(page)

        try:
            print("Navigating to Puma...")
            page.goto("https://in.puma.com/in/en/deals", timeout=90000, wait_until="domcontentloaded")
            print("Waiting for Puma content...")
            page.wait_for_selector(".product-tile, .deal-block, [data-category-id]", timeout=45000) # Broader selector for product list
            scroll_down_page(page, scroll_attempts=2)
            page.wait_for_timeout(random.randint(3000, 7000))

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            blocks = soup.find_all("div", class_="product-tile")
            if not blocks:
                blocks = soup.find_all("div", class_="deal-block")
            if not blocks:
                # Look for product containers
                blocks = soup.find_all("div", class_=re.compile(r'product-grid-item|pdp-wrapper', re.I))


            for block in blocks:
                title_elem = block.find(["h1", "h2", "h3", "h4", "div"], class_=re.compile(r'product-name|title|heading', re.I))
                desc_elem = block.find(["div", "span", "p"], class_=re.compile(r'discount|price|description', re.I))
                link_tag = block.find("a", href=True)

                title = title_elem.get_text(strip=True) if title_elem else "No Title"
                description = desc_elem.get_text(strip=True) if desc_elem else "No Description"
                link = "https://in.puma.com" + link_tag['href'] if link_tag and link_tag['href'].startswith('/') else (link_tag['href'] if link_tag else "https://in.puma.com/in/en/deals")

                if title != "No Title" or description != "No Description":
                    offers.append({
                        "title": title,
                        "description": description,
                        "expiry_date": None,
                        "brand": "Puma",
                        "link": link
                    })
        except Exception as e:
            print(f"Puma page load or scraping failed: {type(e).__name__}: {e}")
        finally:
            browser.close()
    print(f"Puma offers found: {len(offers)}")
    return offers

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    all_offers = []
    all_offers.extend(scrape_flipkart())
    all_offers.extend(scrape_nykaa())
    all_offers.extend(scrape_puma())

    with open("data/raw_offers.json", "w", encoding="utf-8") as f:
        json.dump(all_offers, f, indent=2, ensure_ascii=False)

    print(f"Total offers scraped: {len(all_offers)}")