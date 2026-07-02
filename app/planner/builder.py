from app.planner.state import ConversationState
from app.planner.extractors.extractor import SlotExtractor


class ConversationStateBuilder:
    def __init__(self):
        self.state = ConversationState()
        self.extractor = SlotExtractor()

    def reset(self):
        self.state = ConversationState()

    def build(self, messages):
        """
        Build conversation state from the
        entire message history.
        """

        self.reset()

        # Get slots from the latest user message
        slots = self.extractor.extract(messages[-1]["content"])

        self.state.role = slots["role"]
        self.state.seniority = slots["seniority"]
        self.state.language = slots["language"]
        self.state.duration = slots["duration"]

        return self.state