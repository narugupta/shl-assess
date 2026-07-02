from pprint import pprint

from app.planner.history import ConversationHistoryBuilder

builder = ConversationHistoryBuilder()

messages = [

    {
        "role": "user",
        "content": "Need Java Developer assessment"
    },

    {
        "role": "assistant",
        "content": "What experience level?"
    },

    {
        "role": "user",
        "content": "Mid level"
    },

    {
        "role": "assistant",
        "content": "Which language?"
    },

    {
        "role": "user",
        "content": "Spanish"
    },

    {
        "role": "assistant",
        "content": "Anything else?"
    },

    {
        "role": "user",
        "content": "Under 20 minutes"
    }

]

state = builder.build(messages)

print("\nConversation State\n")

pprint(state.summary())

print("\nExtracted Slots\n")

pprint(state.extracted_slots)

print("\nHistory\n")

pprint(state.history_summary)