from app.planner.state import ConversationState

state = ConversationState()

print("Empty State")
print(state)

print()

state.role = "Java Developer"
state.seniority = "Mid-Professional"
state.language = "Spanish"

state.add_skill("Java")
state.add_skill("Spring")
state.add_skill("Java")          # duplicate ignored

state.add_category("Knowledge & Skills")

print("Updated State")
print(state)

print()

print(state.to_dict())