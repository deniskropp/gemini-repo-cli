import os
import logging
import json
from typing import List

from google.genai import Client
from google.genai.types import GenerateContentConfig

# Constants
DEFAULT_MODEL = 'gemini-2.0-flash'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiRepoAPI:
    """
    A class to interact with the Google Gemini API for generating content based on a repository context.
    """

    def __init__(self, api_key: str = None, model_name: str = DEFAULT_MODEL):
        """
        Initializes the GeminiRepoAPI with an API key and model name.

        Args:
            api_key: The Google Gemini API key. If not provided, it will be read from the GEMINI_API_KEY environment variable.
            model_name: The name of the Gemini model to use. Defaults to 'gemini-2.0-flash'.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            log_data = {"error": "GEMINI_API_KEY not set"}
            logger.error(json.dumps(log_data))
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        self.model_name = model_name
        try:
            self.client = Client(api_key=self.api_key)
            log_data = {"status": "success"}
            logger.info(json.dumps(log_data))
        except Exception as e:
            log_data = {"error": str(e)}
            logger.exception(json.dumps(log_data))
            raise Exception(f"Failed to initialize Gemini client: {e}")

        self.generation_config = GenerateContentConfig(candidate_count=1, temperature=0.1, max_output_tokens=8192)
        log_data = {"generation_config": self.generation_config.__dict__}
        logger.debug(json.dumps(log_data))

    def generate_content(self, repo_name: str, file_paths: List[str], target_file_name: str, prompt: str) -> str:
        """
        Generates content for a target file based on the provided context files and prompt.

        Args:
            repo_name: The name of the repository.
            file_paths: A list of file paths to include in the prompt as context.
            target_file_name: The name of the target file to generate.
            prompt: The prompt to guide the generation.

        Returns:
            The generated content as a string.

        Raises:
            Exception: If an error occurs during content generation.
        """
        inputs = self._create_prompt_inputs(repo_name, file_paths, target_file_name, prompt)
        log_data = {"num_inputs": len(inputs)}
        logger.debug(json.dumps(log_data))

        try:
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=inputs,
                config=self.generation_config,
            )
            log_data = {"model": self.model_name}
            logger.info(json.dumps(log_data))

            generated_content = ""
            for part in response:
                generated_content += part.text

            log_data = {"status": "success"}
            logger.info(json.dumps(log_data))

            return generated_content

        except Exception as e:
            log_data = {"error": str(e)}
            logger.exception(json.dumps(log_data))
            raise Exception(f"An error occurred during content generation: {e}")

    def _read_file_content(self, file_path: str) -> str | None:
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

    def _create_prompt_inputs(
        self, repo_name: str, file_paths: List[str], target_file_name: str, initial_prompt: str
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
            file_content = self._read_file_content(file_path)
            if file_content:
                inputs.append([f"⫻context/file:{file_path}\n{file_content}"])
                log_data = {"file_path": file_path, "file_size_bytes": len(file_content)}
                logger.debug(json.dumps(log_data))

        inputs.append([f"Generate {target_file_name}\n"])
        log_data = {"target_file_name": target_file_name}
        logger.debug(json.dumps(log_data))
        return inputs
