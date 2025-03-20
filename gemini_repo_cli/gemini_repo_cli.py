import argparse
import os
import logging
import json

from gemini_repo import GeminiRepoAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Main function to parse command-line arguments and generate content using the GeminiRepoAPI.
    """
    # Extract the last two directories from the current working directory
    current_dir = os.path.normpath(os.getcwd())
    repo_name = "/".join(current_dir.split(os.sep)[-2:])

    parser = argparse.ArgumentParser(description="Generate content for a target file using Google Gemini API.")
    parser.add_argument("repo_name", help="The name of the repository.", default=repo_name)
    parser.add_argument("target_file_name", help="The name of the target file to generate.", default='solution.md')
    parser.add_argument("prompt", help="The prompt to guide the content generation.", default='')
    parser.add_argument(
        "--file_paths",
        nargs="+",
        default=[],
        help="A list of file paths to include in the prompt as context (space-separated).",
    )
    parser.add_argument(
        "--api_key", help="The Google Gemini API key. If not provided, it will be read from the GEMINI_API_KEY environment variable."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Set logging level to DEBUG."
    )
    parser.add_argument(
        "--model_name", default="gemini-2.0-flash", help="The name of the Gemini model to use. Defaults to 'gemini-2.0-flash'."
    )
    parser.add_argument(
        "--output_file", help="The path to the file where the generated content will be written. If not provided, output to stdout."
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Initialize the API
    try:
        api = GeminiRepoAPI(api_key=args.api_key, model_name=args.model_name)
        log_data = {"status": "GeminiRepoAPI initialized successfully"}
        logger.info(json.dumps(log_data))
    except ValueError as e:
        log_data = {"error": str(e)}
        logger.error(json.dumps(log_data))
        print(f"Error initializing GeminiRepoAPI: {e}")
        return
    except Exception as e:
        log_data = {"error": str(e)}
        logger.exception(json.dumps(log_data))
        print(f"Error initializing GeminiRepoAPI: {e}")
        return

    # Generate the content
    try:
        generated_content = api.generate_content(
            repo_name=args.repo_name,
            file_paths=args.file_paths,
            target_file_name=args.target_file_name,
            prompt=args.prompt,
        )
        log_data = {"status": "Content generated successfully"}
        logger.info(json.dumps(log_data))
    except Exception as e:
        log_data = {"error": str(e)}
        logger.exception(json.dumps(log_data))
        print(f"Error generating content: {e}")
        return

    # Output the generated content
    if args.output_file:
        try:
            with open(args.output_file, "w") as f:
                f.write(generated_content)
            log_data = {"output_file": args.output_file, "status": "Content written to file"}
            logger.info(json.dumps(log_data))
            print(f"Content written to {args.output_file}")
        except Exception as e:
            log_data = {"output_file": args.output_file, "error": str(e)}
            logger.exception(json.dumps(log_data))
            print(f"Error writing to file {args.output_file}: {e}")
            return
    else:
        print(generated_content)
        log_data = {"status": "Content printed to stdout"}
        logger.info(json.dumps(log_data))


if __name__ == "__main__":
    main()