from app.planner.extractors.language import LanguageExtractor

extractor = LanguageExtractor()

examples = [

    "Need assessment in Spanish",

    "French language test",

    "German assessment",

    "English (USA)",

    "English International",

    "Japanese developers",

    "Italian assessment",

    "Need Java developer"

]

for text in examples:

    slot = extractor.extract(text)

    print("-" * 60)

    print(text)

    if slot:

        print("Language   :", slot.value)

        print("Matched    :", slot.matched_text)

        print("Confidence :", slot.confidence)

    else:

        print("No language detected")