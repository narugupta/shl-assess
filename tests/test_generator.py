from app.generation.generator import LLMGenerator

from app.generation.prompts import PromptType

generator = LLMGenerator()

context = """
Assessment 1

Name: Java Programming

Duration: 30 minutes

Languages: English (USA)

Categories: Knowledge & Skills

Description:
Measures Java programming knowledge.

URL:
https://www.shl.com/example
"""

result = generator.generate(

    PromptType.RECOMMEND,

    "Need Java Developer assessment",

    context

)

print()

print("=" * 80)

print(result.answer)