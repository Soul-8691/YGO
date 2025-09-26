import json

# Load the source JSON
with open("json/FL_Usage.json", "r", encoding="utf8") as f:
    data = json.load(f)

# Transform into desired structure
output = {}
for entry in data:
    card_name = entry["Card"]
    # Convert to float first, then round to nearest integer
    usage = round(float(entry["Usage"]))
    usage_weighted = round(float(entry["Usage (Weighted)"]))
    output[card_name] = {
        "usage": usage,
        "usage_weighted": usage_weighted
    }

# Write new JSON
with open("json/FL_Usage_Stats.json", "w", encoding="utf8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("Wrote FL_Usage_Stats.json")
