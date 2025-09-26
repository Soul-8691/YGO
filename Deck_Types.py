from collections import defaultdict, Counter
import requests
import json
from dateutil import parser

format_library_formats = ['goat']

formats_json = open('Format_Library_Formats.json', 'r', encoding='utf8')
formats_json = json.load(formats_json)

formats = []
formats_dict = {}

for format in sorted(formats_json, key=lambda x: parser.parse(x['date']).date()):
    if format['name'].lower() in format_library_formats:
        formats.append(format['name'])
        formats_dict[format['name']] = format

site = "https://www.formatlibrary.com"

# New dict: { deckTypeName: Counter() }
decktype_card_usage = defaultdict(Counter)

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

            # Tally all cards from main, side, extra
            for section in ("main", "extra", "side"):
                for card in deck[section]:
                    decktype_card_usage[deck_type][card["name"]] += 1

# Convert Counters to normal dicts for JSON
decktype_card_usage_json = {
    decktype: dict(counter) for decktype, counter in decktype_card_usage.items()
}

with open("Format_Library_Decktype_Usage.json", "w", encoding="utf8") as f_out:
    json.dump(decktype_card_usage_json, f_out, indent=2, ensure_ascii=False)

print("Wrote Format_Library_Decktype_Usage.json")
