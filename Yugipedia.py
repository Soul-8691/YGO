import requests
from bs4 import BeautifulSoup
import json
import time
from dotenv import load_dotenv
import os

# Load contact email from .env
load_dotenv()
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "no-email@example.com")

API_URL = "https://yugipedia.com/api.php"
HEADERS = {
    "User-Agent": f"Archetypes and Series (https://github.com/Soul-8691/YGO/; ({CONTACT_EMAIL}))"
}

def fetch_archetype_html(name):
    """Try page name, fallback to (Archetype) and (Series) to get rendered HTML."""
    candidates = [name, f"{name} (Archetype)", f"{name} (Series)"]

    for title in candidates:
        params = {
            "action": "parse",
            "page": title,
            "prop": "text",  # rendered HTML
            "format": "json"
        }
        r = requests.get(API_URL, params=params, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            if "error" not in data:
                return data["parse"]["text"]["*"], title
        time.sleep(1)  # politeness pause
    return None, None

def extract_cards_from_html(html):
    """Extract Members, Support, Anti-Support, and Related cards from navbox HTML."""
    sections = {"Members": [], "Support": [], "Anti-Support": [], "Related": []}
    soup = BeautifulSoup(html, "html.parser")

    # Iterate over navboxes
    for navbox in soup.find_all("div", class_="navbox"):
        table = navbox.find("table", class_="navbox-inner")
        if not table:
            continue

        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th", class_="navbox-group")
            td = row.find("td", class_="navbox-list-with-group")
            if th and td:
                section_name = th.get_text(strip=True).lower()
                if "member" in section_name:
                    key = "Members"
                elif "support" in section_name and "anti" not in section_name:
                    key = "Support"
                elif "anti" in section_name:
                    key = "Anti-Support"
                elif "related" in section_name:
                    key = "Related"
                else:
                    continue

                # Extract all card links
                for li in td.find_all("li"):
                    a = li.find("a")
                    if a and a.get("title"):
                        sections[key].append(a["title"])

    return sections

def main():
    results = {}

    # Read archetype/series names from text file
    with open("Archetypes_Series.txt", "r", encoding="utf-8") as f:
        archetypes = [line.strip() for line in f if line.strip()]

    for name in archetypes:
        print(f"Fetching {name}...")
        html, used_title = fetch_archetype_html(name)
        if html:
            results[name] = extract_cards_from_html(html)
            print(f"  ✓ Found under: {used_title}")
        else:
            print(f"  ✗ No page found for {name}")
        time.sleep(1)  # politeness pause

    # Save output JSON
    with open("Yugipedia_Archetypes_Series_Cards.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("✅ Done! Data saved to Yugipedia_Archetypes_Series_Cards.json")

if __name__ == "__main__":
    main()
