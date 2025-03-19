#!/usr/bin/env python

import argparse
import os
import logging
import json
from typing import List

from google.genai import Client
from google.genai.types import GenerateContentConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
            content = file.read()
            logging.debug(json.dumps({"file_read": file_path, "status": "success", "length": len(content)}))
            return content
    except FileNotFoundError:
        logging.error(json.dumps({"file_read": file_path, "status": "failed", "error": "File not found"}))
        print(f"File not found: {file_path}")  # Keep the print for user feedback as well
        return None
    except Exception as e:
        logging.exception(json.dumps({"file_read": file_path, "status": "failed", "error": str(e)}))
        print(f"Error reading file {file_path}: {e}") # Keep the print for user feedback
        return None


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

    inputs = [[initial_prompt, f"⫻const:repo_name\n{repo_name}"]]
    logging.debug(json.dumps({"inputs_init": True, "repo_name": repo_name}))

    for file_name in file_names:
        content = read_file_content(file_name)
        if content:
            inputs.append([f"⫻context/file:{file_name}\n{content}"])
            logging.debug(json.dumps({"input_file_added": file_name, "length": len(content)}))

    inputs.append([f"Generate {target_file_name}\n"])
    logging.debug(json.dumps({"target_file": target_file_name, "action": "generate"}))
    return inputs


def main():
    """
    Main function to parse arguments, build the prompt, and generate content using the language model.
    """
    parser = argparse.ArgumentParser(description='Generate content for a target file based on provided context files.')
    parser.add_argument('--model', type=str, default='gemini-2.0-flash', help='Model name')
    parser.add_argument('--repo', type=str, default='awesome-ai', help='Repository name')
    parser.add_argument('--prompt', type=str, action='append', default=[], help='Prompt for the model')
    parser.add_argument('--log_level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')
    parser.add_argument('files', nargs='+', help='List of files (context files followed by the target file)')
    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(args.log_level.upper())
    logging.info(json.dumps({"cli_args": vars(args)}))


    repo_name = args.repo
    file_names = args.files[:-1]
    target_file_name = args.files[-1]

    prompt = ''

    for p in args.prompt:
        # Check if the prompt is a file name
        if os.path.isfile(p):
            logging.info(json.dumps({"prompt_source": "file", "file_name": p}))
            logging.debug("Using file content as prompt.")
            prompt_content = read_file_content(p)
            if prompt_content:
                prompt += prompt_content
        else:
            logging.info(json.dumps({"prompt_source": "cli", "prompt": p}))
            logging.debug("Using command-line argument as prompt.")
            prompt += p

    logging.debug(f"Prompt:\n{prompt}")
    logging.debug(json.dumps({"final_prompt": prompt}))

    inputs = create_inputs(repo_name, file_names, target_file_name, prompt)
    logging.debug(json.dumps({"inputs_created": True, "num_inputs": len(inputs)}))

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error(json.dumps({"error": "GEMINI_API_KEY not set"}))
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    client = Client(api_key=api_key)
    logging.info(json.dumps({"gemini_client_initialized": True}))

    config = GenerateContentConfig(
        candidate_count=1,
        temperature=0.1,
        max_output_tokens=8192
    )
    logging.debug(json.dumps({"generation_config": config.__dict__}))


    try:
        response = client.models.generate_content_stream(
            model=args.model,  # Using the model name from the command-line arguments
            contents=inputs,
            config=config
        )
        logging.info(json.dumps({"generation_request_sent": True, "model": args.model}))

        for part in response:
            print(part.text, end='', flush=True)

        print('')
        logging.info(json.dumps({"generation_completed": True}))


    except Exception as e:
        logging.exception(json.dumps({"generation_failed": True, "error": str(e)}))
        print(f"An error occurred during content generation: {e}")


if __name__ == "__main__":
    main()
