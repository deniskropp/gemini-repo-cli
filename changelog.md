# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

* Comprehensive documentation in the `docs/` directory, including:
  * [Getting Started](docs/getting_started.md): Installation and configuration guide.
  * [Usage](docs/usage.md): Detailed usage instructions and examples.
  * [Contributing](docs/contributing.md): Guidelines for contributing to the project.
  * [License](docs/license.md): License information.
* `awesome.md` file with demo use cases.
* Logging using the `logging` module for debugging and error tracking.  Log level can be configured via the `--log_level` argument.
* Clearer error messages and user feedback.
* More robust handling of file reading errors.
* Support for loading prompts from files using the `--prompt` argument.
* More detailed logging of CLI arguments and model configuration.

### Changed

* Refactored the prompt construction logic for better readability and maintainability.
* Improved the structure of the `README.md` file with more detailed information and links to the documentation.
* Updated the `setup.py` file with more metadata and classifiers.
* Improved argument parsing with `argparse` for better user experience.
* The tool now streams output from the Gemini API for real-time display.
* The tool now uses `google.genai.Client` instead of `genai` directly.
* The tool now uses `google.genai.types.GenerateContentConfig` for configuring content generation.
* The tool now uses `generate_content_stream` for streaming the output.
* The tool now supports multiple prompts via the `--prompt` argument.

### Fixed

* Fixed an issue where the API key was not being properly loaded from the environment.
* Fixed an issue where the prompt was not being properly constructed.
* Fixed an issue where the output was not being properly displayed.

## [0.1.0] - 2024-05-03

### Added

* Initial release of the Gemini Repo CLI.
* Basic functionality for generating content based on context files and a prompt.
* Support for specifying the model and repository name.
* Command-line interface using `argparse`.
