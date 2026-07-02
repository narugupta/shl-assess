from app.planner.extractors.seniority import SeniorityExtractor

extractor = SeniorityExtractor()

examples = [

    "Need assessment for freshers",

    "Hiring junior developers",

    "Graduate recruitment program",

    "Need assessment for experienced Java engineers",

    "Senior Software Engineer",

    "Engineering Manager",

    "Director hiring",

    "Need assessment for CTO",

    "Everyone in the company"

]

for text in examples:

    slot = extractor.extract(text)

    print("-" * 60)

    print(text)

    if slot:

        print("Level      :", slot.value)

        print("Matched    :", slot.matched_text)

        print("Confidence :", slot.confidence)

    else:

        print("No seniority detected")