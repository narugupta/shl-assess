from app.planner.extractors.role import RoleExtractor

extractor = RoleExtractor()

examples = [

    "Need Java Developer assessment",

    "Hiring Senior Backend Engineer",

    "Graduate Data Scientist",

    "Looking for Finance Analyst",

    "Need Product Manager",

    "Hiring QA Engineer",

    "Need Principal Software Architect",

    "Customer Success Manager",

    "Need assessment in Spanish"

]

for text in examples:

    slot = extractor.extract(text)

    print("-" * 60)

    print(text)

    if slot:

        print("Role       :", slot.value)

        print("Matched    :", slot.matched_text)

        print("Confidence :", slot.confidence)

    else:

        print("No role detected")