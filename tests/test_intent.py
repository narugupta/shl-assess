from app.planner.intent import detect_intent

examples = [

    "Need Java developer assessment",

    "Compare OPQ and GSA",

    "Actually add personality tests",

    "Here is the job description",

    "Hi",

    "Help",

    "Tell me a joke"

]

for message in examples:

    print(message)

    print(detect_intent(message))

    print("-" * 40)