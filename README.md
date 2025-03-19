# Gemini Repo CLI

A command-line tool that leverages the Google Gemini API to generate code or text for a target file, using contextual information from other files within a repository.

## Key Features

* **Context-Aware Generation:** Utilizes relevant context from specified files to generate content.
* **Customizable Prompts:** Allows tailoring prompts for desired outcomes with clear and specific instructions.
* **Flexible Input:** Accepts multiple context files and a target file.
* **Streamed Output:** Displays the generated output in real-time.

## Prerequisites

* Python 3.8 or higher
* pip (Python package installer)
* A Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/deniskropp/gemini-repo-cli.git
    cd gemini-repo-cli
    ```

2. **Install the dependencies and the CLI tool:**

    ```bash
    pip install -e .
    ```

    *(Run this from the same directory where `setup.py` exists.)*

## Configuration

1. **Set the Gemini API Key:**

    You **must** set your Google Gemini API key as an environment variable.

    ```bash
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

    *(Replace `YOUR_GEMINI_API_KEY` with your actual API key.) You might want to add this line to your `.bashrc` or `.zshrc` file for persistence.*

## Usage

```bash
gemini-repo-cli --model <model_name> --repo <repository_name> --prompt "<your_prompt>" <file1> <file2> ... <target_file>
```

* `gemini-repo-cli`: The command to execute the tool.
* `--model <model_name>`: *(Optional)* Specifies the Gemini model to use (e.g., `gemini-2.0-flash`). Defaults to `gemini-2.0-flash`.
* `--repo <repository_name>`: *(Optional)* Specifies the name of the repository. Defaults to `awesome-ai`.  This is used in the prompt context.
* `--prompt "<your_prompt>"`: *(Required)* The prompt to guide the Gemini model. Enclose the prompt in double quotes. Be as specific as possible.  Prompt engineering is key - the better the prompt, the better the result.
* `<file1> <file2> ...`: A list of files to use as context for the model.
* `<target_file>`: The target file for which you want to generate content. The generated content will be printed to the console.

**Important:** The order of the files matters. List the context files first, followed by the target file.

## Examples

1. **Generate a function implementation based on context files:**

    ```bash
    gemini-repo-cli --model gemini-1.5-pro-latest --repo my-project --prompt "Implement a function called 'calculate_average' that calculates the average of a list of numbers." utils.py data_processing.py average_calculator.py
    ```

    This command uses `utils.py` and `data_processing.py` as context to generate code for the `average_calculator.py` file.

2. **Generate documentation for a class:**

    ```bash
    gemini-repo-cli --repo my-library --prompt "Generate docstrings for the 'MyClass' class, including descriptions of the attributes and methods." my_class.py
    ```

    This generates docstrings for the `MyClass` class defined in `my_class.py`.

3. **Redirect Output to a File:**

   ```bash
   gemini-repo-cli --model gemini-1.5-pro-latest --repo my-project --prompt "..." file1.py file2.py target.py > output.txt
   ```

   Saves the generated content to `output.txt`.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Documentation

For more detailed documentation, please see the [docs](docs/) directory.  It contains:

* [Getting Started](docs/getting_started.md): Installation and configuration.
* [Usage](docs/usage.md): Detailed usage instructions and examples.
* [Contributing](docs/contributing.md): Guidelines for contributing to the project.
* [License](docs/license.md): License information.
