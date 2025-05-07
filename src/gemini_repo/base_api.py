# New file: src/gemini_repo/base_api.py
import logging
from abc import ABC, abstractmethod
from typing import List

# Get logger for this module
logger = logging.getLogger(__name__)

class BaseRepoAPI(ABC):
    """
    Abstract base class for repository-aware content generation APIs.
    Defines the common interface for interacting with different LLM providers.
    """

    def __init__(self, model_name: str):
        """
        Initializes the base API class.

        Args:
            model_name: The name of the specific model to use within the provider.
        """
        self.model_name = model_name
        logger.info({"event": "base_api_init", "provider": self.__class__.__name__, "model_name": self.model_name})

    @abstractmethod
    def generate_content(self, repo_name: str, file_paths: List[str], target_file_name: str, prompt: str) -> str:
        """
        Generates content based on repository context and a prompt.

        Args:
            repo_name: The name of the repository.
            file_paths: List of paths to context files.
            target_file_name: The name/path of the file the generated content is for.
            prompt: The user's core instruction.

        Returns:
            The generated content as a string.

        Raises:
            FileNotFoundError: If a context file cannot be read.
            Exception: If an API error or other generation error occurs.
        """
        pass

    def _read_file_content(self, file_path: str) -> str:
        """
        Reads the content of a single file. (Shared implementation)

        Args:
            file_path: The path to the file.

        Returns:
            The content of the file as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If any other error occurs during file reading.
        """
        log_data = {"event": "read_file_attempt", "file_path": file_path, "provider": self.__class__.__name__}
        logger.debug(log_data)
        try:
            # Use 'rb' and decode explicitly to handle potential encoding errors more gracefully
            with open(file_path, 'rb') as file:
                raw_content = file.read()
            try:
                # Try UTF-8 first
                content = raw_content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1 or another common encoding if UTF-8 fails
                logger.warning({"event": "read_file_decode_fallback", "file_path": file_path, "encoding": "latin-1"})
                content = raw_content.decode('latin-1', errors='replace') # Replace errors to avoid crashing

            log_data.update({"status": "success", "file_size_bytes": len(raw_content)})
            logger.debug(log_data)
            return content
        except FileNotFoundError:
            log_data.update({"status": "failed", "error": "File not found"})
            logger.error(log_data)
            raise FileNotFoundError(f"Context file not found: {file_path}")
        except Exception as e:
            log_data.update({"status": "failed", "error": str(e)})
            logger.exception(log_data)
            raise IOError(f"Error reading file {file_path}: {e}")

    def _create_prompt_inputs(
        self, repo_name: str, file_paths: List[str], target_file_name: str, initial_prompt: str
    ) -> str:
        """
        Constructs a single string prompt suitable for most LLMs.
        Specific providers might override this if they need a different format.

        Args:
            repo_name: The repository name.
            file_paths: List of context file paths.
            target_file_name: The target file name for generation.
            initial_prompt: The user's core prompt/instruction.

        Returns:
            A single string containing the structured prompt.

        Raises:
            FileNotFoundError: If `_read_file_content` fails.
            IOError: If `_read_file_content` fails.
        """
        prompt_parts = []
        log_data = {"event": "prompt_build_start", "repo_name": repo_name, "provider": self.__class__.__name__}
        logger.debug(log_data)

        # 1. Initial User Prompt
        prompt_parts.append(f"--- User Task ---\n{initial_prompt}\n")

        # 2. Repository Context
        prompt_parts.append(f"--- Repository Context ---\nRepository Name: {repo_name}\n")

        # 3. File Context
        if file_paths:
            prompt_parts.append("--- File Context ---")
            for file_path in file_paths:
                try:
                    file_content = self._read_file_content(file_path) # Can raise FileNotFoundError/IOError
                    prompt_parts.append(f"\n### File: {file_path}\n```\n{file_content}\n```")
                    log_data = {"event": "prompt_add_context", "file_path": file_path}
                    logger.debug(log_data)
                except (FileNotFoundError, IOError) as e:
                     raise e # Re-raise to be caught by the caller
            prompt_parts.append("\n--- End File Context ---\n") # Mark end of file context
        else:
            prompt_parts.append("--- No File Context Provided ---\n")


        # 4. Final Instruction
        prompt_parts.append(f"--- Generation Target ---\nGenerate the complete content for the file: {target_file_name}\n")
        prompt_parts.append("--- Output ---") # Signal where the model's output should begin

        full_prompt = "\n".join(prompt_parts)

        # Save prompt for debugging if needed (consider making this optional)
        # try:
        #     with open('prompt_debug.txt', mode='w', encoding='utf-8') as f:
        #          f.write(full_prompt)
        #     logger.debug({"event": "prompt_saved_to_file", "file": "prompt_debug.txt"})
        # except Exception as e:
        #     logger.warning({"event": "prompt_save_failed", "error": str(e)})


        log_data = {"event": "prompt_build_complete", "target_file_name": target_file_name, "prompt_length": len(full_prompt)}
        logger.debug(log_data)

        return full_prompt
