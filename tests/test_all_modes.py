import os
import sys

# Define path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.parser import TextParser
from core.patterns import get_language

def test_all_modes():
    parser = TextParser()
    test_file = os.path.join(project_root, 'tests', 'dummy_novel.txt')
    out_dir = os.path.join(project_root, 'tests', 'output_test')
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return

    print(f"\n{'='*30}")
    print(f"Starting Automated Tests: {test_file}")
    
    # 1. Encoding
    enc = parser.detect_encoding(test_file)
    print(f"Detected Encoding: {enc}")

    state = {"tests_run": 0, "passed": 0}

    def assert_chunk_count(action, out_sub, expected_min, expected_max=None):
        state["tests_run"] += 1
        out_path = os.path.join(out_dir, out_sub)
        files = [f for f in os.listdir(out_path) if os.path.isfile(os.path.join(out_path, f))] if os.path.exists(out_path) else []
        count = len(files)
        
        ok = False
        if expected_max is None:
            ok = count == expected_min
            msg = f"Expected {expected_min}, got {count}"
        else:
            ok = expected_min <= count <= expected_max
            msg = f"Expected {expected_min}-{expected_max}, got {count}"

        if ok:
            print(f"  [PASS] {action}: {msg}")
            state["passed"] += 1
        else:
            print(f"  [FAIL] {action}: {msg}")

    # ==========================
    # Test 1: By Size (KB)
    # ==========================
    try:
        sub_dir = "test_size"
        full_out = os.path.join(out_dir, sub_dir)
        parser.split_file(test_file, [], full_out, enc, 
                        output_mode="By File Size (KB)", constraint_limit=1)
        # Dummy file is very small (<1KB), should be 1 chunk
        assert_chunk_count("Split By Size (1KB)", sub_dir, 1)
    except Exception as e:
        print(f"  [FAIL] Split By Size (1KB) - Exception: {e}")

    # ==========================
    # Test 2: By Word Count
    # ==========================
    try:
        sub_dir = "test_words"
        full_out = os.path.join(out_dir, sub_dir)
        # Limit to 50 words (chars), should be split into multiple
        parser.split_file(test_file, [], full_out, enc, 
                        output_mode="By Word Count", constraint_limit=50, chunk_break="Paragraph")
        # Dummy file has ~250 chars. 250/50 = ~5 chunks
        assert_chunk_count("Split By Words (50)", sub_dir, 4, 10)
    except Exception as e:
        print(f"  [FAIL] Split By Words (50) - Exception: {e}")

    # ==========================
    # Test 3: By Line Count
    # ==========================
    try:
        sub_dir = "test_lines"
        full_out = os.path.join(out_dir, sub_dir)
        # Dummy file has 19 lines. Limit 5 -> ~4 chunks
        parser.split_file(test_file, [], full_out, enc, 
                        output_mode="By Line Count", constraint_limit=5)
        assert_chunk_count("Split By Lines (5)", sub_dir, 3, 7)
    except Exception as e:
        print(f"  [FAIL] Split By Lines (5) - Exception: {e}")

    # ==========================
    # Test 4: By Paragraph Count
    # ==========================
    try:
        sub_dir = "test_paragraphs"
        full_out = os.path.join(out_dir, sub_dir)
        # Dummy file has multiple paragraphs (double newlines). Let's say limit 2.
        parser.split_file(test_file, [], full_out, enc, 
                        output_mode="By Paragraph Count", constraint_limit=2)
        # dummy_novel has ~14 non-empty lines. re.split('\\n+') treats each as a paragraph.
        # With limit=2, we get ceil(14/2) = 7 chunks
        assert_chunk_count("Split By Paragraphs (2)", sub_dir, 4, 12)
    except Exception as e:
        print(f"  [FAIL] Split By Paragraphs (2) - Exception: {e}")

    # ==========================
    # Test 5: Regex Chapter Flat
    # ==========================
    try:
        sub_dir = "test_chapters"
        full_out = os.path.join(out_dir, sub_dir)
        pattern = get_language('zh').preset_patterns["Common All (卷/编/篇/章/回/节)"]
        chapters, final_enc = parser.parse_chapters(test_file, [pattern], enc)
        
        print(f"  [DEBUG] Parsed chapters: {[c['title'] for c in chapters]}")
        
        parser.split_file(test_file, chapters, full_out, final_enc, output_mode="Flat Folder", skip_toc=True, include_body=True)
        # From dummy novel we expect 5 chapters + 1 Prologue chunk = 6 files.
        assert_chunk_count("Split By Chapters (Flat)", sub_dir, 6)
    except Exception as e:
        print(f"  [FAIL] Split By Chapters - Exception: {e}")

    # ==========================
    # Test 6: Batch Processing
    # ==========================
    try:
        # Simulate GUI logic for batch folder
        sub_dir = "test_batch"
        base_out = os.path.join(out_dir, sub_dir)
        import datetime
        batch_folder_name = f"批量输出_Batch_{datetime.datetime.now().strftime('%H%M%S')}"
        full_out_base = os.path.join(base_out, batch_folder_name)
        
        # Test 2 files mimicking batch
        file_idx = 0
        file_out_dir = os.path.join(full_out_base, os.path.splitext(os.path.basename(test_file))[0])
        
        parser.split_file(test_file, [], file_out_dir, enc, output_mode="By Line Count", constraint_limit=10)
        
        # We expect a nested structure now: out_dir/test_batch/Batch_Split_Output_time/dummy_novel/ chunks
        assert_chunk_count("Split Batch (File 1)", os.path.join(sub_dir, batch_folder_name, "dummy_novel"), 1, 3)
    except Exception as e:
        print(f"  [FAIL] Split Batch - Exception: {e}")

    print(f"\n{'='*30}")
    print(f"TEST RESULTS: {state['passed']}/{state['tests_run']} Passed")
    
    if state['passed'] != state['tests_run']:
        sys.exit(1)

if __name__ == "__main__":
    test_all_modes()
