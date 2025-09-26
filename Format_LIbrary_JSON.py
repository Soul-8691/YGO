from collections import defaultdict
import requests
import json
from dateutil import parser
import traceback

format_library_formats = ['goat']

# Load available formats
with open('Format_Library_Formats.json', 'r', encoding='utf8') as f:
    formats_json = json.load(f)

formats = []
formats_dict = {}

for format in sorted(formats_json, key=lambda x: parser.parse(x['date']).date()):
    if format['name'].lower() in format_library_formats:
        formats.append(format['name'])
        formats_dict[format['name']] = format

site = "https://www.formatlibrary.com"

# Data structures
card_usage = defaultdict(dict) # per-format stats
decktype_card_usage = defaultdict(lambda: defaultdict(dict)) # per-decktype stats

for f in formats:
    dt = requests.get(f"{site}/api/events/gallery/{f}").json()["events"]

    for event_info in dt:
        print(f"Processing {f + ' ' + event_info['abbreviation']} event")
        event = requests.get(
            f"{site}/api/events/{event_info['abbreviation']}?isAdmin=false&isSubscriber=false"
        ).json()

        for deck_info in event["topDecks"]:
            deck = requests.get(
                f"{site}/api/decks/{deck_info['id']}?isAdmin=false&isSubscriber=false"
            ).json()

            deck_type = deck_info.get("deckTypeName", "Unknown")

            try:
                for section in ("main", "side", "extra"):
                    for c in deck[section]:
                        name = c["name"]

                        # Per-format stats
                        if section not in card_usage[name]:
                            card_usage[name][section] = 0
                        card_usage[name][section] += 1

                        # Per-decktype stats
                        if section not in decktype_card_usage[deck_type][name]:
                            decktype_card_usage[deck_type][name][section] = 0
                        decktype_card_usage[deck_type][name][section] += 1

                # Update totals after processing all sections
                for card_name in set(c["name"] for s in ("main", "side", "extra") for c in deck[s]):
                    counts = {
                        sec: card_usage[card_name][sec]
                        for sec in ("main", "side", "extra")
                        if sec in card_usage[card_name]
                    }
                    if "extra" in counts and len(counts) == 1:
                        total_val = counts["extra"]
                    else:
                        total_val = counts.get("main", 0) + counts.get("side", 0)
                    card_usage[card_name]["total"] = total_val

                    # Do the same for decktype
                    counts_dt = {
                        sec: decktype_card_usage[deck_type][card_name][sec]
                        for sec in ("main", "side", "extra")
                        if sec in decktype_card_usage[deck_type][card_name]
                    }
                    if "extra" in counts_dt and len(counts_dt) == 1:
                        total_val_dt = counts_dt["extra"]
                    else:
                        total_val_dt = counts_dt.get("main", 0) + counts_dt.get("side", 0)
                    decktype_card_usage[deck_type][card_name]["total"] = total_val_dt

            except Exception:
                traceback.print_exc()
                continue

# Clean up: remove empty sections (main/side/extra that never appeared)
def prune_empty(d):
    return {
        k: v for k, v in d.items()
        if not (k in ("main", "side", "extra") and v == {})
    }

card_usage_clean = {card: prune_empty(data) for card, data in card_usage.items()}
decktype_card_usage_clean = {
    decktype: {card: prune_empty(data) for card, data in cards.items()}
    for decktype, cards in decktype_card_usage.items()
}

# Save per-format stats
with open("Format_Library_Usage_Stats.json", "w", encoding="utf8") as f_out:
    json.dump(card_usage_clean, f_out, indent=2, ensure_ascii=False)

# Save per-decktype stats
with open("Format_Library_Decktype_Usage.json", "w", encoding="utf8") as f_out:
    json.dump(decktype_card_usage_clean, f_out, indent=2, ensure_ascii=False)

print("Wrote Format_Library_Usage_Stats.json and Format_Library_Decktype_Usage.json")
