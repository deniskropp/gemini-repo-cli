import argparse
import os
import sys
import logging
import json
import time
from logging import StreamHandler, Formatter

# Import necessary classes and constants from the updated __init__
from gemini_repo import (
    GeminiRepoAPI,
    OllamaRepoAPI,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_OLLAMA_MODEL,
)


# --- JSON Logging Setup ---
# ... (JsonFormatter and setup_logging function remain the same) ...
class JsonFormatter(Formatter):
    """
    Formats log records as JSON strings (JSONL format - one JSON object per line).
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            #"pathname": record.pathname, # Optional: file path
            #"lineno": record.lineno,     # Optional: line number
        }
        # If the log message is a dictionary, merge it
        if isinstance(record.msg, dict):
            log_record.update(record.msg)
        else:
            log_record["message"] = record.getMessage()

        # Add exception info if present
        if record.exc_info:
            # formatException typically returns a multi-line string; replace newlines
            log_record['exception'] = self.formatException(record.exc_info).replace('\n', '\\n')
        if record.stack_info:
             log_record['stack_info'] = self.formatStack(record.stack_info).replace('\n', '\\n')

        return json.dumps(log_record)

def setup_logging(debug=False):
    """Configures logging to output JSONL to stderr."""
    log_level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger() # Get root logger
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates if run multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handler and formatter
    handler = StreamHandler(sys.stderr) # Log to stderr
    formatter = JsonFormatter(datefmt='%Y-%m-%dT%H:%M:%S%z') # ISO 8601 format

    # Set formatter and add handler
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set level for the specific logger of this module
    logging.getLogger(__name__).setLevel(log_level)
    logging.getLogger("gemini_repo").setLevel(log_level) # Set level for the whole package logger
    # Optionally set levels for other libraries if needed
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING) # Common dependency for network requests
    logging.getLogger('ollama').setLevel(logging.INFO if debug else logging.WARNING) # Ollama lib logging


# --- Main CLI Logic ---

def main():
    """
    Command-Line Interface for generating file content using different LLM providers.
    """
    parser = argparse.ArgumentParser(
        description="Generate file content using Gemini or Ollama API and repository context.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # --- Provider Selection ---
    parser.add_argument(
        "--provider", "-p",
        choices=["gemini", "ollama"],
        default="gemini", # Default to Gemini
        help="The LLM provider to use."
    )

    # --- Common Arguments ---
    parser.add_argument(
        "repo_name",
        help="The logical name of the repository (used for context)."
    )
    parser.add_argument(
        "target_file",
        help="The name/path of the target file to generate content for."
    )
    parser.add_argument(
        "prompt",
        help="The core prompt/instruction to guide content generation."
    )
    parser.add_argument(
        "--files", "-f",
        nargs="+",
        default=[],
        metavar="FILE_PATH",
        help="Space-separated list of file paths to include as context.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="OUTPUT_FILE",
        help="Path to the file where generated content will be written. If omitted, output to stdout."
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable DEBUG level logging."
    )

    # --- Provider-Specific Arguments ---
    # Gemini
    gemini_group = parser.add_argument_group('Gemini Options (used if --provider=gemini)')
    gemini_group.add_argument(
        "--gemini-api-key",
        dest="gemini_api_key",
        default=None, # API class checks env var GEMINI_API_KEY
        help="Google Gemini API key. Overrides GEMINI_API_KEY environment variable."
    )
    gemini_group.add_argument(
        "--gemini-model",
        dest="gemini_model",
        default=DEFAULT_GEMINI_MODEL,
        help="Name of the Gemini model to use."
    )

    # Ollama
    ollama_group = parser.add_argument_group('Ollama Options (used if --provider=ollama)')
    ollama_group.add_argument(
        "--ollama-model",
        dest="ollama_model",
        default=DEFAULT_OLLAMA_MODEL,
        help="Name of the Ollama model to use."
    )
    ollama_group.add_argument(
        "--ollama-host",
        dest="ollama_host",
        default=None, # API class checks env var OLLAMA_HOST
        help="Ollama host URL (e.g., http://localhost:11434). Overrides OLLAMA_HOST environment variable."
    )

    args = parser.parse_args()

    # --- Setup Logging ---
    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__)
    start_time = time.time()
    # Log selected args, masking sensitive ones if necessary in a real app
    log_args = vars(args).copy()
    if 'gemini_api_key' in log_args and log_args['gemini_api_key']:
        log_args['gemini_api_key'] = '***REDACTED***'
    logger.info({"event": "cli_start", "args": log_args})

    # --- Initialize API based on provider ---
    api_instance = None
    try:
        if args.provider == "gemini":
            logger.info({"event": "api_init_start", "provider": "gemini"})
            api_instance = GeminiRepoAPI(
                api_key=args.gemini_api_key,
                model_name=args.gemini_model
            )
        elif args.provider == "ollama":
            logger.info({"event": "api_init_start", "provider": "ollama"})
            api_instance = OllamaRepoAPI(
                model_name=args.ollama_model,
                host=args.ollama_host
            )
        else:
            # This case should not be reachable due to argparse choices
            raise ValueError(f"Unsupported provider: {args.provider}")
        logger.info({"event": "api_init", "status": "success", "provider": args.provider})

    except ValueError as e: # Catches initialization errors like missing API keys/hosts
        logger.error({"event": "api_init", "status": "failed", "provider": args.provider, "error": str(e)})
        print(f"ERROR: Initialization failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # Catch unexpected errors during init
        logger.exception({"event": "api_init", "status": "failed", "provider": args.provider, "error": str(e)})
        print(f"ERROR: Unexpected error during initialization: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Generate Content ---
    generated_content = None
    try:
        logger.info({
            "event": "generation_start",
            "provider": args.provider,
            "model": api_instance.model_name, # Log the actual model used
            "target_file": args.target_file,
            "context_files": args.files
        })
        generation_start_time = time.time()

        # Call the common generate_content method
        generated_content = api_instance.generate_content(
            repo_name=args.repo_name,
            file_paths=args.files,
            target_file_name=args.target_file,
            prompt=args.prompt,
        )
        generation_duration = time.time() - generation_start_time
        logger.info({
            "event": "generation_end",
            "status": "success",
            "provider": args.provider,
            "duration_seconds": round(generation_duration, 3),
            "output_length": len(generated_content)
        })

    except FileNotFoundError as e:
        logger.error({"event": "generation_end", "status": "failed", "reason": "context_file_not_found", "provider": args.provider, "error": str(e)})
        print(f"ERROR: Could not read context file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # Catch API errors or other issues during generation
        logger.exception({"event": "generation_end", "status": "failed", "reason": "api_error", "provider": args.provider, "error": str(e)})
        print(f"ERROR: Failed to generate content: {e}", file=sys.stderr)
        # Consider more specific error handling for different API exceptions if needed
        sys.exit(1)

    # --- Output Content ---
    output_destination = args.output if args.output else "stdout"
    try:
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir:
                 os.makedirs(output_dir, exist_ok=True)

            with open(args.output, "w", encoding='utf-8') as f:
                f.write(generated_content)
            logger.info({"event": "output_write", "status": "success", "destination": args.output})
            print(f"Content successfully written to {args.output}", file=sys.stderr)
        else:
            print(generated_content)
            logger.info({"event": "output_write", "status": "success", "destination": "stdout"})

    except Exception as e:
        logger.exception({"event": "output_write", "status": "failed", "destination": output_destination, "error": str(e)})
        print(f"ERROR: Failed to write output to {output_destination}: {e}", file=sys.stderr)
        sys.exit(1)

    total_duration = time.time() - start_time
    logger.info({"event": "cli_end", "status": "success", "total_duration_seconds": round(total_duration, 3)})


if __name__ == "__main__":
    main()
