# Gemini Repo CLI

A command-line tool to generate content for a target file using Large Language Models (LLMs), leveraging existing repository files as context.  Currently supports Google Gemini and local Ollama models.

## 🎉 What's New! 🎉

* **Ollama Support!** You can now use local Ollama models for content generation. This allows for offline usage and greater control over your LLM.
* **Improved Logging:** Structured JSON logging provides better debugging and monitoring capabilities.
* **More Gemini Models:**  You can now specify different Gemini models, including the latest `gemini-2.0-flash`.

## Features

* Generates content based on a given prompt.
* Uses specified files from a repository as context for content generation.
* Supports specifying the LLM provider (Gemini or Ollama) and model to use.
* Outputs generated content to the console or a file.
* Uses structured JSON logging for better debugging and monitoring.

## Getting Started

### Prerequisites

* Python 3.8 or higher
* pip (Python package installer)
* For Gemini: A Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))
* For Ollama: A local installation of [Ollama](https://ollama.com/) and a compatible model pulled (e.g., `ollama pull qwen2.5-coder:1.5b`).

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

#### Gemini

1. **Set the Gemini API Key:**

    You **must** set your Google Gemini API key as an environment variable.

    ```bash
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

    *(Replace `YOUR_GEMINI_API_KEY` with your actual API key.) You might want to add this line to your `.bashrc` or `.zshrc` file for persistence.*

#### Ollama

1. **Ensure Ollama is running:**

    Start your local Ollama server.  The default host is `http://localhost:11434`.

2. **Pull a model:**

    Use the `ollama pull` command to download a model to your local machine. For example:

    ```bash
    ollama pull qwen2.5-coder:1.5b
    ```

## Usage

```bash
gemini-repo-cli <repo_name> <target_file_name> <prompt> [--provider <provider>] [--files <file_path1> <file_path2> ...] [--output <output_file>] [--gemini-api-key <api_key>] [--gemini-model <model_name>] [--ollama-model <model_name>] [--ollama-host <host>] [--debug]
```

### Arguments

* `<repo_name>`: The name of the repository (used for context).
* `<target_file_name>`: The name of the target file to generate.
* `<prompt>`: The prompt to guide the content generation.

### Options

* `--provider <provider>`: The LLM provider to use.  Choices are `gemini` (default) or `ollama`.
* `--files <file_path1> <file_path2> ...`: A list of file paths to include in the prompt as context (space-separated).
* `--output <output_file>`: The path to the file where the generated content will be written. If not provided, output to stdout.
* `--debug`: Enable debug logging.

#### Gemini Options (used if `--provider=gemini`)

* `--gemini-api-key <api_key>`: The Google Gemini API key. If not provided, it will be read from the `GEMINI_API_KEY` environment variable.
* `--gemini-model <model_name>`: The name of the Gemini model to use. Defaults to `gemini-2.0-flash`.  Consider trying `gemini-1.5-pro-latest` for more advanced tasks!

#### Ollama Options (used if `--provider=ollama`)

* `--ollama-model <model_name>`: The name of the Ollama model to use. Defaults to `qwen2.5-coder:1.5b`.
* `--ollama-host <host>`: The Ollama host URL (e.g., `http://localhost:11434`). If not provided, it will use the default or the `OLLAMA_HOST` environment variable.

### Examples

#### Gemini Examples

1. **Generate content and print to stdout:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --files utils.py helper.py
    ```

2. **Generate content and write to a file:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --files utils.py helper.py --output factorial.py
    ```

3. **Specify the API key and model name:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --gemini-api-key YOUR_API_KEY --gemini-model gemini-1.5-pro-latest
    ```

#### Ollama Examples

1. **Generate content using Ollama and print to stdout:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --provider ollama --files utils.py helper.py
    ```

2. **Specify the Ollama model:**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --provider ollama --ollama-model codellama:34b --files utils.py
    ```

3. **Specify the Ollama host (if not the default):**

    ```bash
    gemini-repo-cli my-project my_new_file.py "Implement a function to calculate the factorial of a number." --provider ollama --ollama-host http://my-ollama-server:11434 --files utils.py
    ```

## Troubleshooting

* **Gemini API Key Issues:** Double-check that your `GEMINI_API_KEY` environment variable is correctly set and that the API key is valid.
* **Ollama Connection Errors:** Ensure that your Ollama server is running and accessible at the specified host and port.  Verify that the model you are trying to use has been pulled.
* **Context Issues:**  Make sure the file paths specified with `--files` are correct and that the files exist in your repository.
* **General Errors:** Enable debug logging with the `--debug` flag for more detailed error messages.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
