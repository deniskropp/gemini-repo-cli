# Renamed from api.py
import os
import logging
from typing import List, Optional

# Note: google-genai library needs to be installed
# pip install google-genai
try:
    from google.genai import Client
    from google.genai.types import GenerateContentConfig
except ImportError:
    print("ERROR: google-genai library not found. Please install it: pip install google-genai")
    exit(1)

from .base_api import BaseRepoAPI # Import the base class

# Constants
DEFAULT_GEMINI_MODEL = 'gemini-2.0-flash' # Updated default model

# Get logger for this module. Configuration is handled by the application using this library.
logger = logging.getLogger(__name__)


class GeminiRepoAPI(BaseRepoAPI): # Inherit from BaseRepoAPI
    """
    Interacts with the Google Gemini API using repository context.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_GEMINI_MODEL):
        """
        Initializes the GeminiRepoAPI client.

        Args:
            api_key: The Google Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model_name: The name of the Gemini model to use.

        Raises:
            ValueError: If API key is missing.
            Exception: If the Google Gemini client fails to initialize.
        """
        super().__init__(model_name) # Initialize base class

        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            log_data = {"event": "gemini_init_failed", "reason": "API key missing"}
            logger.error(log_data)
            raise ValueError("GEMINI_API_KEY not provided or set in environment variables.")

        try:
            # Initialize the Google Gemini client
            self.client = Client(api_key=self.api_key)
            # Or directly use the generic client if preferred for simple cases:
            # self.client = Client() # Keeps the client instance if needed elsewhere

            log_data = {"event": "gemini_client_init", "status": "success", "model_name": self.model_name}
            logger.info(log_data)
        except Exception as e:
            log_data = {"event": "gemini_client_init", "status": "failed", "error": str(e)}
            logger.exception(log_data)
            raise Exception(f"Failed to initialize Google Gemini client: {e}")

        # Configure generation parameters
        self.generation_config = GenerateContentConfig(
            candidate_count=1,
            temperature=0.3, # Adjusted slightly
            max_output_tokens=8192
        )
        log_data = {
            "event": "gemini_config_set",
            "generation_config": {
                "candidate_count": self.generation_config.candidate_count,
                "temperature": self.generation_config.temperature,
                "max_output_tokens": self.generation_config.max_output_tokens
            }
        }
        logger.debug(log_data)

    def generate_content(self, repo_name: str, file_paths: List[str], target_file_name: str, prompt: str) -> str:
        """
        Generates content using the Gemini API.

        Overrides the base class method.

        Args: See BaseRepoAPI.generate_content.
        Returns: See BaseRepoAPI.generate_content.
        Raises: See BaseRepoAPI.generate_content.
        """
        try:
            # Use the base class method to create the prompt string
            full_prompt = self._create_prompt_inputs(repo_name, file_paths, target_file_name, prompt)
            log_data = {"event": "gemini_prompt_created", "prompt_length": len(full_prompt)}
            logger.debug(log_data)

            # Save prompt for debugging if needed
            with open('prompt_gemini.txt', mode='w', encoding='utf-8') as f:
                f.write(full_prompt)

            # Gemini API expects a list of strings/parts.
            model_inputs = [full_prompt] # Pass the full prompt as a single item in the list

            # Generate content using the specific model instance
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=model_inputs,
                config=self.generation_config
                # stream=False # Set stream=True if needed, handle response differently
            )
            log_data = {"event": "gemini_generation_request_sent", "model": self.model_name}
            logger.info(log_data)

            # --- Response Handling ---
            try:
                # Access the text content safely
                generated_content = response.text
                log_data = {"event": "gemini_generation_complete", "status": "success", "output_length": len(generated_content)}
                logger.info(log_data)
                return generated_content
            except ValueError as e:
                 # Handle cases where response.text might raise an error (e.g., blocked content)
                finish_reason = "Unknown"
                block_reason = "Unknown"
                safety_ratings = [] # Initialize safety_ratings as an empty list
                try:
                    # Attempt to get more detailed feedback if available
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                         # Use getattr for safer access to block_reason
                         block_reason = getattr(response.prompt_feedback, 'block_reason', 'Unknown')
                         if hasattr(response.prompt_feedback, 'safety_ratings'):
                              safety_ratings = [str(rating) for rating in response.prompt_feedback.safety_ratings] # Convert enum/objects to string
                except Exception:
                    logger.warning({"event": "gemini_feedback_parsing_error"}) # Log if feedback access fails

                try:
                     # Check candidates finish reason if feedback isn't definitive
                     # Ensure candidates exist and the first candidate has finish_reason
                     if hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0, 'finish_reason']):
                          # Convert finish_reason enum to string/int if needed
                          finish_reason = str(response.candidates[0].finish_reason)
                except Exception:
                    logger.warning({"event": "gemini_finish_reason_parsing_error"})

                error_message = f"Gemini API response error: {e}. Finish Reason: {finish_reason}, Block Reason: {block_reason}"
                log_data = {
                    "event": "gemini_generation_failed",
                    "reason": "api_response_error",
                    "error": str(e),
                    "finish_reason": finish_reason,
                    "block_reason": block_reason,
                    "safety_ratings": safety_ratings # Log extracted ratings
                }
                logger.error(log_data)
                raise Exception(error_message) from e # Raise a new exception chaining the original
            # --- End Response Handling ---

        except FileNotFoundError as e:
            # Logged in _read_file_content, re-raise for CLI handling
            log_data = {"event": "gemini_generation_failed", "reason": "context_file_not_found", "error": str(e)}
            logger.error(log_data)
            raise
        except Exception as e:
            # Catch other potential API errors (network, config, etc.)
            log_data = {"event": "gemini_generation_failed", "reason": "api_error", "error": str(e)}
            logger.exception(log_data) # Use exception for traceback
            # Avoid raising the raw google.api_core.exceptions error directly if possible
            raise Exception(f"An error occurred during Gemini content generation: {e}") from e
