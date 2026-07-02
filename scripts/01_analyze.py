import json

with open("../data/raw/shl_catalog.json","r",encoding="utf-8") as f:
    data=json.load(f)

print("Total Assessments:",len(data))