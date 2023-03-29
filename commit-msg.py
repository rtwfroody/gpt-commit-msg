#!/bin/env python3

import argparse
import openai
import os
import subprocess
import sys

# Set up the OpenAI API client
openai.api_key = os.environ["OPENAI_API_KEY"]

def gpt(prompt, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0]['message']['content']

def main():
    parser = argparse.ArgumentParser(
        description="""Use GPT to create source control commit messages.

        Unless other arguments are passed, reads the diff from stdin.
        """)
    parser.add_argument("--git", "-g", help="Use staged git changes.",
                        action="store_true")
    parser.add_argument("--4", "-4", help="Use GPT4 (slower, costs more money)",
                        dest='gpt4', action="store_true")
    args = parser.parse_args()

    prompt = """Write a git commit message for the following diff. The message
            must start with a one-line summary of 60 characters, then have a
            blank line, and then have a longer but concise description of the
            change."""
    prompt += "Here's the diff:"

    if args.git:
        diff = (
            subprocess.check_output(['git', 'diff', '--cached']).decode('utf-8'))
    else:
        diff = sys.stdin.read()
    if len(diff) < 5:
        print("Empty diff.")
        return 1
    prompt += diff
    if args.gpt4:
        print(gpt(prompt, model="gpt-4"))
    else:
        print(gpt(prompt))

if __name__ == "__main__":
    sys.exit(main())
