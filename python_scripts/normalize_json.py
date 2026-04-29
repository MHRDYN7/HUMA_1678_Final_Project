import json

filename = r"..\data\laureates_after_2000.json"

with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)


with open(filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
