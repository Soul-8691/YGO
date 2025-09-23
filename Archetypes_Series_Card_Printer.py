import json

# Input files
yugipedia_file = "Yugipedia_Archetypes_Series_Cards.json"
ygopro_file = "YGOProDeck_Cards.json"
output_file = "Archetypes_Series_Cards.tsv"

# Load Yugipedia archetype data
with open(yugipedia_file, "r", encoding="utf-8") as f:
    archetypes_data = json.load(f)

# Load YGOProDeck data
with open(ygopro_file, "r", encoding="utf-8") as f:
    ygopro_data = json.load(f)["data"]

# Make a dict keyed by card name for quick lookup
card_dict = {card["name"]: card for card in ygopro_data}

# Open output TSV
with open(output_file, "w", encoding="utf-8") as out:
    # Write header
    out.write("Archetype\tDesignation\tName\tKonami_ID\tCard_ID\tType\tAttribute\tRace\tLevel\tATK\tDEF\tDescription\n")

    # Iterate over archetypes
    for archetype_name, sections in archetypes_data.items():
        # Handle top-level sections: Members, Support, Anti-Support, Related
        for designation in ["Members", "Support", "Anti-Support", "Related"]:
            for card_name in sections.get(designation, []):
                card = card_dict.get(card_name)
                if not card:
                    continue
                # Extract card info
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

                out.write(f"{archetype_name}\t{designation}\t{name}\t{konami_id}\t{cid}\t{ctype}\t{attribute}\t{race}\t{level}\t{atk}\t{defe}\t{desc}\n")

        # Handle Recommended cards
        recommended = sections.get("Recommended", {})
        for deck_type in ["Main Deck", "Extra Deck"]:
            for subcat_key, subcat_value in recommended.get(deck_type, {}).items():
                if isinstance(subcat_value, dict):  # Main Deck (Monster/Spell/Trap cards)
                    for sub_subcat, card_list in subcat_value.items():
                        for card_name in card_list:
                            card = card_dict.get(card_name)
                            if not card:
                                continue
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
                            out.write(f"{archetype_name}\tRecommended\t{name}\t{konami_id}\t{cid}\t{ctype}\t{attribute}\t{race}\t{level}\t{atk}\t{defe}\t{desc}\n")
                else:  # Extra Deck (Fusion/Synchro/Xyz/Link)
                    for card_name in subcat_value:
                        card = card_dict.get(card_name)
                        if not card:
                            continue
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
                        out.write(f"{archetype_name}\tRecommended\t{name}\t{konami_id}\t{cid}\t{ctype}\t{attribute}\t{race}\t{level}\t{atk}\t{defe}\t{desc}\n")
