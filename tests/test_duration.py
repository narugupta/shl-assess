from app.planner.extractors.duration import DurationExtractor

extractor = DurationExtractor()

examples = [

    "Need assessment under 20 minutes",

    "Maximum 30 min",

    "Less than 45 mins",

    "Need 25 minutes",

    "Half hour assessment",

    "One hour assessment",

    "Need Java developer"

]

for text in examples:

    slot = extractor.extract(text)

    print("-" * 60)
    print(text)

    if slot:
        print("Minutes :", slot.value)
        print("Operator:", slot.operator)
    else:
        print("No duration found")