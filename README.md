# Gemini Repo CLI

This command-line tool facilitates generating code or text for a specific target file, leveraging the Google Gemini API and contextual information from other files within a repository.  It's designed to help automate code completion, documentation generation, or any task where understanding existing code is beneficial.

## Features

* **Context-Aware Generation:**  Provides the Gemini model with relevant context from specified files within a repository.
* **Customizable Prompts:** Allows you to guide the model with a specific prompt tailored to your desired outcome.
* **Flexible Input:**  Accepts a list of context files and a target file, enabling focused generation.
* **Streamed Output:**  Displays the model's generated output in real-time as it's produced.
* **Easy Configuration:**  Uses environment variables for API key management.

## Installation

1. **Clone the Repository (if you haven't already):**

    ```bash
    git clone <your_repository_url>  # Replace with your actual repository URL
    cd <your_repository_directory> # Replace with your actual repository directory
    ```

2. **Install Dependencies:**

    ```bash
    pip install google-generative-ai
    ```

    *(Ensure you have Python and pip installed.)*

3. **Install the CLI tool:**

    ```bash
    pip install -e .
    ```

    *(Run this from the same directory where `setup.py` exists.)*

## Configuration

1. **Set the Gemini API Key:**

    You **must** set your Google Gemini API key as an environment variable.  Get your API key from the [Google AI Studio](https://makersuite.google.com/app/apikey).

    ```bash
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

    *(Replace `YOUR_GEMINI_API_KEY` with your actual API key.)  You might want to add this line to your `.bashrc` or `.zshrc` file for persistence.*

## Usage

```bash
gemini-repo-cli --model <model_name> --repo <repository_name> --prompt "<your_prompt>" <file1> <file2> ... <target_file>
```

* `gemini-repo-cli`:  The command to execute the tool.
* `--model <model_name>`:  *(Optional)* Specifies the Gemini model to use (e.g., `gemini-2.0-flash`). Defaults to `gemini-2.0-flash`.
* `--repo <repository_name>`: *(Optional)* Specifies the name of the repository.  Defaults to `awesome-ai`.  This is used in the prompt context.
* `--prompt "<your_prompt>"`:  *(Required)*  The prompt to guide the Gemini model. Enclose the prompt in double quotes.  Be as specific as possible.
* `<file1> <file2> ...`:  A list of files to use as context for the model.
* `<target_file>`:  The target file for which you want to generate content.  The generated content will be printed to the console.

**Important:** The order of the files matters.  List the context files first, followed by the target file.

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

## Notes

* The tool reads the content of each file and includes it in the prompt to the Gemini model.
* The output is streamed to the console.  You can redirect it to a file if needed (e.g., `gemini-repo-cli ... > output.txt`).
* Ensure that the specified files exist and are readable.
* The quality of the generated content depends heavily on the prompt and the context provided. Experiment with different prompts to achieve the desired results.
* Error messages are printed to the console if a file is not found.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## Contact

For any questions or feedback, please open an issue on the GitHub repository.
