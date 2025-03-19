# Usage

This section provides detailed instructions on how to use the Gemini Repo CLI.

## Command-Line Syntax

```bash
gemini-repo-cli --model <model_name> --repo <repository_name> --prompt "<your_prompt>" <file1> <file2> ... <target_file>
```

* `gemini-repo-cli`: The command to execute the tool.
* `--model <model_name>`: *(Optional)* Specifies the Gemini model to use (e.g., `gemini-2.0-flash`). Defaults to `gemini-2.0-flash`.
* `--repo <repository_name>`: *(Optional)* Specifies the name of the repository. Defaults to `awesome-ai`.  This is used in the prompt context.
* `--prompt "<your_prompt>"`: *(Required)* The prompt to guide the Gemini model. Enclose the prompt in double quotes. Be as specific as possible.
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

## Best Practices

* **Prompt Engineering:** The quality of the generated content depends heavily on the prompt. Experiment with different prompts to achieve the desired results. Provide clear and specific instructions.
* **Context Selection:**  Choose context files that are most relevant to the target file and the task you want to accomplish.
* **Output Redirection:** Redirect the output to a file if you need to save the generated content:

   ```bash
   gemini-repo-cli --model gemini-1.5-pro-latest --repo my-project --prompt "..." file1.py file2.py target.py > output.txt
   ```
