import json

# Load the deck types JSON
with open("Format_Library_Decktype_Usage.json", "r", encoding="utf8") as f:
    deck_types = json.load(f)

# Sort each deck type
sorted_deck_types = {}
for deck_type, cards in deck_types.items():
    # Sort by value descending, then key alphabetically
    sorted_cards = dict(
        sorted(cards.items(), key=lambda x: (-x[1], x[0]))
    )
    sorted_deck_types[deck_type] = sorted_cards

# Write the sorted JSON
with open("Deck_Types.json", "w", encoding="utf8") as f:
    json.dump(sorted_deck_types, f, indent=2, ensure_ascii=False)

print("Wrote Deck_Types.json")
