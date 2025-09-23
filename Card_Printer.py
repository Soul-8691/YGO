import json

# Input files
json_file = "YGOProDeck_Cards.json"
cards_file = "Cards.txt"
output_file = "Cards.tsv"

# Load JSON data
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)["data"]

# Make a dictionary keyed by card name for quick lookup
card_dict = {card["name"]: card for card in data}

# Read list of cards from cards.txt
with open(cards_file, "r", encoding="utf-8") as f:
    requested_cards = [line.strip() for line in f if line.strip()]

# Open output file
with open(output_file, "w", encoding="utf-8") as out:
    for card_name in requested_cards:
        card = card_dict.get(card_name)
        if not card:
            # Skip cards not found in JSON
            continue

        # Extract required fields safely
        name = card.get("name", "")
        konami_id = card.get("misc_info", [{}])[0].get("konami_id", "")
        cid = card.get("id", "")
        ctype = card.get("type", "")
        attribute = card.get("attribute", "") or "None"
        race = card.get("race", "")
        level = card.get("level", 0)
        atk = card.get("atk", 0)
        defe = card.get("def", 0)
        desc = card.get("desc", "").replace("\t", "    ").replace("\r\n", "\\n").replace("\n", "\\n")

        # Write in given order, tab-separated
        out.write(f"{name}\t{konami_id}\t{cid}\t{ctype}\t{attribute}\t{race}\t{level}\t{atk}\t{defe}\t{desc}\n")
