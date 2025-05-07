# Awesome `gemini-repo-cli`: Creative Applications

Welcome to the showcase of creative applications for `gemini-repo-cli`! This tool isn't just for straightforward code generation; its ability to leverage repository context with powerful LLMs opens up a world of possibilities. Below are some examples to inspire you.

## 1. Code Generation & Augmentation

Beyond generating full scripts, `gemini-repo-cli` can assist in various coding tasks.

### a. Generating Unit Tests

Quickly scaffold unit tests for your existing functions.

**Goal:** Create Pytest unit tests for a function in `calculator.py`.
**Context Files:** `src/calculator.py` (containing the function to be tested).

```bash
gemini-repo-cli my-calculator-project test_calculator.py \
  "Write pytest unit tests for the 'add' and 'subtract' functions in 'src/calculator.py'. Include tests for positive numbers, negative numbers, and zero." \
  --files src/calculator.py \
  --output tests/test_calculator.py
```

### b. Translating Code Snippets

Translate functions or small scripts between languages (experimental, quality depends on the LLM).

**Goal:** Translate a Python utility function to JavaScript.
**Context Files:** `utils/helpers.py` (containing the Python function).

```bash
gemini-repo-cli python-to-js-project translated_helper.js \
  "Translate the Python function 'format_user_data' from 'utils/helpers.py' into an equivalent JavaScript function. Maintain the same input/output structure." \
  --files utils/helpers.py \
  --output static/js/translated_helper.js \
  --gemini-model gemini-1.5-pro-latest
```

## 2. Documentation & Explanation

Leverage the LLM's understanding of your code to generate helpful documentation.

### a. Explaining Complex Code for Documentation

Generate human-readable explanations for complex code sections.

**Goal:** Create a markdown explanation for a tricky algorithm in `core_processing.py`.
**Context Files:** `lib/core_processing.py`.

```bash
gemini-repo-cli my-complex-lib algorithm_explanation.md \
  "Explain the 'recursive_optimization_algorithm' function found in 'lib/core_processing.py'. Describe its purpose, inputs, outputs, and provide a high-level overview of its steps. Target audience is a new developer joining the team." \
  --files lib/core_processing.py \
  --output docs/explanations/recursive_optimization.md
```

### b. Generating README Sections

Draft sections for your `README.md` based on project files or feature descriptions.

**Goal:** Create a "Key Features" section for a new utility's README.
**Context Files:** `src/main_cli.py`, `docs/feature_list.txt`.

```bash
gemini-repo-cli my-new-util readme_features.md \
  "Generate a 'Key Features' section for a README.md. The tool is a command-line utility for image processing. Use 'src/main_cli.py' to understand its commands and 'docs/feature_list.txt' for a summary of features. Present as a bulleted list." \
  --files src/main_cli.py docs/feature_list.txt \
  --output temp/readme_features_section.md
```

## 3. Project Management & Workflow

Streamline parts of your development workflow.

### a. Drafting Git Commit Messages

Get help crafting informative commit messages (especially useful with local models for speed).

**Goal:** Generate a git commit message summarizing changes.
**Context Files:** `src/auth_service.py`, `src/user_model.py` (files that were changed).

```bash
gemini-repo-cli my-app-backend suggested_commit.txt \
  "Draft a git commit message in conventional commit format. The changes involve adding two-factor authentication. Key files modified are 'src/auth_service.py' and 'src/user_model.py'." \
  --files src/auth_service.py src/user_model.py \
  --provider ollama \
  --ollama-model qwen2.5-coder:1.5b
```
*(Note: For actual commit message generation based on diffs, you might pipe a `git diff` output into the prompt or a temporary file used as context.)*

## 4. Content Creation

Use `gemini-repo-cli` for various writing tasks, using your existing documents as a base.

### a. Drafting Blog Post Snippets

Generate initial drafts for blog posts or articles.

**Goal:** Write an introductory paragraph for a blog post about a new product feature.
**Context Files:** `release_notes/v2.5.md`, `marketing/feature_brief_super_sort.txt`.

```bash
gemini-repo-cli company-blog blog_intro_super_sort.md \
  "Draft an engaging introductory paragraph for a blog post announcing our new 'SuperSort' algorithm. Highlight its speed and efficiency improvements for users. Refer to 'release_notes/v2.5.md' and 'marketing/feature_brief_super_sort.txt' for key details." \
  --files release_notes/v2.5.md marketing/feature_brief_super_sort.txt \
  --output drafts/blog_intro_super_sort.md
```

## 5. DevOps & Configuration

Automate the creation of boilerplate configuration files.

### a. Generating a Basic Dockerfile

Scaffold a Dockerfile for your application.

**Goal:** Create a simple Dockerfile for a Python FastAPI application.
**Context Files:** `requirements.txt`, `main.py` (the FastAPI app).

```bash
gemini-repo-cli my-fastapi-app Dockerfile \
  "Generate a basic Dockerfile for a Python FastAPI application. The main application file is 'main.py', and dependencies are listed in 'requirements.txt'. The application runs on port 8000 using uvicorn." \
  --files main.py requirements.txt \
  --output Dockerfile
```

## 6. Creative Writing & Brainstorming

Tap into the LLM's creative potential.

### a. Story Snippet Generation

Kickstart a creative writing project.

**Goal:** Write an opening scene for a sci-fi story.
**Context Files:** `characters/aria_bio.txt`, `characters/zed_bio.txt`, `world/neon_city_description.txt`.

```bash
gemini-repo-cli sci-fi-novel chapter1_scene1.md \
  "Write a short, intriguing opening scene (approx. 300 words) for a sci-fi story. It features Aria, a rebellious hacker (details in 'characters/aria_bio.txt'), and Zed, a repurposed security drone (details in 'characters/zed_bio.txt'). They are trying to evade capture in the underbelly of Neon City (described in 'world/neon_city_description.txt'). Focus on atmosphere and suspense." \
  --files characters/aria_bio.txt characters/zed_bio.txt world/neon_city_description.txt \
  --provider ollama \
  --ollama-model llama3 \
  --output story_ideas/chapter1_opening.md
```

### b. Brainstorming Project Ideas

Generate ideas based on existing notes or code.

**Goal:** Brainstorm new features for an existing to-do list application.
**Context Files:** `src/todo_app.py`, `docs/current_features.md`, `user_feedback.txt`.

```bash
gemini-repo-cli todo-app-v2 new_feature_ideas.md \
  "Brainstorm 5 innovative new features for a to-do list application. The current application code is in 'src/todo_app.py', existing features are listed in 'docs/current_features.md', and user feedback is in 'user_feedback.txt'. Focus on features that would improve productivity and user engagement." \
  --files src/todo_app.py docs/current_features.md user_feedback.txt
```

---

These are just a few examples. The power of `gemini-repo-cli` lies in its flexibility. Experiment with different prompts, context files, and LLM providers/models to discover even more creative uses for your projects!
