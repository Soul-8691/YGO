import json

def main():
    # Input/Output files
    json_file = "YGOProDeck_Cards.json"
    cards_file = "Cards.txt"
    output_file = "lflist.conf"

    # Load JSON data
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)["data"]

    # Create lookup dictionary {name: id}
    card_dict = {card["name"]: card["id"] for card in data}

    # Read card names from cards.txt
    with open(cards_file, "r", encoding="utf-8") as f:
        card_names = [line.strip() for line in f if line.strip()]

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        for name in card_names:
            if name in card_dict:
                card_id = card_dict[name]
                f.write(f"{card_id} 3 --{name}\n")
            else:
                print(f"Warning: Card '{name}' not found in JSON database.")

if __name__ == "__main__":
    main()
