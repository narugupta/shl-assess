from app.planner.decision import DecisionEngine

from app.planner.state import ConversationState

from app.planner.intent import Intent


engine = DecisionEngine()

# ----------------------------------------

state = ConversationState()

state.intent = Intent.RECOMMEND

state.needs_clarification = True

state.clarification_question = "What role are you hiring for?"

print(engine.decide(state))

# ----------------------------------------

state = ConversationState()

state.intent = Intent.GREETING

print(engine.decide(state))

# ----------------------------------------

state = ConversationState()

state.intent = Intent.RECOMMEND

print(engine.decide(state))

# ----------------------------------------

state = ConversationState()

state.intent = Intent.COMPARE

print(engine.decide(state))

# ----------------------------------------

state = ConversationState()

state.intent = Intent.OFF_TOPIC

print(engine.decide(state))