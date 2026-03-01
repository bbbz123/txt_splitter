import os
import sys

# Define path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.parser import TextParser
from core.patterns import get_language

def test_files():
    parser = TextParser()
    folder = r"d:\ai work\1"
    files = ["中华人民共和国民法典.txt", "资本论(套装共3册).txt"]
    
    for filename in files:
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"\n{'='*20}")
        print(f"Testing File: {filename}")
        
        # 1. Encoding
        enc = parser.detect_encoding(file_path)
        print(f"Detected Encoding: {enc}")
        
        # 2. Test with Common Regex
        pattern = get_language('zh').preset_patterns["Common All (卷/编/篇/章/回/节)"]
        chapters, _ = parser.parse_chapters(file_path, [pattern], enc)
        
        print(f"Found {len(chapters)} levels (Volumes/Parts/Chapters)")
        if chapters:
            print("First 5 titles:")
            for c in chapters[:5]:
                print(f"  - {c['title']}")
                
        # 3. Specifically for Civil Code, test "Law Article"
        if "民法典" in filename:
            pattern_art = get_language('zh').preset_patterns["Law Article (第一条)"]
            articles, _ = parser.parse_chapters(file_path, [pattern_art], enc)
            print(f"Found {len(articles)} Articles (条)")

if __name__ == "__main__":
    test_files()
