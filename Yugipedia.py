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
        time.sleep(1)
    return None, None

def extract_cards_from_html(html):
    """Extract Members, Support, Anti-Support, Related cards."""
    sections = {"Members": [], "Support": [], "Anti-Support": [], "Related": []}
    soup = BeautifulSoup(html, "html.parser")

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

                for li in td.find_all("li"):
                    a = li.find("a")
                    if a and a.get("title"):
                        sections[key].append(a["title"])

    return sections

def extract_recommended_cards(html):
    """Extract Recommended cards from a Yugipedia decklist."""
    recommended = {"Main Deck": {}, "Extra Deck": {}}
    soup = BeautifulSoup(html, "html.parser")

    # Find the Recommended cards decklist
    decklist_header = soup.find("div", class_="decklist-header", string=lambda t: t and "Recommended cards" in t)
    if not decklist_header:
        return recommended

    # The parent div contains all the columns
    decklist_div = decklist_header.find_parent("div", class_="decklist")
    if not decklist_div:
        return recommended

    decklist_body = decklist_div.find("div", class_="decklist-body")
    if not decklist_body:
        return recommended

    # Iterate columns
    for column in decklist_body.find_all("div", class_="decklist-column"):
        b_tag = column.find("b")
        if not b_tag:
            continue
        top_name = b_tag.get_text(strip=True)

        # Determine deck_type
        if top_name in ["Monster Cards", "Spell Cards", "Trap Cards"]:
            deck_type = "Main Deck"
        else:  # Fusion/Synchro/Xyz/Link
            deck_type = "Extra Deck"

        # Initialize structure
        if deck_type == "Main Deck":
            if top_name not in recommended[deck_type]:
                recommended[deck_type][top_name] = {}
        else:
            if top_name not in recommended[deck_type]:
                recommended[deck_type][top_name] = []

        # Iterate siblings after <b> to get subcategories + cards
        sibling = b_tag.parent.next_sibling
        current_subcat = None
        while sibling:
            if getattr(sibling, 'name', None) is None:
                sibling = sibling.next_sibling
                continue

            # Subcategory <p><a> for Main Deck
            if sibling.name == "p":
                a = sibling.find("a")
                if a:
                    current_subcat = a.get_text(strip=True)
                    if deck_type == "Main Deck":
                        recommended[deck_type][top_name][current_subcat] = []
            # Card list
            elif sibling.name == "ul":
                for li in sibling.find_all("li"):
                    a = li.find("a")
                    if a and a.get("title"):
                        if deck_type == "Main Deck":
                            recommended[deck_type][top_name][current_subcat].append(a["title"])
                        else:
                            recommended[deck_type][top_name].append(a["title"])

                    # Handle nested <ul> inside this <li> (e.g., Bystial monsters)
                    nested_ul = li.find("ul")
                    if nested_ul:
                        for nested_li in nested_ul.find_all("li"):
                            nested_a = nested_li.find("a")
                            if nested_a and nested_a.get("title"):
                                if deck_type == "Main Deck":
                                    recommended[deck_type][top_name][current_subcat].append(nested_a["title"])
                                else:
                                    recommended[deck_type][top_name].append(nested_a["title"])
            sibling = sibling.next_sibling

    return recommended

def main():
    results = {}

    with open("Archetypes_Series.txt", "r", encoding="utf-8") as f:
        archetypes = [line.strip() for line in f if line.strip()]

    for name in archetypes:
        print(f"Fetching {name}...")
        html, used_title = fetch_archetype_html(name)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            results[name] = extract_cards_from_html(html)
            # Add Recommended cards
            results[name]["Recommended"] = extract_recommended_cards(html)
            print(f"  ✓ Found under: {used_title}")
        else:
            print(f"  ✗ No page found for {name}")
        time.sleep(1)

    with open("Yugipedia_Archetypes_Series_Cards.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("✅ Done! Data saved to Yugipedia_Archetypes_Series_Cards.json")

if __name__ == "__main__":
    main()
