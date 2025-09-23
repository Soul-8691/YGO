from collections import Counter
import requests
import json
from dateutil import parser
from tqdm import tqdm

format_library_formats = ['yugi-kaiba', 'critter', 'treasure', 'imperial', 'android', 'joey-pegasus', 'fiber', 'yata', 'scientist', 'vampire', 'chaos', 'warrior', 'goat', 'cyber', 'reaper']

# This code gets the most used decks of all recent events of a particular format
formats_json = open('Format_Library_Formats.json', 'r', encoding='utf8')
formats_json = json.load(formats_json)
formats = list()
formats_dict = dict()

for format in sorted(formats_json, key = lambda x: parser.parse(x['date']).date()):
    if format['name'].lower() in format_library_formats:
        formats.append(format['name'])
        formats_dict[format['name']] = format

site = "https://www.formatlibrary.com"

output_sheets = open('Format_Library_Usage_Stats.tsv', 'w', encoding='utf8')

used_cards = dict()
cumulative = dict()
total = dict()
status = dict()

for f in formats:
    status[f] = dict()
    status[f]['cards'] = set()
    status[f]['card_flags'] = dict()
    finalised_data = dict()
    dt = requests.get(f"{site}/api/events/recent/{f}").json()["events"]
    for event_info in dt:
        print(f"Going through {f + ' ' + event_info['abbreviation']} event's decks")
        event = requests.get(f"{site}/api/events/{event_info['abbreviation']}?isAdmin=false&isSubscriber=false").json()
        decks = []
        finalised_data[event_info["abbreviation"]] = decks
        for deck_info in event["topDecks"]:
            deck = requests.get(f"{site}/api/decks/{deck_info['id']}?isAdmin=false&isSubscriber=false").json()
            try:
                decks.append({
                    "main": [c["name"] for c in deck["main"]],
                    "extra": [c["name"] for c in deck["extra"]],
                    "side": [c["name"] for c in deck["side"]]
                })
                for c in deck["main"]:
                    status[f]['cards'].add(c["name"])
                for c in deck["extra"]:
                    status[f]['cards'].add(c["name"])
                for c in deck["side"]:
                    status[f]['cards'].add(c["name"])
            except Exception as e:
                pass

    cards_all = []
    cards_main = []
    cards_side = []
    cards_extra = []

    for tour in finalised_data:
        for deck in finalised_data[tour]:
            for card in deck['main']:
                cards_main.append(card)
                cards_all.append(card)
                if card not in status[f]['card_flags']:
                    status[f]['card_flags'][card] = 'Main/Side'
            for card in deck['side']:
                cards_side.append(card)
                cards_all.append(card)
                if card not in status[f]['card_flags']:
                    status[f]['card_flags'][card] = 'Main/Side'
            for card in deck['extra']:
                cards_extra.append(card)
                cards_all.append(card)
                if card not in status[f]['card_flags']:
                    status[f]['card_flags'][card] = 'Extra'

    cards_all.sort()
    card_counts = Counter(cards_all).most_common()
    for key, value in card_counts:
        if key not in used_cards:
            used_cards[key] = dict()
            cumulative[key] = 0
            total[key] = 0
        cumulative[key] += value
        total[key] += value
        used_cards[key][f] = {'amount': value, 'amount_weighted': 0, 'cumulative': cumulative[key], 'total': 0}

output_sheets.write('Card\tFormat\tUsage\tUsage (Weighted)\tUsage (%)\tUsage (% - Weighted)\tExtra Deck\tBanlist\tMonth\tDate\tCumulative\tTotal\tIndex\n')

for format in formats:
    dt = requests.get("https://formatlibrary.com/api/banlists/" + formats_dict[format]['banlist'].replace(' ', '%20') + "?category=" + formats_dict[format]['category']).json()
    status[format]['banned'] = set()
    for card_index in range(len(dt['forbidden'])):
        card = dt['forbidden'][card_index]['cardName']
        status[format]['banned'].add(card)
        status[format][card] = dict()
        status[format][card]['banlist'] = 'Forbidden'
        status[format][card]['weight'] = 0
        status[format][card]['month'] = formats_dict[format]['banlist']
        status[format][card]['date'] = formats_dict[format]['date']
    for card_index in range(len(dt['limited'])):
        card = dt['limited'][card_index]['cardName']
        status[format]['banned'].add(card)
        status[format][card] = dict()
        status[format][card]['banlist'] = 'Limited'
        status[format][card]['weight'] = 3
        status[format][card]['month'] = formats_dict[format]['banlist']
        status[format][card]['date'] = formats_dict[format]['date']
    for card_index in range(len(dt['semiLimited'])):
        card = dt['semiLimited'][card_index]['cardName']
        status[format]['banned'].add(card)
        status[format][card] = dict()
        status[format][card]['banlist'] = 'Semi-Limited'
        status[format][card]['weight'] = 3/2
        status[format][card]['month'] = formats_dict[format]['banlist']
        status[format][card]['date'] = formats_dict[format]['date']
    for card in status[format]['cards']:
        if card not in status[format]['banned']:
            status[format][card] = {}
            status[format][card]['banlist'] = 'Unlimited'
            status[format][card]['weight'] = 1
            status[format][card]['month'] = formats_dict[format]['banlist']
            status[format][card]['date'] = formats_dict[format]['date']

for key in used_cards:
    for f in used_cards[key]:
        used_cards[key][f]['total'] = total[key]
        used_cards[key][f]['amount_weighted'] = used_cards[key][f]['amount'] * status[f][key]['weight']

def find_highest_number(data, format):
    highest = float('-inf')  # Initialize with negative infinity

    for key, value in data.items():
        if isinstance(value, dict):
            highest = max(highest, find_highest_number_2(value, format))  # Recursive call

    return highest

def find_highest_number_2(data, format):
    highest = float('-inf')  # Initialize with negative infinity

    for key, value in data.items():
        if isinstance(value, dict) and key == format:
            highest = max(highest, find_highest_number_2(value, format))  # Recursive call
        elif isinstance(value, (int, float)) and key == 'amount':
            highest = max(highest, value)  # Compare if it's a number

    return highest

def find_highest_number_weighted(data, format):
    highest = float('-inf')  # Initialize with negative infinity

    for key, value in data.items():
        if isinstance(value, dict):
            highest = max(highest, find_highest_number_weighted_2(value, format))  # Recursive call

    return highest

def find_highest_number_weighted_2(data, format):
    highest = float('-inf')  # Initialize with negative infinity

    for key, value in data.items():
        if isinstance(value, dict) and key == format:
            highest = max(highest, find_highest_number_weighted_2(value, format))  # Recursive call
        elif isinstance(value, (int, float)) and key == 'amount_weighted':
            highest = max(highest, value)  # Compare if it's a number

    return highest

for card in tqdm(used_cards):
    print(card)
    for format in used_cards[card]:
        max_values = find_highest_number(used_cards, format)
        max_values_weighted = find_highest_number_weighted(used_cards, format)
        output_sheets.write(card + '\t' + format + '\t' + str(used_cards[card][format]['amount']) + '\t' + str(used_cards[card][format]['amount'] * status[format][card]['weight']) + '\t' + str(round((used_cards[card][format]['amount']/max_values)*100, 1)) + '\t' + str(round(((used_cards[card][format]['amount_weighted'])/max_values_weighted)*100, 1)) + '\t' + status[format]['card_flags'][card] + '\t' + status[format][card]['banlist'] + '\t' + status[format][card]['month'] + '\t' + status[format][card]['date'] + '\t' + str(used_cards[card][format]['cumulative']) + '\t' + str(used_cards[card][format]['total']) + '\t' + str(formats.index(format)) + '\n')

output_sheets.close()