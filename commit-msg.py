#!/bin/env python3

import openai
import os
import sys

# Set up the OpenAI API client
openai.api_key = os.environ["OPENAI_API_KEY"]

def gpt3_5(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0]['message']['content']

if __name__ == "__main__":
    prompt = """Write a git commit message for the following diff. The message
            must start with a one-line summary of 60 characters, then have a
            blank line, and then have a longer but concise description of the
            change."""
    prompt += "Here's the diff:"
    prompt += sys.stdin.read()
    print(gpt3_5(prompt))
