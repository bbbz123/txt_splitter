import sys
import os
sys.path.insert(0, r'D:\ai work\txt_splitter')
from core.parser import TextParser
from core.patterns import build_regexes_from_tokens, get_language

def test_file(file_path, log_file):
    def log(msg):
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            
    log(f"\n{'='*50}")
    log(f"File: {os.path.basename(file_path)}")
    parser = TextParser()
    enc = parser.detect_encoding(file_path)
    log(f"Encoding: {enc}")

    lang_ids = parser.detect_multilang_from_toc(file_path, enc)
    if not lang_ids:
        log("TOC Detection: Failed, falling back...")
        lang_ids = ['zh', 'en']
    else:
        log(f"TOC Detection: Success! {lang_ids}")

    for lang in lang_ids:
        lang_name = get_language(lang).display_name
        regexes = build_regexes_from_tokens(['章', 'Chapter', 'Part', '1', 'I'], lang)
            
        chapters, _ = parser.parse_chapters(file_path, regexes, enc)
        log(f"\n--- {lang_name} ({len(chapters)} chapters) ---")
        for i, c in enumerate(chapters[:10]):
            log(f"  {i+1:02d}. {c['title']}")
        if len(chapters) > 10:
            log("  ...")

if __name__ == '__main__':
    test_dir = r"D:\ai work\1"
    log_file = r"D:\ai work\txt_splitter\tests\test_out.log"
    # clear log
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Multi-Language Test Run\n")
        
    if os.path.exists(test_dir):
        for f in os.listdir(test_dir):
            if f.endswith('.txt'):
                test_file(os.path.join(test_dir, f), log_file)
    else:
        print(f"Directory {test_dir} not found.")
