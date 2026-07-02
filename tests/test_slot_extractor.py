from app.planner.extractors.extractor import SlotExtractor

extractor = SlotExtractor()

message = """
Need a mid-level Java developer assessment
in Spanish under 20 minutes.
"""

slots = extractor.extract(message)

print(slots)