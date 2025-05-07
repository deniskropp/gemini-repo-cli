# src/gemini_repo/ui.py

import sys
import os
import logging
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
        QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QStackedWidget,
        QFileDialog, QCheckBox, QStatusBar, QListWidget, QListWidgetItem, QMessageBox,
        QGroupBox
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    # from PyQt6.QtGui import QIcon # For window icon, optional
except ImportError:
    print("PyQt6 is not installed. Please install it: pip install PyQt6")
    sys.exit(1)

# Import API classes and constants from the project
from gemini_repo import (
    GeminiRepoAPI,
    OllamaRepoAPI,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_HOST, # Make sure this is added to gemini_repo/__init__.py
)
from gemini_repo.base_api import BaseRepoAPI # For type hinting
from gemini_repo.cli import setup_logging # To use the same logging setup

# Get logger for the UI module
logger = logging.getLogger(__name__) # Will be gemini_repo.ui


# --- Generation Worker Thread ---
class GenerationWorker(QThread):
    """
    Worker thread to handle time-consuming API calls for content generation
    without freezing the GUI.
    """
    started_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)  # Emits generated content
    error_signal = pyqtSignal(str)     # Emits error message
    # progress_signal = pyqtSignal(str) # Optional: for more granular progress

    def __init__(self, api_instance: BaseRepoAPI, repo_name: str, file_paths: list[str],
                 target_file_name: str, prompt: str):
        super().__init__()
        self.api_instance = api_instance
        self.repo_name = repo_name
        self.file_paths = file_paths
        self.target_file_name = target_file_name
        self.prompt = prompt

    def run(self):
        try:
            self.started_signal.emit(f"Generating content with {self.api_instance.__class__.__name__} (model: {self.api_instance.model_name}) for target '{self.target_file_name}'...")
            logger.info({
                "event": "ui_generation_thread_start",
                "provider": self.api_instance.__class__.__name__,
                "model": self.api_instance.model_name,
                "target_file": self.target_file_name
            })
            # The actual API call
            content = self.api_instance.generate_content(
                repo_name=self.repo_name,
                file_paths=self.file_paths,
                target_file_name=self.target_file_name,
                prompt=self.prompt
            )
            self.finished_signal.emit(content)
            logger.info({"event": "ui_generation_thread_success", "output_length": len(content)})
        except FileNotFoundError as e:
            logger.error({"event": "ui_generation_thread_error", "error_type": "FileNotFoundError", "message": str(e)})
            self.error_signal.emit(f"Context file not found: {e}")
        except Exception as e:
            # API classes' generate_content methods usually log details of API errors
            logger.exception({"event": "ui_generation_thread_error", "error_type": str(type(e).__name__), "message": str(e)})
            self.error_signal.emit(f"Generation failed: {e}")


# --- Main UI Window ---
class GeminiRepoUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Repo - Interactive UI")
        # self.setWindowIcon(QIcon("path/to/your/icon.png")) # Optional

        # Initial logging setup (can be changed by debug checkbox)
        # This will setup JSON logging to stderr, same as CLI
        setup_logging(debug=False)
        logger.info({"event": "ui_start"}) # This log goes to stderr as JSON

        self.current_api_instance = None
        self.generation_worker = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Left Pane: Inputs ---
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_pane.setFixedWidth(450)

        # Provider Selection
        provider_group = QGroupBox("LLM Provider")
        provider_layout = QFormLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Gemini", "Ollama"])
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addRow(QLabel("Provider:"), self.provider_combo)
        provider_group.setLayout(provider_layout)
        left_layout.addWidget(provider_group)

        # Common Inputs
        common_inputs_group = QGroupBox("Common Inputs")
        common_inputs_layout = QFormLayout()
        self.repo_name_edit = QLineEdit("gemini-repo-cli")
        self.target_file_edit = QLineEdit("src/example_output.py")
        self.prompt_edit = QTextEdit("Create an interactive sister of the cli using Qt6")
        self.prompt_edit.setFixedHeight(100) # Adjust height as needed
        common_inputs_layout.addRow("Repository Name:", self.repo_name_edit)
        common_inputs_layout.addRow("Target File Name:", self.target_file_edit)
        common_inputs_layout.addRow("Prompt:", self.prompt_edit)
        common_inputs_group.setLayout(common_inputs_layout)
        left_layout.addWidget(common_inputs_group)

        # Context Files
        context_files_group = QGroupBox("Context Files")
        context_files_layout = QVBoxLayout()
        self.context_files_list = QListWidget()
        self.context_files_list.setFixedHeight(100) # Adjust height
        context_buttons_layout = QHBoxLayout()
        self.add_context_button = QPushButton("Add File(s)")
        self.add_context_button.clicked.connect(self.add_context_files)
        self.remove_context_button = QPushButton("Remove Selected")
        self.remove_context_button.clicked.connect(self.remove_context_file)
        context_buttons_layout.addWidget(self.add_context_button)
        context_buttons_layout.addWidget(self.remove_context_button)
        context_files_layout.addWidget(self.context_files_list)
        context_files_layout.addLayout(context_buttons_layout)
        context_files_group.setLayout(context_files_layout)
        left_layout.addWidget(context_files_group)

        # Provider-Specific Options (Stacked Widget)
        self.provider_options_stack = QStackedWidget()
        self._create_gemini_options_page()
        self._create_ollama_options_page()
        left_layout.addWidget(self.provider_options_stack)
        self.on_provider_changed(0) # Initialize to the first provider's options

        # Output File Configuration
        output_file_group = QGroupBox("Output Configuration")
        output_file_layout = QFormLayout()
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("Optional: Leave blank to display output below")
        browse_output_button = QPushButton("Browse...")
        browse_output_button.clicked.connect(self.browse_output_file)
        output_file_row = QHBoxLayout()
        output_file_row.addWidget(self.output_file_edit)
        output_file_row.addWidget(browse_output_button)
        output_file_layout.addRow("Save to File:", output_file_row)
        output_file_group.setLayout(output_file_layout)
        left_layout.addWidget(output_file_group)

        # Actions & Settings
        actions_group = QGroupBox("Actions & Settings")
        actions_layout = QVBoxLayout()
        self.debug_checkbox = QCheckBox("Enable Debug Logging")
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_logging)
        actions_layout.addWidget(self.debug_checkbox)

        self.generate_button = QPushButton("Generate Content")
        self.generate_button.clicked.connect(self.handle_generate)
        self.generate_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 7px; font-weight: bold; }")
        actions_layout.addWidget(self.generate_button)
        actions_group.setLayout(actions_layout)
        left_layout.addWidget(actions_group)

        left_layout.addStretch() # Pushes widgets to the top
        main_layout.addWidget(left_pane)

        # --- Right Pane: Output ---
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        output_label = QLabel("Generated Content / Status Log:")
        self.output_display_edit = QTextEdit()
        self.output_display_edit.setReadOnly(True)
        self.output_display_edit.setFontFamily("Courier New, Courier, monospace") # Monospaced font
        self.output_display_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # Horizontal scroll for long lines

        clear_output_button = QPushButton("Clear Output Display")
        clear_output_button.clicked.connect(lambda: self.output_display_edit.clear())
        
        right_layout.addWidget(output_label)
        right_layout.addWidget(self.output_display_edit)
        right_layout.addWidget(clear_output_button)
        main_layout.addWidget(right_pane, 1) # Give right pane more stretch factor

        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status("Ready.")

        self.resize(1000, 700) # Initial window size

    def _create_gemini_options_page(self):
        page_widget = QWidget() # Main widget for this page of the stack
        page_layout = QVBoxLayout(page_widget) # Use QVBoxLayout to hold the QGroupBox
        page_layout.setContentsMargins(0,0,0,0)

        group = QGroupBox("Gemini Options")
        layout = QFormLayout()
        self.gemini_api_key_edit = QLineEdit()
        self.gemini_api_key_edit.setPlaceholderText("Optional: Uses GEMINI_API_KEY env var if blank")
        self.gemini_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_model_edit = QLineEdit(DEFAULT_GEMINI_MODEL)
        layout.addRow("API Key:", self.gemini_api_key_edit)
        layout.addRow("Model:", self.gemini_model_edit)
        group.setLayout(layout)
        page_layout.addWidget(group)
        self.provider_options_stack.addWidget(page_widget)

    def _create_ollama_options_page(self):
        page_widget = QWidget()
        page_layout = QVBoxLayout(page_widget)
        page_layout.setContentsMargins(0,0,0,0)

        group = QGroupBox("Ollama Options")
        layout = QFormLayout()
        self.ollama_model_edit = QLineEdit(DEFAULT_OLLAMA_MODEL)
        self.ollama_host_edit = QLineEdit()
        self.ollama_host_edit.setPlaceholderText(f"Optional: Uses OLLAMA_HOST env var or default ({DEFAULT_OLLAMA_HOST})")
        layout.addRow("Model:", self.ollama_model_edit)
        layout.addRow("Host URL:", self.ollama_host_edit)
        group.setLayout(layout)
        page_layout.addWidget(group)
        self.provider_options_stack.addWidget(page_widget)

    def on_provider_changed(self, index):
        self.provider_options_stack.setCurrentIndex(index)
        provider_name = self.provider_combo.currentText()
        logger.info({"event": "ui_provider_changed", "provider": provider_name})
        self.update_status(f"Provider set to {provider_name}.")

    def add_context_files(self):
        # Ensure current directory for file dialog is something sensible, e.g., user's home directory
        home_dir = str(Path.home())
        files, _ = QFileDialog.getOpenFileNames(self, "Select Context Files", home_dir, "All Files (*.*)")
        if files:
            for file_path in files:
                # Avoid adding duplicates
                if not self.context_files_list.findItems(file_path, Qt.MatchFlag.MatchExactly):
                    self.context_files_list.addItem(QListWidgetItem(file_path))
            logger.debug({"event": "ui_context_files_added", "count": len(files), "files": files})

    def remove_context_file(self):
        selected_items = self.context_files_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            file_path_removed = item.text()
            self.context_files_list.takeItem(self.context_files_list.row(item))
            logger.debug({"event": "ui_context_file_removed", "file_path": file_path_removed})

    def browse_output_file(self):
        home_dir = str(Path.home())
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Output As...", home_dir, "All Files (*.*)")
        if file_path:
            self.output_file_edit.setText(file_path)
            logger.debug({"event": "ui_output_file_selected", "file_path": file_path})

    def toggle_debug_logging(self, state):
        is_debug = (state == Qt.CheckState.Checked.value) # Qt.CheckState enum comparison
        setup_logging(debug=is_debug)
        level = "DEBUG" if is_debug else "INFO"
        # This log will use the new setting. If debug is enabled, it appears. If disabled, it doesn't.
        # To ensure it's always logged at INFO about the change:
        logging.getLogger("gemini_repo.ui").info({"event": "ui_debug_logging_toggled", "level": level})
        self.update_status(f"Debug logging {'enabled' if is_debug else 'disabled'}.")

    def handle_generate(self):
        logger.info({"event": "ui_generate_button_clicked"})
        self.generate_button.setEnabled(False)
        self.output_display_edit.clear() # Clear previous output/status
        self.update_status("Initiating generation...")
        self.output_display_edit.append("Attempting to generate content...\n---")

        # --- Gather Inputs ---
        provider = self.provider_combo.currentText()
        repo_name = self.repo_name_edit.text().strip()
        target_file_name_for_prompt = self.target_file_edit.text().strip() # This is for the prompt context
        prompt_text = self.prompt_edit.toPlainText().strip()
        
        context_files = [self.context_files_list.item(i).text() for i in range(self.context_files_list.count())]

        # Basic input validation
        if not repo_name:
            QMessageBox.warning(self, "Input Error", "Repository Name is required.")
            self._reset_generate_button_and_status("Input error: Repository Name required."); return
        if not target_file_name_for_prompt:
            QMessageBox.warning(self, "Input Error", "Target File Name (for prompt context) is required.")
            self._reset_generate_button_and_status("Input error: Target File Name required."); return
        if not prompt_text:
            QMessageBox.warning(self, "Input Error", "Prompt is required.")
            self._reset_generate_button_and_status("Input error: Prompt required."); return

        # --- Initialize API ---
        try:
            if provider == "Gemini":
                api_key = self.gemini_api_key_edit.text().strip() or None
                model_name = self.gemini_model_edit.text().strip() or DEFAULT_GEMINI_MODEL
                self.current_api_instance = GeminiRepoAPI(api_key=api_key, model_name=model_name)
            elif provider == "Ollama":
                model_name = self.ollama_model_edit.text().strip() or DEFAULT_OLLAMA_MODEL
                host = self.ollama_host_edit.text().strip() or None # API handles default if None
                self.current_api_instance = OllamaRepoAPI(model_name=model_name, host=host)
            else: # Should not happen due to ComboBox
                raise ValueError(f"Unsupported provider selected: {provider}")
            logger.info({"event": "ui_api_instance_created", "provider": provider, "model": self.current_api_instance.model_name, "host_if_ollama": getattr(self.current_api_instance, 'host', 'N/A')})
        except ValueError as e: # Catches API key missing from Gemini, model not found from Ollama (if checked), etc.
            logger.error({"event": "ui_api_init_failed", "provider": provider, "error": str(e)})
            QMessageBox.critical(self, "API Initialization Error", f"Failed to initialize {provider} API: {e}")
            self._reset_generate_button_and_status(f"API Init Error: {e}"); return
        except Exception as e: # Catch any other unexpected init errors
            logger.exception({"event": "ui_api_init_failed_unexpected", "provider": provider, "error": str(e)})
            QMessageBox.critical(self, "API Initialization Error", f"An unexpected error occurred initializing {provider} API: {e}")
            self._reset_generate_button_and_status(f"Unexpected API Init Error: {e}"); return

        # --- Start Generation Worker ---
        self.generation_worker = GenerationWorker(
            api_instance=self.current_api_instance,
            repo_name=repo_name,
            file_paths=context_files,
            target_file_name=target_file_name_for_prompt,
            prompt=prompt_text
        )
        self.generation_worker.started_signal.connect(self.on_generation_started)
        self.generation_worker.finished_signal.connect(self.on_generation_finished)
        self.generation_worker.error_signal.connect(self.on_generation_error)
        self.generation_worker.start() # This calls the worker's run() method in a new thread

    def _reset_generate_button_and_status(self, status_message: str):
        self.generate_button.setEnabled(True)
        self.update_status(status_message)

    def on_generation_started(self, message: str):
        self.update_status(message) # Show in status bar
        self.output_display_edit.append(f"{message}\n---") # Also log to output area

    def on_generation_finished(self, content: str):
        self.output_display_edit.append("\n--- Generation Complete ---\n")
        self.output_display_edit.append(content)
        logger.info({"event": "ui_generation_success", "output_length": len(content)})

        output_file_path = self.output_file_edit.text().strip()
        if output_file_path:
            try:
                output_dir = os.path.dirname(output_file_path)
                if output_dir: # Only create if path includes a directory
                    os.makedirs(output_dir, exist_ok=True)
                with open(output_file_path, "w", encoding='utf-8') as f:
                    f.write(content)
                final_status = f"Content generated and saved to {output_file_path}"
                QMessageBox.information(self, "Output Saved", f"Generated content successfully saved to:\n{output_file_path}")
                logger.info({"event": "ui_output_file_saved", "path": output_file_path})
            except Exception as e:
                logger.error({"event": "ui_output_file_save_error", "path": output_file_path, "error": str(e)})
                QMessageBox.warning(self, "File Save Error", f"Failed to save output to {output_file_path}:\n{e}")
                final_status = f"Generated content (display only). Error saving to file: {e}"
        else:
             final_status = "Generation successful! Content displayed."
        
        self._reset_generate_button_and_status(final_status)

    def on_generation_error(self, error_message: str):
        self.output_display_edit.append(f"\n--- GENERATION ERROR ---\n{error_message}")
        QMessageBox.critical(self, "Generation Error", error_message)
        # Error already logged by worker thread or API class
        self._reset_generate_button_and_status(f"Error: {error_message}")

    def update_status(self, message: str):
        ####FIXME self.statusBar.showMessage(message, 5000) # Show for 5 seconds, or 0 for permanent until next message
        # logger.debug({"event": "ui_status_update", "message": message}) # Can be too noisy for status bar
        pass

    def closeEvent(self, event):
        # Clean up worker thread if it's running when the window is closed
        if self.generation_worker and self.generation_worker.isRunning():
            reply = QMessageBox.question(self, 'Confirm Exit',
                                         "Generation is in progress. Do you want to stop it and exit?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                logger.info({"event": "ui_close_while_worker_running", "action": "terminate_worker"})
                self.generation_worker.terminate() # Force terminate (use with caution)
                self.generation_worker.wait()      # Wait for thread to finish terminating
                event.accept()
            else:
                event.ignore()
                return # Don't proceed with closing
        logger.info({"event": "ui_close"})
        super().closeEvent(event)


def main_gui():
    # Ensure sys.argv exists for QApplication, important for Qt command-line args like -style
    app_argv = sys.argv if hasattr(sys, 'argv') else [] 
    app = QApplication(app_argv)
    
    # Optional: Apply a style for a more modern look across platforms
    # Styles available depend on OS and Qt installation: "Windows", "Fusion", "Macintosh"
    # if "Fusion" in QStyleFactory.keys():
    #    app.setStyle("Fusion")

    window = GeminiRepoUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # This allows the UI to be run directly as a script: python -m gemini_repo.ui
    main_gui()