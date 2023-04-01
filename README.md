# GPT Commit Message Generator

This program is a commit message generator that leverages GPT-4 or GPT-3.5-turbo
to create detailed and informative commit messages for your source control.

## Requirements
* Python 3
* openai
* tiktoken
* An OpenAI API key

## Installation
1. Install the program:
```sh
pip3 install gpt-commit-msg
```
2. Set your OpenAI API key as an environment variable:
```sh
export OPENAI_API_KEY="your_openai_api_key"
```

## Usage
The program can be run in two ways:

1. Piping a diff into the script:
```sh
diff -u old_file new_file | gpt-commit-msg
```
2. Using the --git flag to automatically use staged git changes:
```sh
gpt-commit-msg --git
```
By default, the script uses GPT-3.5-turbo, which is faster and costs less. To use GPT-4 instead, add the -4 flag:
```sh
gpt-commit-msg -4
```

## How It Works
The script reads a diff from either stdin or staged git changes, and then
creates a commit message using OpenAI's GPT. It handles large diffs by splitting
and summarizing the input until it fits within the model's token limit.

The generated commit message will start with a one-line summary of 60
characters, followed by a blank line, and then a longer but concise description
of the changes.

## Editor Integration
### Vim

I use the following two macros in my .vimrc to easily invoke this command when
writing a commit message.
```
command! CommitMsg :r !gpt-commit-msg --git
command! CommitMsg4 :r !gpt-commit-msg --git -4
```

## Notes

Every change description in this project's history also came courtesy of this
script.
