import re


def extract_duration(text):

    match = re.search(r"(\d+)\s*minute", text.lower())

    if match:
        return int(match.group(1))

    return None