from __future__ import annotations

import tkinter as tk
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from tkinter import filedialog, messagebox, ttk

from ..pipeline import run_pipeline
from ..settings import PipelineSettings, load_settings, save_settings


def main() -> None:
    app = TextExtractionApp()
    app.mainloop()


class TextExtractionApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Text Extraction")
        self.geometry("900x760")
        self.configure(bg="#f5f7fb")

        self.selected_file: Path | None = None
        self.workspace_dir = Path.cwd()
        self.settings = load_settings(self.workspace_dir)
        self._events: Queue[tuple[str, str]] = Queue()

        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg="#f5f7fb")
        header.pack(fill=tk.X, padx=24, pady=(24, 12))

        title = tk.Label(
            header,
            text="Text Extraction Pipeline",
            font=("Segoe UI", 20, "bold"),
            bg="#f5f7fb",
            fg="#1f2937",
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Hybrid Java + Python pipeline with translation support",
            font=("Segoe UI", 11),
            bg="#f5f7fb",
            fg="#6b7280",
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self, bg="#f5f7fb")
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        file_card = tk.LabelFrame(
            content,
            text="Input",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#111827",
            padx=12,
            pady=12,
        )
        file_card.pack(fill=tk.X, pady=(0, 16))

        self.file_label = tk.Label(
            file_card,
            text="No file selected",
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#374151",
        )
        self.file_label.pack(anchor="w")

        select_button = tk.Button(
            file_card,
            text="Choose File",
            command=self._choose_file,
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
        )
        select_button.pack(anchor="w", pady=(8, 0))

        actions = tk.Frame(content, bg="#f5f7fb")
        actions.pack(fill=tk.X, pady=(0, 16))

        self.run_button = tk.Button(
            actions,
            text="Run Extraction",
            command=self._run_pipeline,
            font=("Segoe UI", 11, "bold"),
            bg="#10b981",
            fg="white",
            relief=tk.FLAT,
            padx=16,
            pady=8,
        )
        self.run_button.pack(side=tk.LEFT)

        settings_button = tk.Button(
            actions,
            text="Settings",
            command=self._open_settings,
            font=("Segoe UI", 11, "bold"),
            bg="#4b5563",
            fg="white",
            relief=tk.FLAT,
            padx=16,
            pady=8,
        )
        settings_button.pack(side=tk.LEFT, padx=8)

        self.progress = ttk.Progressbar(actions, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)

        output_card = tk.LabelFrame(
            content,
            text="Output Triples",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#111827",
            padx=12,
            pady=12,
        )
        output_card.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(
            output_card,
            wrap="word",
            font=("Consolas", 11),
            bg="#f9fafb",
            fg="#111827",
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.configure(state=tk.DISABLED)

        logs_card = tk.LabelFrame(
            content,
            text="Progress Logs",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#111827",
            padx=12,
            pady=12,
        )
        logs_card.pack(fill=tk.BOTH, expand=False, pady=(12, 0))

        self.logs_text = tk.Text(
            logs_card,
            wrap="word",
            height=8,
            font=("Consolas", 10),
            bg="#0b1020",
            fg="#d1d5db",
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        self.logs_text.configure(state=tk.DISABLED)

    def _choose_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select text file",
            filetypes=[("Text files", "*.txt")],
        )
        if not file_path:
            return
        self.selected_file = Path(file_path)
        self.file_label.configure(text=str(self.selected_file))

    def _run_pipeline(self) -> None:
        if self.selected_file is None:
            messagebox.showwarning("Missing file", "Please select a text file first.")
            return

        self.progress.start(10)
        self.run_button.configure(state=tk.DISABLED)
        self._append_log("Starting pipeline")
        Thread(target=self._pipeline_worker, daemon=True).start()
        self.after(100, self._poll_worker_events)

    def _pipeline_worker(self) -> None:
        try:
            assert self.selected_file is not None
            config = run_pipeline(self.selected_file, self.workspace_dir, log_fn=self._thread_log)
            content = config.triples_file.read_text(encoding="utf-8")
            self._events.put(("finished", content))
        except Exception as exc:
            self._events.put(("failed", str(exc)))

    def _thread_log(self, message: str) -> None:
        self._events.put(("log", message))

    def _poll_worker_events(self) -> None:
        finished = False
        try:
            while True:
                event, payload = self._events.get_nowait()
                if event == "log":
                    self._append_log(payload)
                elif event == "finished":
                    self._pipeline_finished(payload)
                    finished = True
                elif event == "failed":
                    self._pipeline_failed(payload)
                    finished = True
        except Empty:
            pass
        if not finished:
            self.after(100, self._poll_worker_events)

    def _pipeline_finished(self, content: str) -> None:
        self._set_output(content)
        self._append_log("Extraction complete")
        self._finish_run()
        messagebox.showinfo("Success", "Extraction complete.")

    def _pipeline_failed(self, message: str) -> None:
        self._append_log(f"Error: {message}")
        self._finish_run()
        messagebox.showerror("Error", message)

    def _finish_run(self) -> None:
        self.progress.stop()
        self.run_button.configure(state=tk.NORMAL)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self, self.workspace_dir, self.settings)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
        self.settings = load_settings(self.workspace_dir)

    def _set_output(self, content: str) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, content)
        self.output_text.configure(state=tk.DISABLED)

    def _append_log(self, message: str) -> None:
        self.logs_text.configure(state=tk.NORMAL)
        self.logs_text.insert(tk.END, message + "\n")
        self.logs_text.see(tk.END)
        self.logs_text.configure(state=tk.DISABLED)


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, workspace_dir: Path, settings: PipelineSettings) -> None:
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x450")
        self.configure(bg="#f8fafc")
        self.workspace_dir = workspace_dir

        self.java_path_var = tk.StringVar(value=settings.java_path or "")
        self.java_cli_jar_var = tk.StringVar(value=settings.java_cli_jar or "")
        self.minie_jar_var = tk.StringVar(value=settings.minie_jar_path or "")
        self.minie_url_var = tk.StringVar(value=settings.minie_url or "")

        self._build_ui()

    def _build_ui(self) -> None:
        container = tk.Frame(self, bg="#f8fafc")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container, text="Java executable path", font=("Segoe UI", 10, "bold"), bg="#f8fafc"
        ).pack(anchor="w")
        java_entry = tk.Entry(container, textvariable=self.java_path_var, font=("Segoe UI", 10))
        java_entry.pack(fill=tk.X, pady=(6, 10))

        java_browse = tk.Button(
            container,
            text="Browse Java",
            command=self._browse_java,
            bg="#2563eb",
            fg="white",
            relief=tk.FLAT,
        )
        java_browse.pack(anchor="w", pady=(0, 16))

        tk.Label(
            container, text="Java CLI jar path", font=("Segoe UI", 10, "bold"), bg="#f8fafc"
        ).pack(anchor="w")
        java_jar_entry = tk.Entry(
            container, textvariable=self.java_cli_jar_var, font=("Segoe UI", 10)
        )
        java_jar_entry.pack(fill=tk.X, pady=(6, 10))

        java_jar_browse = tk.Button(
            container,
            text="Browse Java CLI jar",
            command=self._browse_java_jar,
            bg="#2563eb",
            fg="white",
            relief=tk.FLAT,
        )
        java_jar_browse.pack(anchor="w", pady=(0, 16))

        tk.Label(
            container, text="MinIE jar path", font=("Segoe UI", 10, "bold"), bg="#f8fafc"
        ).pack(anchor="w")
        minie_entry = tk.Entry(container, textvariable=self.minie_jar_var, font=("Segoe UI", 10))
        minie_entry.pack(fill=tk.X, pady=(6, 10))

        minie_browse = tk.Button(
            container,
            text="Browse MinIE jar",
            command=self._browse_minie,
            bg="#2563eb",
            fg="white",
            relief=tk.FLAT,
        )
        minie_browse.pack(anchor="w", pady=(0, 16))

        tk.Label(
            container, text="MinIE download URL", font=("Segoe UI", 10, "bold"), bg="#f8fafc"
        ).pack(anchor="w")
        minie_url_entry = tk.Entry(
            container, textvariable=self.minie_url_var, font=("Segoe UI", 10)
        )
        minie_url_entry.pack(fill=tk.X, pady=(6, 16))

        actions = tk.Frame(container, bg="#f8fafc")
        actions.pack(fill=tk.X, pady=(8, 0))

        save_button = tk.Button(
            actions,
            text="Save",
            command=self._save,
            bg="#10b981",
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
        )
        save_button.pack(side=tk.LEFT)

        cancel_button = tk.Button(
            actions,
            text="Close",
            command=self.destroy,
            bg="#6b7280",
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
        )
        cancel_button.pack(side=tk.LEFT, padx=8)

    def _browse_java(self) -> None:
        path = filedialog.askopenfilename(title="Select java.exe")
        if path:
            self.java_path_var.set(path)

    def _browse_minie(self) -> None:
        path = filedialog.askopenfilename(
            title="Select MinIE jar", filetypes=[("Jar files", "*.jar")]
        )
        if path:
            self.minie_jar_var.set(path)

    def _browse_java_jar(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Java CLI jar", filetypes=[("Jar files", "*.jar")]
        )
        if path:
            self.java_cli_jar_var.set(path)

    def _save(self) -> None:
        settings = PipelineSettings(
            java_path=self.java_path_var.get() or None,
            java_cli_jar=self.java_cli_jar_var.get() or None,
            minie_jar_path=self.minie_jar_var.get() or None,
            minie_url=self.minie_url_var.get() or None,
        )
        save_settings(self.workspace_dir, settings)
        messagebox.showinfo("Settings", "Settings saved.")
        self.destroy()


if __name__ == "__main__":
    main()
