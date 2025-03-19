#!/usr/bin/env python

import argparse
import os
from typing import List

from google import genai


def read_file_content(file_path: str) -> str | None:
    """
    Reads the content of a file.

    Args:
        file_path: The path to the file.

    Returns:
        The content of the file as a string, or None if the file is not found.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def build_prompt(
        repo_name: str, file_names: List[str], target_file_name: str, initial_prompt: str
) -> str:
    """
    Builds the prompt for the language model.

    Args:
        repo_name: The name of the repository.
        file_names: A list of file names to include in the prompt.
        target_file_name: The name of the target file.
        initial_prompt: The initial prompt.

    Returns:
        The complete prompt as a string.
    """
    prompt = f"{initial_prompt}\n"
    prompt += f"<|repo_name|>{repo_name}\n"

    for file_name in file_names:
        content = read_file_content(file_name)
        if content:
            prompt += f"<|file_sep|>{file_name}\n"
            prompt += f"{content}\n"
            print(f"⫻context/file:{file_name} ({len(content)})")

    prompt += f"<|file_sep|>{target_file_name}\n"
    print(f"⫻content/file:{target_file_name}")

    return prompt


def create_inputs(
        repo_name: str, file_names: List[str], target_file_name: str, initial_prompt: str
) -> List[List[str]]:
    """Creates input list for the model

    Args:
        repo_name: The name of the repository.
        file_names: A list of file names to include in the prompt.
        target_file_name: The name of the target file.
        initial_prompt: The initial prompt.

    Returns:
        A list of lists containing prompt components as strings.
    """

    inputs = [[f"⫻const:repo_name\n{repo_name}", initial_prompt]]

    for file_name in file_names:
        content = read_file_content(file_name)
        if content:
            inputs.append([f"⫻context/file:{file_name}\n{content}"])

    inputs.append([f"Generate {target_file_name}\n"])
    return inputs


def main():
    """
    Main function to parse arguments, build the prompt, and generate content using the language model.
    """
    parser = argparse.ArgumentParser(description='Generate content for a target file based on provided context files.')
    parser.add_argument('--model', type=str, default='gemini-2.0-flash', help='Model name')  # Changed default model
    parser.add_argument('--repo', type=str, default='awesome-ai', help='Repository name')
    parser.add_argument('--prompt', type=str, default='', help='Prompt for the model')
    parser.add_argument('files', nargs='+', help='List of files (context files followed by the target file)')
    args = parser.parse_args()

    repo_name = args.repo
    file_names = args.files[:-1]
    target_file_name = args.files[-1]

    prompt = args.prompt
    print(prompt)

    # Build the prompt using the helper function
    #full_prompt = build_prompt(repo_name, file_names, target_file_name, prompt)

    inputs = create_inputs(repo_name, file_names, target_file_name, prompt)

    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    response = client.models.generate_content_stream(
        model=args.model,  # Using the model name from the command-line arguments
        contents=inputs,
    )

    for part in response:
        print(part.text, end='', flush=True)

    print('')


if __name__ == "__main__":
    main()
