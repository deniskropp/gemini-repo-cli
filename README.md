# Gemini Repo CLI

A command-line tool to generate content for a target file using the Google Gemini API, leveraging existing repository files as context.

## Features

* Generates content based on a given prompt.
* Uses specified files from a repository as context for content generation.
* Supports specifying the Gemini model to use.
* Outputs generated content to the console or a file.
* Uses structured logging for better debugging and monitoring.

## Getting Started

### Prerequisites

* Python 3.8 or higher
* pip (Python package installer)
* A Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the Repository:**

    ```bash
    gh repo clone deniskropp/gemini-repo-cli
    cd gemini-repo-cli
    ```

2. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Install the CLI tool:**

    ```bash
    pip install -e .
    ```

    *(Run this from the same directory where `setup.py` exists.)*

### Configuration

1. **Set the Gemini API Key:**

    You **must** set your Google Gemini API key as an environment variable.

    ```bash
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

    *(Replace `YOUR_GEMINI_API_KEY` with your actual API key.) You might want to add this line to your `.bashrc` or `.zshrc` file for persistence.*

## Usage

```bash
gemini-repo-cli <repo_name> <target_file_name> <prompt> [--file_paths <file_path1> <file_path2> ...] [--api_key <api_key>] [--model_name <model_name>] [--output_file <output_file>]
```

### Arguments

* `<repo_name>`: The name of the repository.
* `<target_file_name>`: The name of the target file to generate.
* `<prompt>`: The prompt to guide the content generation.

### Options

* `--file_paths <file_path1> <file_path2> ...`: A list of file paths to include in the prompt as context (space-separated).
* `--api_key <api_key>`: The Google Gemini API key. If not provided, it will be read from the `GEMINI_API_KEY` environment variable.
* `--model_name <model_name>`: The name of the Gemini model to use. Defaults to `gemini-2.0-flash`.
* `--output_file <output_file>`: The path to the file where the generated content will be written. If not provided, output to stdout.

### Examples

1. **Generate content and print to stdout:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --file_paths utils.py helper.py
    ```

2. **Generate content and write to a file:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --file_paths utils.py helper.py --output_file factorial.py
    ```

3. **Specify the API key and model name:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --api_key YOUR_API_KEY --model_name gemini-1.5-pro-latest
    ```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
