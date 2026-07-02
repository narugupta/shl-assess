from app.generation.prompts import (
    PromptManager,
    PromptType,
)

manager = PromptManager()

context = """
Assessment 1

Java Programming

Duration: 30 minutes

Language: English (USA)

Reason:
Measures Java programming skills.
"""

query = "Need a Java Developer assessment"

print("=" * 80)
print("SYSTEM PROMPT")
print("=" * 80)
print(manager.get_system_prompt())

print()

print("=" * 80)
print("RECOMMENDATION PROMPT")
print("=" * 80)
print(

    manager.build_prompt(

        PromptType.RECOMMEND,

        query,

        context

    )

)

print()

print("=" * 80)
print("COMPARE PROMPT")
print("=" * 80)
print(

    manager.build_prompt(

        PromptType.COMPARE,

        "Compare Java and .NET assessments",

        context

    )

)