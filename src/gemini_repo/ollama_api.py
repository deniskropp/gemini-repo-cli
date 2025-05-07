# New file: src/gemini_repo/ollama_api.py
import logging
from typing import List, Optional
import os

# Note: ollama library needs to be installed
# pip install ollama
try:
    import ollama
except ImportError:
    print("ERROR: ollama library not found. Please install it: pip install ollama")
    # Consider logging this error instead of printing if library is optional
    # logger.error({"event": "dependency_missing", "library": "ollama"})
    exit(1) # Or handle more gracefully

from .base_api import BaseRepoAPI

# Constants
DEFAULT_OLLAMA_MODEL = 'qwen2.5-coder:1.5b' # Example default Ollama model
DEFAULT_OLLAMA_HOST = 'http://localhost:11434' # Let the library use its default (usually http://localhost:11434)

# Get logger
logger = logging.getLogger(__name__)

class OllamaRepoAPI(BaseRepoAPI):
    """
    Interacts with a local Ollama instance using repository context.
    """

    def __init__(self, model_name: str = DEFAULT_OLLAMA_MODEL, host: Optional[str] = DEFAULT_OLLAMA_HOST):
        """
        Initializes the OllamaRepoAPI client.

        Args:
            model_name: The name of the Ollama model to use (must be pulled locally).
            host: The URL of the Ollama server (e.g., 'http://localhost:11434').
                  If None, uses the default from the `ollama` library or OLLAMA_HOST env var.
        """
        super().__init__(model_name) # Initialize base class

        self.host = host
        try:
            # Initialize the Ollama client
            # The library handles the OLLAMA_HOST env var automatically if host is None
            self.client = ollama.Client(host=self.host)

            # Optional: Check if the model exists locally (can be slow)
            # try:
            #     self.client.show(self.model_name)
            #     logger.info({"event": "ollama_model_check", "status": "found", "model": self.model_name})
            # except ollama.ResponseError as e:
            #     if e.status_code == 404:
            #         logger.error({"event": "ollama_init_failed", "reason": "model_not_found", "model": self.model_name, "host": self.client.host})
            #         raise ValueError(f"Ollama model '{self.model_name}' not found locally on {self.client.host}. Pull it first (e.g., `ollama pull {self.model_name}`)")
            #     else:
            #         raise # Re-raise other ResponseErrors

            log_data = {"event": "ollama_client_init", "status": "success", "model_name": self.model_name, "host": self.host}
            logger.info(log_data)
        except Exception as e:
            log_data = {"event": "ollama_client_init", "status": "failed", "error": str(e), "host": self.host}
            logger.exception(log_data)
            raise Exception(f"Failed to initialize Ollama client for host '{self.host}': {e}")

        # Set common Ollama options (can be overridden in generate call)
        self.options = {
            'temperature': 0.3,
            'num_ctx': 4096, # Example context window size, adjust based on model
             # Add other options like top_p, top_k, seed etc. if needed
             # 'seed': 42,
             # 'top_p': 0.9,
        }
        log_data = {"event": "ollama_config_set", "options": self.options}
        logger.debug(log_data)


    def generate_content(self, repo_name: str, file_paths: List[str], target_file_name: str, prompt: str) -> str:
        """
        Generates content using the Ollama API.

        Overrides the base class method.

        Args: See BaseRepoAPI.generate_content.
        Returns: See BaseRepoAPI.generate_content.
        Raises: See BaseRepoAPI.generate_content.
        """
        try:
            # Use the base class method to create the prompt string
            full_prompt = self._create_prompt_inputs(repo_name, file_paths, target_file_name, prompt)
            log_data = {"event": "ollama_prompt_created", "prompt_length": len(full_prompt)}
            logger.debug(log_data)

            # Save prompt for debugging if needed
            # with open('prompt_ollama.txt', mode='w', encoding='utf-8') as f:
            #     f.write(full_prompt)

            # Ollama API expects the prompt in the 'prompt' field
            # System prompt could be added here if desired: system="..."
            response = self.client.generate(
                model=self.model_name,
                prompt=full_prompt,
                stream=False, # Keep it simple for now, no streaming
                options=self.options # Pass configured options
            )
            log_data = {"event": "ollama_generation_request_sent", "model": self.model_name}
            logger.info(log_data)

            # Extract the response text
            generated_content = response.get('response', '').strip() # Get 'response' field, default to empty string

            # Log details from the response if needed
            response_details = {}#{k: v for k, v in response.items() if k != 'response'} # Log metadata without the full text
            log_data = {
                "event": "ollama_generation_complete",
                "status": "success",
                "output_length": len(generated_content),
                "response_details": response_details
                }
            logger.info(log_data)

            return generated_content

        except FileNotFoundError as e:
            # Logged in _read_file_content, re-raise for CLI handling
            log_data = {"event": "ollama_generation_failed", "reason": "context_file_not_found", "error": str(e)}
            logger.error(log_data)
            raise
        except ollama.ResponseError as e:
             # Handle specific Ollama API errors (e.g., model not found, connection error)
             log_data = {
                 "event": "ollama_generation_failed",
                 "reason": "api_response_error",
                 "status_code": e.status_code,
                 "error": str(e)}
             logger.error(log_data)
             raise Exception(f"Ollama API error (status {e.status_code}): {e}") from e
        except Exception as e:
            # Catch other potential errors (network, config, etc.)
            log_data = {"event": "ollama_generation_failed", "reason": "api_error", "error": str(e)}
            logger.exception(log_data) # Use exception for traceback
            raise Exception(f"An error occurred during Ollama content generation: {e}") from e
