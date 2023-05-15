#!/bin/env python3

import argparse
import re
import subprocess
import sys
import textwrap

import llmlib

max_token_count = {
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4097
}

def commit_message(llm, diff, prompt):
    # Simple case. No summarizing needed.
    tcount = llm.get_num_tokens(prompt + diff)
    if tcount <= max_token_count[args.model]:
        return llm.ask(prompt + diff)

    summaries = summarize(llm, diff)
    result = ["## More Detail"] + summaries
    overall_summary = "\n\n".join(summaries)
    while True:
        if llm.get_num_tokens(prompt + overall_summary) <= max_token_count[args.model]:
            break
        # Summarize the summary
        summaries = summarize(llm, overall_summary,
                prompt="Make an unordered list that summarizes the changes described below.n\n")
        result = summaries + ["## More Detail"] + result
        overall_summary = "\n\n".join(summaries)

    result.insert(0, llm.ask(prompt + overall_summary))
    return "\n\n".join(result)

def summarize(llm,
              text,
              splitre=(
                r"^(diff )", # First try to split by diff
                "^$",        # Then try blank line
                "\n",        # Then try newline
                ),
                prompt="Make an unordered list of the effects of every change in this diff.\n\n"
                ):
    query = prompt + text
    tcount = llm.get_num_tokens(query)

    if tcount <= max_token_count[args.model]:
        return [llm.ask(prompt + text)]

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
    chunk_tcount = llm.get_num_tokens(parts[0])
    for part in parts[1:]:
        part_tcount = llm.get_num_tokens(part)

        if chunk_tcount + part_tcount >= max_token_count[args.model]:
            text = "".join(chunk)
            chunk = []
            if llm.get_num_tokens(text) > max_token_count[args.model]:
                # Need to split using a different regex
                summaries.extend(summarize(llm, text, splitre=splitre[1:], prompt=prompt))
            else:
                summaries.append(llm.ask(prompt + text))
            chunk_tcount = sum(llm.get_num_tokens(c) for c in chunk)
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
    parser.add_argument("--verbose", "-v", help="Print verbose output",
                        action="store_true")
    parser.add_argument("--prompt", "-p", help="Custom prompt to use",
                        action="store",
                        default="""Write a git commit message for the following. The message
                                starts with a one-line summary of 60 characters, followed by a
                                blank line, followed by a longer but concise description of the
                                change.""",
                        )
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

    llm = llmlib.Llm(llmlib.Openai(args.model), verbose=args.verbose)

    message = commit_message(llm, diff, args.prompt)
    paragraphs = message.splitlines()
    wrapped_paragraphs = [textwrap.wrap(p) for p in paragraphs]
    wrapped = "\n".join("\n".join(p) for p in wrapped_paragraphs)
    print(wrapped)
    print(f"({llm.counter_string()})")

    return 0

if __name__ == "__main__":
    sys.exit(main())
