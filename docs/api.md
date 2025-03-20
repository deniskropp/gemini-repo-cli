# GeminiRepoAPI Class Documentation

This document provides detailed information about the `GeminiRepoAPI` class, which facilitates interaction with the Google Gemini API for generating content based on a repository context.

## Overview

The `GeminiRepoAPI` class encapsulates the logic for authenticating with the Google Gemini API, constructing prompts with relevant file context, and generating content based on a given prompt. It leverages the `google.genai` library for interacting with the Gemini API.

## Class Definition

```python
class GeminiRepoAPI:
    """
    A class to interact with the Google Gemini API for generating content based on a repository context.
    """
```

## Constructor (`__init__`)

```python
def __init__(self, api_key: str = None, model_name: str = DEFAULT_MODEL):
    """
    Initializes the GeminiRepoAPI with an API key and model name.

    Args:
        api_key: The Google Gemini API key. If not provided, it will be read from the GEMINI_API_KEY environment variable.
        model_name: The name of the Gemini model to use. Defaults to 'gemini-2.0-flash'.
    """
```

The constructor initializes the `GeminiRepoAPI` instance. It accepts an optional API key and model name. If the API key is not provided, it attempts to retrieve it from the `GEMINI_API_KEY` environment variable. It then initializes the Gemini client using the provided API key and sets up a default generation configuration.

**Parameters:**

* `api_key` (str, optional): The Google Gemini API key. Defaults to `None`.
* `model_name` (str, optional): The name of the Gemini model to use. Defaults to `DEFAULT_MODEL` (which is `gemini-2.0-flash`).

**Raises:**

* `ValueError`: If the `GEMINI_API_KEY` environment variable is not set and no `api_key` is provided.
* `Exception`: If the Gemini client fails to initialize.

**Example:**

```python
api = GeminiRepoAPI(api_key="YOUR_API_KEY", model_name="gemini-1.5-pro-latest")
```

## Method: `generate_content`

```python
def generate_content(self, repo_name: str, file_paths: List[str], target_file_name: str, prompt: str) -> str:
    """
    Generates content for a target file based on the provided context files and prompt.

    Args:
        repo_name: The name of the repository.
        file_paths: A list of file paths to include in the prompt as context.
        target_file_name: The name of the target file to generate.
        prompt: The prompt to guide the generation.

    Returns:
        The generated content as a string.

    Raises:
        Exception: If an error occurs during content generation.
    """
```

This method is the core functionality of the class. It takes a repository name, a list of file paths for context, a target file name, and a prompt as input. It constructs a prompt using the provided information and sends it to the Gemini API to generate content.

**Parameters:**

* `repo_name` (str): The name of the repository.
* `file_paths` (List[str]): A list of file paths to use as context.
* `target_file_name` (str): The name of the target file for which to generate content.
* `prompt` (str): The prompt to guide the content generation.

**Returns:**

* str: The generated content.

**Raises:**

* `Exception`: If an error occurs during content generation.

**Example:**

```python
generated_code = api.generate_content(
    repo_name="my-project",
    file_paths=["utils.py", "data_processing.py"],
    target_file_name="average_calculator.py",
    prompt="Implement a function called 'calculate_average' that calculates the average of a list of numbers."
)
print(generated_code)
```

## Constants

* `DEFAULT_MODEL`:  A string representing the default Gemini model to use, which is `gemini-2.0-flash`.

## Logging

The class uses the `logging` module to log information, warnings, and errors.  Log messages are formatted to include the timestamp, log level, and message.  JSON formatting is used for structured logging.

## Error Handling

The class includes comprehensive error handling, including:

* Checking for the presence of the `GEMINI_API_KEY` environment variable.
* Handling file not found errors.
* Catching exceptions during API calls.
* Logging errors and exceptions.

## Usage Example

```python
from gemini_repo import GeminiRepoAPI

# Initialize the API with your API key
api = GeminiRepoAPI(api_key="YOUR_API_KEY")

# Define the parameters for content generation
repo_name = "my-project"
file_paths = ["utils.py", "data_processing.py"]
target_file_name = "average_calculator.py"
prompt = "Implement a function called 'calculate_average' that calculates the average of a list of numbers."

# Generate the content
try:
    generated_code = api.generate_content(repo_name, file_paths, target_file_name, prompt)
    print(generated_code)
except Exception as e:
    print(f"Error generating content: {e}")
```
