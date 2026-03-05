import os
import sys

# Force UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
project_root = r"d:\ai work\txt_splitter"
sys.path.insert(0, project_root)

from core.parser import TextParser
from core.patterns import get_language

def split_user_files():
    parser = TextParser()
    base_folder = r"d:\ai work\1"
    files = [
        {
            "name": "中华人民共和国民法典.txt",
            "pattern": get_language('zh').preset_patterns["Common All (卷/编/篇/章/回/节)"],
            "output_subdir": "民法典_按章拆分"
        },
        {
            "name": "资本论(套装共3册).txt",
            "pattern": get_language('zh').preset_patterns["Level 3: Chapter (章/回/节)"], # More granular for Das Kapital
            "output_subdir": "资本论_按章拆分"
        }
    ]
    
    for item in files:
        file_path = os.path.join(base_folder, item["name"])
        out_path = os.path.join(base_folder, item["output_subdir"])
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"\nProcessing: {item['name']}")

        with parser.prepared_document(file_path) as prepared:
            work_path = prepared.working_text_path

            # 1. Detect Encoding
            enc = prepared.encoding
            print(f"  Encoding: {enc}")

            # 2. Parse (prefer native chapters when available)
            if prepared.has_native_structure and prepared.native_chapters:
                chapters = prepared.native_chapters
                final_enc = enc
            else:
                chapters, final_enc = parser.parse_chapters(work_path, [item["pattern"]], enc)
            print(f"  Found {len(chapters)} segments.")

            # 3. Split
            def progress(curr, tot):
                if curr % 20 == 0 or curr == tot:
                    print(f"  Progress: {curr}/{tot}")

            parser.split_file(work_path, chapters, out_path, final_enc, progress_callback=progress)
            print(f"  Successfully split into: {out_path}")

if __name__ == "__main__":
    split_user_files()
