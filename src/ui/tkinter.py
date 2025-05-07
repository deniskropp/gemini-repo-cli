import logging
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List

from gemini_repo import (
    GeminiRepoAPI,
    OllamaRepoAPI,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_OLLAMA_MODEL,
)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiRepoUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Repo Content Generator")

        # --- Variables ---
        self.repo_name = tk.StringVar()
        self.target_file = tk.StringVar()
        self.prompt = tk.StringVar()
        self.context_files = []
        self.output_file = tk.StringVar()
        self.provider = tk.StringVar(value="gemini")  # Default provider
        self.gemini_api_key = tk.StringVar()
        self.gemini_model = tk.StringVar(value=DEFAULT_GEMINI_MODEL)
        self.ollama_model = tk.StringVar(value=DEFAULT_OLLAMA_MODEL)
        self.ollama_host = tk.StringVar()

        # --- UI Elements ---
        self.create_widgets()

    def create_widgets(self):
        # --- Provider Selection ---
        provider_frame = ttk.LabelFrame(self.root, text="Provider")
        provider_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        gemini_radio = ttk.Radiobutton(provider_frame, text="Gemini", variable=self.provider, value="gemini")
        gemini_radio.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        ollama_radio = ttk.Radiobutton(provider_frame, text="Ollama", variable=self.provider, value="ollama")
        ollama_radio.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # --- Input Fields ---
        input_frame = ttk.LabelFrame(self.root, text="Input")
        input_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Repo Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(input_frame, textvariable=self.repo_name, width=50).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Target File:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(input_frame, textvariable=self.target_file, width=50).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Prompt:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(input_frame, textvariable=self.prompt, width=50).grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # --- Context Files ---
        context_frame = ttk.LabelFrame(self.root, text="Context Files")
        context_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.context_listbox = tk.Listbox(context_frame, width=60, height=5)
        self.context_listbox.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        add_context_button = ttk.Button(context_frame, text="Add File", command=self.add_context_file)
        add_context_button.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        remove_context_button = ttk.Button(context_frame, text="Remove File", command=self.remove_context_file)
        remove_context_button.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # --- Output ---
        output_frame = ttk.LabelFrame(self.root, text="Output")
        output_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_file, width=40).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        browse_output_button = ttk.Button(output_frame, text="Browse", command=self.browse_output_file)
        browse_output_button.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # --- Provider-Specific Settings ---
        settings_frame = ttk.LabelFrame(self.root, text="Provider Settings")
        settings_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Gemini Settings
        ttk.Label(settings_frame, text="Gemini API Key:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.gemini_api_key, width=40, show="*").grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="Gemini Model:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.gemini_model, width=40).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Ollama Settings
        ttk.Label(settings_frame, text="Ollama Model:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.ollama_model, width=40).grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="Ollama Host:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.ollama_host, width=40).grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # --- Generate Button ---
        generate_button = ttk.Button(self.root, text="Generate Content", command=self.generate_content)
        generate_button.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # --- Output Text Area ---
        self.output_text = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.output_text.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        self.output_text.config(state=tk.DISABLED)  # Make it read-only

        # --- Configure Grid Weights ---
        self.root.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        context_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(1, weight=1)

    def add_context_file(self):
        filepath = filedialog.askopenfilename(title="Select Context File")
        if filepath:
            self.context_files.append(filepath)
            self.context_listbox.insert(tk.END, filepath)

    def remove_context_file(self):
        try:
            index = self.context_listbox.curselection()[0]
            filepath = self.context_files.pop(index)
            self.context_listbox.delete(index)
        except IndexError:
            messagebox.showinfo("Info", "No file selected to remove.")

    def browse_output_file(self):
        filepath = filedialog.asksaveasfilename(title="Select Output File")
        if filepath:
            self.output_file.set(filepath)

    def generate_content(self):
        # --- Get Values from UI ---
        repo_name = self.repo_name.get()
        target_file = self.target_file.get()
        prompt = self.prompt.get()
        context_files = self.context_files
        output_file = self.output_file.get()
        provider = self.provider.get()
        gemini_api_key = self.gemini_api_key.get()
        gemini_model = self.gemini_model.get()
        ollama_model = self.ollama_model.get()
        ollama_host = self.ollama_host.get()

        # --- Input Validation ---
        if not repo_name or not target_file or not prompt:
            messagebox.showerror("Error", "Repo Name, Target File, and Prompt are required.")
            return

        # --- Logging ---
        logger.info(f"Generating content with provider: {provider}")
        logger.info(f"Repo Name: {repo_name}, Target File: {target_file}")
        logger.info(f"Context Files: {context_files}")

        # --- Clear Previous Output ---
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

        # --- Initialize API ---
        try:
            if provider == "gemini":
                api_instance = GeminiRepoAPI(api_key=gemini_api_key, model_name=gemini_model)
            elif provider == "ollama":
                api_instance = OllamaRepoAPI(model_name=ollama_model, host=ollama_host)
            else:
                messagebox.showerror("Error", f"Unsupported provider: {provider}")
                return
        except Exception as e:
            logger.exception("API Initialization Failed")
            messagebox.showerror("Error", f"API Initialization Failed: {e}")
            return

        # --- Generate Content ---
        try:
            start_time = time.time()
            generated_content = api_instance.generate_content(
                repo_name=repo_name,
                file_paths=context_files,
                target_file_name=target_file,
                prompt=prompt,
            )
            end_time = time.time()
            generation_time = end_time - start_time
            logger.info(f"Content generated in {generation_time:.2f} seconds")

            # --- Display Output ---
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, generated_content)
            self.output_text.config(state=tk.DISABLED)

            # --- Save to File (Optional) ---
            if output_file:
                try:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(generated_content)
                    messagebox.showinfo("Success", f"Content written to {output_file}")
                except Exception as e:
                    logger.exception("Failed to write output to file")
                    messagebox.showerror("Error", f"Failed to write output to file: {e}")

        except Exception as e:
            logger.exception("Content Generation Failed")
            messagebox.showerror("Error", f"Content Generation Failed: {e}")

def main():
    root = tk.Tk()
    ui = GeminiRepoUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
