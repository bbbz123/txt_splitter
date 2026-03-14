from __future__ import annotations

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gui.app import GUI


def test_gui_smoke_selects_files_and_resets(monkeypatch, sample_markdown_path):
    txt_path = os.path.join(project_root, "tests", "dummy_novel.txt")
    selected = (txt_path, str(sample_markdown_path))

    monkeypatch.setattr("gui.app.filedialog.askopenfilenames", lambda filetypes=None: selected)

    app = GUI()
    app.withdraw()
    try:
        assert app._is_supported_file(str(sample_markdown_path))
        assert not app._is_supported_file(str(sample_markdown_path.with_suffix(".rst")))

        app.select_file()
        app.update_idletasks()

        assert app.selected_files == list(selected)
        assert app.out_var.get().endswith("Batch_Split_Output")
        assert ".md:1" in app.file_count_var.get()

        app.on_mode_change("By Line Count")
        app.update_idletasks()
        assert app.split_btn.cget("state") == "normal"

        app.on_mode_change("Chapter Mode")
        app.update_idletasks()
        assert app.scan_btn.cget("state") == "normal"

        app.clear_files()
        app.update_idletasks()
        assert app.selected_files == []
        assert app.split_btn.cget("state") == "disabled"
    finally:
        app.destroy()
