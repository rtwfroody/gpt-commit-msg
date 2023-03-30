#!/bin/env python3

import argparse
import openai
import os
import re
import subprocess
import sys
import textwrap
import tiktoken

max_token_count = {
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4097
}

# Set up the OpenAI API client
openai.api_key = os.environ.get("OPENAI_API_KEY")

def gpt(prompt):
    #print("prompt:", repr(prompt))

    assert len(prompt) > 25
    #response = f"{prompt[:300]!r}:{len(prompt)}"
    #return response

    response = openai.ChatCompletion.create(
        model=args.model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    #print("response:", repr(response))

    return response.choices[0]['message']['content']

def token_count(text):
    encoding = tiktoken.encoding_for_model(args.model)
    # tiktoken seems to be undercounting tokens compared to the API
    return len(encoding.encode(text)) * 2

def commit_message(diff):
    prompt = """Write a git commit message for the following. The message
            starts with a one-line summary of 60 characters, then have a
            blank line, and then have a longer but concise description of the
            change."""

    # Simple case. No summarizing needed.
    tcount = token_count(prompt + diff)
    if tcount <= max_token_count[args.model]:
        return gpt(prompt + diff)

    result = []
    summaries = summarize(diff)
    result.extend(summaries)
    summary_string = "\n\n".join(summaries)
    while True:
        if token_count(prompt + summary_string) <= max_token_count[args.model]:
            break
        # Summarize the summary
        summaries = summarize(summary_string)
        result = summaries + ["## More Detail"] + result
        summary_string = "\n\n".join(summaries)
    
    result.insert(0, gpt(prompt + summary_string))
    return "\n\n".join(result)

def summarize(text,
              splitre=[
                r"^(diff )", # First try to split by diff
                "^$",        # Then try blank line
                "\n",        # Then try newline
                ]
                ):
    prompt = "Summarize the following:"
    query = prompt + text
    tcount = token_count(query)

    if tcount <= max_token_count[args.model]:
        return [gpt(prompt + text)]

    summaries = []
    parts = re.split(splitre[0], text, flags=re.MULTILINE)
    combined_parts = []
    # Now go back through and put the split string back together with the next
    # thing
    for part in parts:
        if re.match(splitre[0], part) or not combined_parts:
            combined_parts.append(part)
        else:
            combined_parts[-1] += part
    parts = combined_parts

    chunk = [parts[0]]
    chunk_tcount = token_count(parts[0])
    for part in parts[1:]:
        part_tcount = token_count(part)
        #print(f">>> {splitre[0]!r}",
        #      chunk_tcount,
        #      len(chunk),
        #      part_tcount,
        #      max_token_count[args.model])

        if chunk_tcount + part_tcount >= max_token_count[args.model]:
            text = "".join(chunk)
            chunk = []
            if token_count(text) > max_token_count[args.model]:
                # Need to split using a different regex
                summaries.extend(summarize(text, splitre=splitre[1:]))
            else:
                summaries.append(gpt(prompt + text))
            chunk_tcount = sum(token_count(c) for c in chunk)
        chunk.append(part)
        chunk_tcount += part_tcount
    return summaries

args = None
def main():
    parser = argparse.ArgumentParser(
        description="""Use GPT to create source control commit messages.

        Unless other arguments are passed, reads the diff from stdin.
        """)
    parser.add_argument("--git", "-g", help="Use staged git changes.",
                        action="store_true")
    parser.add_argument("--4", "-4", help="Use GPT4 (slower, costs more money)",
                        dest='gpt4', action="store_true")
    global args
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
        args.model = "gpt-4"
    else:
        args.model = "gpt-3.5-turbo"

    message = commit_message(diff)
    paragraphs = message.split("\n\n")
    wrapped = "\n\n".join(textwrap.fill(p, 80) for p in paragraphs)
    print(wrapped)
    print(f"({args.model})")

if __name__ == "__main__":
    sys.exit(main())
