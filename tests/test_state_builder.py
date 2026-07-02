from app.planner.builder import ConversationStateBuilder


messages = [

    {

        "role":"user",

        "content":"Need Java Developer"

    }

]

builder = ConversationStateBuilder()

state = builder.build(messages)

# print(state)
print(state.summary())