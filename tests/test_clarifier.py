from pprint import pprint

from app.planner.clarifier import Clarifier

from app.planner.state import ConversationState

from app.planner.intent import Intent


clarifier = Clarifier()

# --------------------------------------------------

state = ConversationState()

state.intent = Intent.RECOMMEND

print("=" * 60)

print("Empty State")

clarifier.update_state(state)

pprint(state.summary())

# --------------------------------------------------

state = ConversationState()

state.intent = Intent.RECOMMEND

state.role = "Java Developer"

print("=" * 60)

print("Role Present")

clarifier.update_state(state)

pprint(state.summary())

# --------------------------------------------------

state = ConversationState()

state.intent = Intent.COMPARE

print("=" * 60)

print("Comparison")

clarifier.update_state(state)

print(state.clarification_question)