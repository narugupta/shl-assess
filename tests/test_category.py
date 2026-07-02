from app.planner.extractors.category import CategoryExtractor

extractor = CategoryExtractor()

examples = [

    "Need personality assessment",

    "Looking for coding test",

    "Need technical assessment",

    "Need aptitude test",

    "Need reasoning assessment",

    "Simulation exercise",

    "Need case study",

    "Need competency assessment",

    "Need development assessment",

    "Need situational judgement test",

    "Need Java developer"

]

for text in examples:

    slot = extractor.extract(text)

    print("-" * 60)

    print(text)

    if slot:

        print("Category   :", slot.value)

        print("Matched    :", slot.matched_text)

        print("Confidence :", slot.confidence)

    else:

        print("No category detected")