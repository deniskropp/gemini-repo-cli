# Awesome Gemini Repo CLI

A curated list of resources, examples, and tools related to the Gemini Repo CLI, along with inspiring prompts and use cases to maximize the tool's potential.

## I. Use Cases & Prompts

These examples demonstrate how to use the Gemini Repo CLI for various code-related tasks.  The `--prompt` argument is crucial for guiding the AI effectively.

### A. Code Generation

* **Implement a Function:** Use context files to guide the implementation of a function.

    ```bash
    gemini-repo-cli --model gemini-1.5-pro-latest --repo my-project --prompt "Implement a function called 'calculate_average' that calculates the average of a list of numbers. Ensure error handling for empty lists." utils.py data_processing.py average_calculator.py
    ```

  * `utils.py`, `data_processing.py`: Context files providing utility functions and data processing logic.
  * `average_calculator.py`: The target file where the `calculate_average` function will be generated.

* **Generate Unit Tests:** Generate unit tests for a given function or class.

    ```bash
    gemini-repo-cli --repo my-library --prompt "Generate unit tests for the 'MyClass' class using pytest.  Cover edge cases." my_class.py test_my_class.py
    ```

  * `my_class.py`: The file containing the class to be tested.
  * `test_my_class.py`: The target file where the unit tests will be generated.

### B. Documentation

* **Generate Docstrings:** Generate docstrings for a class, including descriptions of attributes and methods.

    ```bash
    gemini-repo-cli --repo my-library --prompt "Generate docstrings for the 'MyClass' class, including descriptions of the attributes and methods." my_class.py
    ```

  * `my_class.py`: The file containing the class for which docstrings will be generated.

* **Create API Documentation:** Generate API documentation from code comments and docstrings. Requires a prompt that guides the AI to use specific documentation formats (e.g., reStructuredText, Markdown).

    ```bash
    gemini-repo-cli --repo my-api --prompt "Generate API documentation in Markdown format for the endpoints defined in this file." api_endpoints.py api_docs.md
    ```

  * `api_endpoints.py`: The file containing the API endpoint definitions.
  * `api_docs.md`: The target file where the API documentation will be generated.

### C. Refactoring

* **Add Type Hints:** Add type hints to a Python file.

    ```bash
    gemini-repo-cli --repo my-project --prompt "Add type hints to all functions and methods in this file." my_module.py
    ```

  * `my_module.py`: The file to which type hints will be added.

* **Improve Code Readability:** Refactor code to improve readability and maintainability.

    ```bash
    gemini-repo-cli --repo my-project --prompt "Refactor this code to improve readability and follow PEP 8 guidelines. Use list comprehensions where appropriate." legacy_code.py refactored_code.py
    ```

  * `legacy_code.py`: The file containing the code to be refactored.
  * `refactored_code.py`: The target file where the refactored code will be generated.

### D. Other Use Cases

* **Generate Configuration Files:** Create configuration files based on a schema or example.

    ```bash
    gemini-repo-cli --repo my-app --prompt "Generate a YAML configuration file based on the following schema: [insert schema here]." config_schema.txt config.yaml
    ```

  * `config_schema.txt`: A file containing the configuration schema.
  * `config.yaml`: The target configuration file.

* **Translate Code Comments:** Translate code comments from one language to another.

    ```bash
    gemini-repo-cli --repo my-project --prompt "Translate all code comments in this file from English to Spanish." my_code.py
    ```

  * `my_code.py`: The file containing the code comments to be translated.

## II. Examples (Expanded)

These examples provide specific, practical demonstrations of the Gemini Repo CLI's capabilities.

* **Generating Docstrings:** Example usage for generating docstrings for a Python class. Demonstrates effective prompt engineering for documentation tasks.

    ```bash
    gemini-repo-cli --repo my-library --prompt "Generate docstrings for the 'MyClass' class, including descriptions of the attributes and methods." my_class.py
    ```

* **Implementing a Function:** An example of using context files to implement a specific function.

    ```bash
    gemini-repo-cli --model gemini-1.5-pro-latest --repo my-project --prompt "Implement a function called 'calculate_average' that calculates the average of a list of numbers. Ensure error handling for empty lists." utils.py data_processing.py average_calculator.py
    ```

* **Refactoring Code:** Example of refactoring existing code using context.

    ```bash
    gemini-repo-cli --repo legacy-code --prompt "Refactor the 'process_data' function to improve readability and performance. Use list comprehensions where appropriate." data_processor.py
    ```

* **Generating Unit Tests:** Example of creating unit tests for a function.

    ```bash
    gemini-repo-cli --repo my-project --prompt "Generate unit tests for the 'calculate_sum' function in the 'calculator.py' file. Cover edge cases such as negative numbers and zero." calculator.py test_calculator.py
    ```

## III. Resources

* **Google Gemini API Documentation:** [https://ai.google.dev/](https://ai.google.dev/) - Official documentation for the Google Gemini API.
* **Prompt Engineering Guide:** [https://www.promptingguide.ai/](https://www.promptingguide.ai/) - A comprehensive guide to prompt engineering techniques. Helpful for crafting effective prompts for the Gemini Repo CLI.

## IV. Tips & Tricks

* **Detailed Prompts:** The more detail you provide in your prompt, the better the generated output will be. Be specific about the desired functionality, style, and any constraints.
* **Context Selection:** Carefully select the context files that are most relevant to the target file and the task. Irrelevant context can confuse the model and lead to poor results.
* **Iterative Refinement:** Use the Gemini Repo CLI in an iterative process. Start with a basic prompt and refine it based on the generated output. This allows you to fine-tune the results to meet your specific needs.
* **Error Handling:** Consider how to handle potential errors in the generated code. Include instructions in your prompt to add error handling where appropriate.
* **Output Redirection:** Use output redirection to save the generated content to a file for further editing and refinement:

    ```bash
    gemini-repo-cli --model gemini-1.5-pro-latest --repo my-project --prompt "..." file1.py file2.py target.py > output.txt
    ```

## V. Related Tools

* **grep:** Use `grep` to quickly search for relevant context within your repository files before using the CLI. This helps identify the best files to include as context.

    ```bash
    grep -rnw . -e "calculate_average"
    ```

* **sed:** Use `sed` to pre-process the generated output before saving it to a file. This can be useful for formatting or making minor adjustments.

## VI. Contributing

If you have any awesome examples, resources, or tips & tricks to share, please submit a pull request!

## VII. License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
