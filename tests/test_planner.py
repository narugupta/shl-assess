from pprint import pprint

from app.planner.planner import Planner

planner = Planner()

# -------------------------------------------------------

messages = [

    {

        "role":"user",

        "content":"Need Java Developer assessment"

    },

    {

        "role":"assistant",

        "content":"What experience level?"

    },

    {

        "role":"user",

        "content":"Mid level"

    },

    {

        "role":"assistant",

        "content":"Language?"

    },

    {

        "role":"user",

        "content":"Spanish"

    },

    {

        "role":"assistant",

        "content":"Anything else?"

    },

    {

        "role":"user",

        "content":"Under 20 minutes"

    }

]

result = planner.plan(messages)

print("=" * 70)

print("ACTION")

print(result.action)

print()

print("MESSAGE")

print(result.message)

print()

print("STATE")

pprint(result.state.summary())

print()

print("DEBUG")

pprint(planner.debug(messages))