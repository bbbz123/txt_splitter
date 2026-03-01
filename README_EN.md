# TXT Splitter (Intelligent Text Splitter)

[中文版](./README.md) | [English Version](./README_EN.md)

TXT Splitter is a powerful and intelligent local text/novel/document splitting tool. The system can intelligently analyze the directory structure embedded within long texts (such as novels, legal documents, etc.), accurately extract true nested levels (from "Volume/Part" to "Chapter/Section", etc.), and completely solve the level confusion problem of various complex single-word and multi-word structures.

![GUI Screenshot](./docs/images/screenshot_gui.png)

In addition to "Chapter-based" splitting based on intelligent directory analysis, it also supports various physical splitting methods based on fixed dimensions and provides an elegant and beautiful Dark/Light interactive graphical user interface (GUI).

## ✨ Core Features

- **🧠 Dynamic Hierarchy Analysis**:
  Unlike traditional hard-coded rule matching, the system prioritizes extracting and learning from the file's actual directory (Table of Contents), automatically calculating true tree-like inclusion relationships through prefix numbers and other arrangements. Even when encountering document structures where "Part" and "Sub-part" are at the same level or confused, it can infer the most perfect inclusion system.
- **✅ Multi-dimensional Splitting Modes**:
  - **Size**: Split evenly by file bytes/volume (KB/MB).
  - **Words**: Limit the maximum number of words per split file (avoiding cutting off paragraphs).
  - **Lines**: Specify the maximum number of text lines per split.
  - **Paragraphs**: Split the file according to the number of natural paragraphs.
  - **Chapters**: The most powerful mode; supports "Flat" output of all chapters or a "Nested" directory structure reconstructed identically to the directory tree.
- **📂 Drag & Drop & Batch Processing**:
  Supports dragging long texts (or selecting multiple files at once) directly into the wait queue. Full background multi-threaded concurrent splitting ensures no UI lag.
- **🎨 Modern GUI**:
  Built on CustomTkinter, supports Dark mode/Light mode switching, and smoothly adapts to modern operating system desktop interaction habits.
- **🔒 Privacy & Offline**:
  Purely local computation, no internet connection required, ensuring absolute security and offline processing of private documents.

## 📦 How to Run and Install

The system is written in Python 3.12+ and is fully packaged. This means you can run it in any of the following ways:

### Method 1: Run the Executable (Recommended)

No Python environment installation required!

1. Enter the `dist/` directory.
2. Download and double-click `TXT_Splitter_Slim_Single.exe` (Portable Version) or find the executable in the folder distribution.

### Method 2: Run from Source

If you wish to perform secondary development and modification:

1. Ensure you have a Python environment installed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application entry point:

   ```bash
   python main.py
   ```

## 📖 User Guide

1. **Drag into Files**: Drag the `.txt` files (or a batch of files) you want to split into the "Listbox" of the software's main window. If you don't like dragging, you can also click the plus sign `+` to manually browse and import.
2. **Set Mode**: Select your splitting mode below (Words, Lines, or Chapters).
    - 💡 **Tip**: If splitting by chapters, it is recommended to click the `Analyze` button in the lower left corner of the panel area first, allowing the system to calculate the most suitable structure for the book (e.g., `Part, Chapter, Section`).
    - 💡 **Skip TOC**: When the book contains a very long general table of contents, enabling the "Skip Table of Contents" option can avoid treating the table of contents as an independent, long, fragmented chapter.
    - 💡 **Hierarchy Spacing**: When analysis shows multiple layers (e.g., Volume -> Part -> Chapter), you can select "Nested: XXX" to have the system automatically create a folder tree identical to the original book.
3. **Select Output Location**: You can select your preferred empty directory (otherwise, the software will create a clean batch folder named `📁_Batch_XXX` next to the source file).
4. **One-Click Splitting**: Press the prominent `Start Splitting` button at the bottom; the progress bar and background will automatically complete the rest.
5. **Open Preview**: A prompt will automatically appear after splitting is complete. Click `Open` on the main interface to instantly pop up the corresponding target output.

## 🛠️ Tree Architecture & Development

The project structure is very streamlined with clear functional boundaries:

```text
txt_splitter/
├── main.py                    # Entry point, launch point
├── core/
│   ├── __init__.py
│   ├── parser.py              # Core Engine: Regex splitting, dynamic TOC analysis, etc.
│   └── patterns.py            # Language Patterns: Specific regexes for ZH/EN
├── gui/
│   ├── __init__.py
│   └── app.py                 # UI View Layer: Multi-threading packaging, UI redrawing, etc.
├── tests/                     # Integration tests
└── dist/                      # Packaged executables
```

## 📄 License and Thanks

This tool is for personal intelligent text organization assistance. Acknowledgments to dependency libraries:

- `customtkinter` for driving beautiful modern graphical components.
- `tkinterdnd2` for unlocking elegant native Windows direct drag-and-drop capabilities.
