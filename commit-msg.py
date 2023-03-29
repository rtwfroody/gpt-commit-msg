#!/bin/env python3

import argparse
import openai
import os
import subprocess
import sys
import tiktoken

max_token_count = {
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4097
}

# Set up the OpenAI API client
openai.api_key = os.environ["OPENAI_API_KEY"]

def gpt(prompt, model="gpt-3.5-turbo"):
    #print("prompt:", repr(prompt))

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    #print("response:", repr(response))

    return response.choices[0]['message']['content']

def token_count(text, model):
    # tiktoken seems to be undercounting tokens compared to the API
    return len(text)
    #encoding = tiktoken.encoding_for_model(model)
    #return len(encoding.encode(diff))

def summarize(text, model="gpt-3.5-turbo", prompt="Summarize the following:"):
    query = prompt + text
    tcount = token_count(query, model)

    if tcount > max_token_count[model]:
        front = summarize(text[:len(text)//2])
        back = summarize(text[len(text)//2:])
        return front + "\n" + back
    else:
        return gpt(prompt + text)

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

    if args.git:
        diff = (
            subprocess.check_output(['git', 'diff', '--cached']).decode('utf-8'))
    else:
        diff = sys.stdin.read()
    if len(diff) < 5:
        print("Empty diff.")
        return 1

    if args.gpt4:
        model = "gpt-4"
    else:
        model = "gpt-3.5-turbo"

    prompt = """Write a git commit message for the following. The message
            starts with a one-line summary of 60 characters, then have a
            blank line, and then have a longer but concise description of the
            change."""

    print(summarize(diff, model, prompt))
    print(f"({model})")

if __name__ == "__main__":
    sys.exit(main())
