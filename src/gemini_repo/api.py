import os
import logging
import json
from typing import List, Optional

# Note: google-genai library needs to be installed
# pip install google-genai
try:
    from google.genai import Client
    from google.genai.types import GenerateContentConfig
except ImportError:
    print("ERROR: google-genai library not found. Please install it: pip install google-genai")
    exit(1)


# Constants
DEFAULT_MODEL = 'gemini-2.0-flash' # Updated default model

# Get logger for this module. Configuration is handled by the application using this library.
logger = logging.getLogger(__name__)


class GeminiRepoAPI:
    """
    Interacts with the Google Gemini API to generate content based on repository context.

    This class encapsulates the logic for authenticating with the Gemini API,
    constructing prompts with file context, sending requests, and processing responses.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_MODEL):
        """
        Initializes the GeminiRepoAPI client.

        Args:
            api_key: The Google Gemini API key. If None, attempts to read from
                     the GEMINI_API_KEY environment variable.
            model_name: The name of the Gemini model to use (e.g., 'gemini-2.5-pro-exp-03-25').

        Raises:
            ValueError: If the API key is not provided and not found in the environment.
            Exception: If the Google Gemini client fails to initialize.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            log_data = {"event": "init_failed", "reason": "API key missing"}
            logger.error(log_data)
            raise ValueError("GEMINI_API_KEY not provided or set in environment variables.")

        self.model_name = model_name
        try:
            # Initialize the Google Gemini client
            self.client = Client(api_key=self.api_key)
            log_data = {"event": "client_init", "status": "success", "model_name": self.model_name}
            logger.info(log_data)
        except Exception as e:
            log_data = {"event": "client_init", "status": "failed", "error": str(e)}
            logger.exception(log_data) # Use exception to include traceback
            raise Exception(f"Failed to initialize Google Gemini client: {e}")

        # Configure generation parameters
        # candidate_count: Number of responses to generate.
        # temperature: Controls randomness (lower means more deterministic).
        # max_output_tokens: Limits the length of the generated response.
        self.generation_config = GenerateContentConfig(
            candidate_count=1,
            temperature=0.2, # Slightly increased for potentially more creative code gen
            max_output_tokens=8192 # Increased token limit for larger files
        )
        log_data = {
            "event": "config_set",
            "generation_config": {
                "candidate_count": self.generation_config.candidate_count,
                "temperature": self.generation_config.temperature,
                "max_output_tokens": self.generation_config.max_output_tokens
            }
        }
        logger.debug(log_data)

    def generate_content(self, repo_name: str, file_paths: List[str], target_file_name: str, prompt: str) -> str:
        """
        Generates content for a target file using context from other files.

        Constructs a structured prompt including the repository name, contents of
        specified files, and the user's request, then sends it to the Gemini API.

        Args:
            repo_name: The name of the repository (used for context).
            file_paths: A list of paths to files whose content should be included
                        in the prompt context.
            target_file_name: The name/path of the file the generated content is intended for.
            prompt: The user's core instruction or question for the generation.

        Returns:
            The generated content as a single string.

        Raises:
            FileNotFoundError: If any file in `file_paths` cannot be read.
            Exception: If an error occurs during API communication or content generation.
        """
        try:
            model_inputs = self._create_prompt_inputs(repo_name, file_paths, target_file_name, prompt)
            log_data = {"event": "prompt_created", "num_input_parts": len(model_inputs)}
            logger.debug(log_data)

            # Select the specific model instance
            model_instance = self.client.get_generative_model(self.model_name)

            # Generate content using the streaming API for potentially long responses
            response_stream = model_instance.generate_content(
                contents=model_inputs,
                generation_config=self.generation_config,
                stream=True
            )
            log_data = {"event": "generation_request_sent", "model": self.model_name}
            logger.info(log_data)

            generated_content_parts = []
            for chunk in response_stream:
                # Handle potential empty chunks or chunks without text
                if chunk.parts:
                    generated_content_parts.append(chunk.text)


            generated_content = "".join(generated_content_parts)

            log_data = {"event": "generation_complete", "status": "success", "output_length": len(generated_content)}
            logger.info(log_data)

            return generated_content

        except FileNotFoundError as e:
             # Log specific file not found errors from _read_file_content via _create_prompt_inputs
            log_data = {"event": "generation_failed", "reason": "context_file_not_found", "error": str(e)}
            logger.error(log_data)
            raise  # Re-raise the specific error
        except Exception as e:
            log_data = {"event": "generation_failed", "reason": "api_error", "error": str(e)}
            logger.exception(log_data) # Use exception for traceback
            raise Exception(f"An error occurred during content generation: {e}")

    def _read_file_content(self, file_path: str) -> str:
        """
        Reads the content of a single file.

        Args:
            file_path: The path to the file.

        Returns:
            The content of the file as a string.

        Raises:
            FileNotFoundError: If the file does not exist at the specified path.
            IOError: If any other error occurs during file reading.
        """
        log_data = {"event": "read_file_attempt", "file_path": file_path}
        logger.debug(log_data)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                log_data.update({"status": "success", "file_size_bytes": len(content.encode('utf-8'))})
                logger.debug(log_data)
                return content
        except FileNotFoundError:
            log_data.update({"status": "failed", "error": "File not found"})
            logger.error(log_data)
            # Raise specific error to be caught by the caller
            raise FileNotFoundError(f"Context file not found: {file_path}")
        except Exception as e:
            log_data.update({"status": "failed", "error": str(e)})
            logger.exception(log_data)
             # Raise a more general error for other issues
            raise IOError(f"Error reading file {file_path}: {e}")

    def _create_prompt_inputs(
        self, repo_name: str, file_paths: List[str], target_file_name: str, initial_prompt: str
    ) -> List:
        """
        Constructs the structured input list for the Gemini API.

        The prompt is assembled using KickLang-like tags for context clarity:
        - `⫻const:repo_name`: Identifies the repository.
        - `⫻context/file:{file_path}`: Provides content from context files.
        - The final part specifies the target file and the core generation task.

        Args:
            repo_name: The repository name.
            file_paths: List of context file paths.
            target_file_name: The target file name for generation.
            initial_prompt: The user's core prompt/instruction.

        Returns:
            A list suitable for the `contents` parameter of the Gemini API's
            `generate_content` method.

        Raises:
            FileNotFoundError: If `_read_file_content` fails for any file.
            IOError: If `_read_file_content` fails for any file.
        """
        # Start with the main user prompt and repository context
        # Using a list of strings/parts per turn, as recommended for multimodal input later
        # For text-only now, simple strings work, but this structure is flexible.
        model_inputs = [initial_prompt, f"⫻const:repo_name\n{repo_name}"]
        log_data = {"event": "prompt_build_start", "repo_name": repo_name}
        logger.debug(log_data)

        # Add context from each specified file
        for file_path in file_paths:
            try:
                file_content = self._read_file_content(file_path) # Can raise FileNotFoundError/IOError
                # Append file context using a specific tag
                model_inputs.append(f"⫻context/file:{file_path}\n{file_content}")
                log_data = {"event": "prompt_add_context", "file_path": file_path, "file_size_bytes": len(file_content.encode('utf-8'))}
                logger.debug(log_data)
            except (FileNotFoundError, IOError) as e:
                 # Log is handled in _read_file_content, just re-raise
                 raise e

        # Add the final instruction specifying the target file
        model_inputs.append(f"Generate content for the file: {target_file_name}\n")
        log_data = {"event": "prompt_build_complete", "target_file_name": target_file_name}
        logger.debug(log_data)

        # The API expects a list where each item represents a turn or a cohesive block.
        # For simple text prompts, often a single list containing all parts works.
        # Let's structure it as a single list of strings for now.
        return model_inputs
