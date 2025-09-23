import requests, json

url = "https://dawnbrandbots.github.io/yaml-yugi/cards.json"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()  # parse into Python dict/list
    
    # Save with pretty printing (tabs for indentation)
    with open("YAML_Yugi.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("Downloaded and pretty-printed cards.json successfully!")
else:
    print(f"Failed to download. Status code: {response.status_code}")
