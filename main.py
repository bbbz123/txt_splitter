# TXT Splitter Main Entry Point | Powered by bbbz123
import os
import sys
import io

# Force UTF-8 encoding for Windows terminal to avoid 'UnicodeEncodeError' or garbled text
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

# Add project root to python path so core and gui imports work properly regardless of CWD.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """
    Main entry point for the TXT Splitter application.
    Verifies dependencies and launches the GUI.
    """
    try:
        import customtkinter # type: ignore # noqa: F401 
        from tkinterdnd2 import TkinterDnD # type: ignore # noqa: F401
    except ImportError as e:
        print(f"Error: Missing dependencies. {e}")
        print("Please install requirements: pip install customtkinter tkinterdnd2 chardet")
        return

    from gui.app import GUI # type: ignore
    
    app = GUI()
    app.mainloop()

if __name__ == "__main__":
    main()
