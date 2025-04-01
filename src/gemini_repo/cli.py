import argparse
import os
import sys
import logging
import json
import time
from logging import StreamHandler, Formatter
from gemini_repo import GeminiRepoAPI


# --- Constants ---

# Use default from API class
from gemini_repo.api import DEFAULT_MODEL


# --- JSON Logging Setup ---

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
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create handler and formatter
    handler = StreamHandler(sys.stderr) # Log to stderr
    formatter = JsonFormatter(datefmt='%Y-%m-%dT%H:%M:%S%z') # ISO 8601 format

    # Set formatter and add handler
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set level for the specific logger of this module
    logging.getLogger(__name__).setLevel(log_level)
    # Optionally set levels for other libraries if needed (e.g., reduce verbosity)
    # logging.getLogger('google').setLevel(logging.WARNING)


# --- Main CLI Logic ---

def main():
    """
    Command-Line Interface for generating file content using GeminiRepoAPI.

    Parses arguments, sets up logging, initializes the API, calls the
    content generation method, and handles output to stdout or a file.
    """
    parser = argparse.ArgumentParser(
        description="Generate content for a target file using Google Gemini API and repository context.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Show default values in help
    )
    parser.add_argument(
        "repo_name",
        help="The logical name of the repository (used for context in the prompt)."
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
        "--api-key", "-k", # Changed short flag to avoid conflict if adding key file option later
        dest="api_key", # Explicit destination name
        default=None, # Default to None, API class will check env var
        help="Google Gemini API key. Overrides GEMINI_API_KEY environment variable if provided."
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help="Name of the Gemini model to use."
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

    args = parser.parse_args()

    # --- Setup Logging ---
    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__) # Get logger for this module
    start_time = time.time()
    logger.info({"event": "cli_start", "args": vars(args)}) # Log arguments securely if needed

    # --- Initialize API ---
    api_instance = None # Initialize to None
    try:
        api_instance = GeminiRepoAPI(api_key=args.api_key, model_name=args.model)
        logger.info({"event": "api_init", "status": "success"})
    except ValueError as e:
        logger.error({"event": "api_init", "status": "failed", "error": str(e)})
        print(f"ERROR: Initialization failed: {e}", file=sys.stderr)
        sys.exit(1) # Exit with error code
    except Exception as e:
        logger.exception({"event": "api_init", "status": "failed", "error": str(e)})
        print(f"ERROR: Unexpected error during initialization: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Generate Content ---
    generated_content = None
    try:
        logger.info({"event": "generation_start", "target_file": args.target_file, "context_files": args.files})
        generation_start_time = time.time()

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
            "duration_seconds": round(generation_duration, 3),
            "output_length": len(generated_content)
        })

    except FileNotFoundError as e:
         # Specific handling for file not found during generation (logged in API, but good to note here too)
        logger.error({"event": "generation_end", "status": "failed", "reason": "context_file_not_found", "error": str(e)})
        print(f"ERROR: Could not read context file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception({"event": "generation_end", "status": "failed", "reason": "api_error", "error": str(e)})
        print(f"ERROR: Failed to generate content: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Output Content ---
    output_destination = args.output if args.output else "stdout"
    try:
        if args.output:
            # Create directories if they don't exist
            output_dir = os.path.dirname(args.output)
            if output_dir: # Ensure it's not an empty string (e.g., file in current dir)
                 os.makedirs(output_dir, exist_ok=True)

            with open(args.output, "w", encoding='utf-8') as f:
                f.write(generated_content)
            logger.info({"event": "output_write", "status": "success", "destination": args.output})
            print(f"Content successfully written to {args.output}", file=sys.stderr) # User feedback to stderr
        else:
            # Print generated content directly to standard output
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
