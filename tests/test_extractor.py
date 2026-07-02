from pprint import pprint

from app.planner.extractors.extractor import SlotExtractor

extractor = SlotExtractor()

examples = [

    "Need a Spanish Java Developer assessment under 20 minutes",

    "Hiring Senior Backend Engineer",

    "Need personality assessment",

    "Graduate recruitment",

    "Need German assessment for Product Manager",

]

for text in examples:

    print("=" * 70)

    print(text)

    print()

    pprint(extractor.extract_values(text))

    print()

    pprint(extractor.extract_debug(text))