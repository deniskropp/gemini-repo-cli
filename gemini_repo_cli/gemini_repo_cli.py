#!/usr/bin/env python

import argparse
import os
import logging
import json
from typing import List

from google.genai import Client
from google.genai.types import GenerateContentConfig

# Constants
DEFAULT_MODEL = 'gemini-2.0-flash'
DEFAULT_REPO_NAME = 'awesome-ai'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def read_file_content(file_path: str) -> str | None:
    """Reads the content of a file.

    Args:
        file_path: The path to the file.

    Returns:
        The content of the file as a string, or None if the file is not found.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            log_data = {"file_path": file_path, "status": "success", "file_size_bytes": len(content)}
            logger.debug(json.dumps(log_data))
            return content
    except FileNotFoundError:
        error_message = f"File not found: {file_path}"
        log_data = {"file_path": file_path, "status": "failed", "error": "File not found"}
        logger.error(json.dumps(log_data))
        print(error_message)  # Keep the print for user feedback as well
        return None
    except Exception as e:
        error_message = f"Error reading file {file_path}: {e}"
        log_data = {"file_path": file_path, "status": "failed", "error": str(e)}
        logger.exception(json.dumps(log_data))
        print(error_message)  # Keep the print for user feedback
        return None


def create_prompt_inputs(
    repo_name: str, file_paths: List[str], target_file_name: str, initial_prompt: str
) -> List[List[str]]:
    """Creates input list for the model, structuring the prompt with repo name and file contents.

    Args:
        repo_name: The name of the repository.
        file_paths: A list of file paths to include in the prompt as context.
        target_file_name: The name of the target file to generate.
        initial_prompt: The initial prompt to guide the generation.

    Returns:
        A list of lists, where each inner list represents a part of the prompt.
    """

    inputs = [[initial_prompt, f"⫻const:repo_name\n{repo_name}"]]
    log_data = {"repo_name": repo_name}
    logger.debug(json.dumps(log_data))

    for file_path in file_paths:
        file_content = read_file_content(file_path)
        if file_content:
            inputs.append([f"⫻context/file:{file_path}\n{file_content}"])
            log_data = {"file_path": file_path, "file_size_bytes": len(file_content)}
            logger.debug(json.dumps(log_data))

    inputs.append([f"Generate {target_file_name}\n"])
    log_data = {"target_file_name": target_file_name}
    logger.debug(json.dumps(log_data))
    return inputs


def configure_logging(log_level: str) -> None:
    """Configures the logging level for the application.

    Args:
        log_level: A string representing the desired log level (e.g., "INFO", "DEBUG").
    """
    try:
        numeric_level = getattr(logging, log_level.upper())
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")
        logger.setLevel(numeric_level)
        log_data = {"log_level": log_level}
        logger.info(json.dumps(log_data))
    except AttributeError:
        log_data = {"error": f"Invalid log level: {log_level}", "defaulting_to": "INFO"}
        logger.error(json.dumps(log_data))
        print(f"Invalid log level: {log_level}. Defaulting to INFO.")
        logger.setLevel(logging.INFO)  # Default to INFO
    except ValueError as e:
        log_data = {"error": str(e), "defaulting_to": "INFO"}
        logger.error(json.dumps(log_data))
        print(str(e) + " Defaulting to INFO.")
        logger.setLevel(logging.INFO)


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments.

    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Generate content for a target file based on provided context files.')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help='Model name')
    parser.add_argument('--repo', type=str, default=DEFAULT_REPO_NAME, help='Repository name')
    parser.add_argument('--prompt', type=str, action='append', default=[], help='Prompt for the model')
    parser.add_argument(
        '--log_level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level',
    )
    parser.add_argument('files', nargs='+', help='List of files (context files followed by the target file)')
    return parser.parse_args()


def load_prompt_from_file(file_path: str) -> str | None:
    """Loads the prompt from a file.

    Args:
        file_path: The path to the prompt file.

    Returns:
        The prompt string, or None if the file could not be read.
    """
    log_data = {"prompt_source": "file", "file_path": file_path}
    logger.info(json.dumps(log_data))
    logger.debug("Using file content as prompt.")
    prompt_content = read_file_content(file_path)
    if not prompt_content:
        log_data = {"prompt_file_load_failed": file_path}
        logger.error(json.dumps(log_data))
        print(f"Failed to load prompt from file: {file_path}")
        return None
    return prompt_content


def main() -> None:
    """Main function to parse arguments, build the prompt, and generate content using the language model."""
    args = parse_arguments()
    configure_logging(args.log_level)
    log_data = {"cli_args": vars(args)}
    logger.info(json.dumps(log_data))

    repo_name = args.repo
    context_file_paths = args.files[:-1]
    target_file_name = args.files[-1]

    prompt = ''
    for prompt_source in args.prompt:
        if os.path.isfile(prompt_source):
            loaded_prompt = load_prompt_from_file(prompt_source)
            if loaded_prompt:
                prompt += loaded_prompt
        else:
            log_data = {"prompt_source": "cli", "prompt": prompt_source}
            logger.info(json.dumps(log_data))
            logger.debug("Using command-line argument as prompt.")
            prompt += prompt_source

    logger.debug(f"Prompt:\n{prompt}")
    log_data = {"final_prompt": prompt}
    logger.debug(json.dumps(log_data))

    inputs = create_prompt_inputs(repo_name, context_file_paths, target_file_name, prompt)
    log_data = {"num_inputs": len(inputs)}
    logger.debug(json.dumps(log_data))

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        log_data = {"error": "GEMINI_API_KEY not set"}
        logger.error(json.dumps(log_data))
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    try:
        client = Client(api_key=api_key)
        log_data = {"status": "success"}
        logger.info(json.dumps(log_data))

        config = GenerateContentConfig(candidate_count=1, temperature=0.1, max_output_tokens=8192)
        log_data = {"generation_config": config.__dict__}
        logger.debug(json.dumps(log_data))

        response = client.models.generate_content_stream(
            model=args.model,  # Using the model name from the command-line arguments
            contents=inputs,
            config=config,
        )
        log_data = {"model": args.model}
        logger.info(json.dumps(log_data))

        for part in response:
            print(part.text, end='', flush=True)

        print('')
        log_data = {"status": "success"}
        logger.info(json.dumps(log_data))

    except Exception as e:
        log_data = {"error": str(e)}
        logger.exception(json.dumps(log_data))
        print(f"An error occurred during content generation: {e}")


if __name__ == "__main__":
    main()
