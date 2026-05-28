import sys
import time
import os
import sqlite3
import json

# Ensure we can import marker packages
sys.path.insert(0, os.path.abspath("."))

# Set stdout/stderr to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from marker.utils.langchain_ai import invoke_text

def test_speed():
    conn = sqlite3.connect("marker.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM tags")
    all_tags = cursor.fetchall()
    tags = [row[1] for row in all_tags]
    conn.close()

    print(f"Loaded {len(tags)} tags from DB")
    
    query = "stolarka drewniana"
    
    # approach 2: semantic query expansion
    print("\nRunning semantic query expansion approach...")
    prompt = f"""You are a Polish semantic query expansion assistant.
Analyze the user's Polish search query: "{query}".
Generate a comprehensive JSON list of Polish words, stems, synonyms, materials, related products, or industries associated with this query.
Keep the list focused and include relevant search terms.
Examples:
Query: "stolarka drewniana" -> ["drewn", "stolark", "okna", "drzwi", "drewnian", "drzwiowe", "okien", "bram", "schody", "fasady"]
Query: "ogrzewanie" -> ["ogrzew", "ciepł", "kocioł", "piec", "grzej", "pompa", "instalac", "gaz", "pellet", "term"]

Return ONLY a JSON list of lowercased words/stems. Do not include markdown block formatting (like ```json), explanations, or extra text.
"""
    started = time.time()
    try:
        res = invoke_text(prompt, model="gemini-2.5-flash-lite")
        gemini_duration = time.time() - started
        print(f"Finished Gemini call in {gemini_duration:.2f}s")
        print("Raw response:", res)
        
        # Clean response
        import re
        clean_text = res.strip()
        clean_text = re.sub(r"^```(?:json)?\s*\n?", "", clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r"\n?```\s*$", "", clean_text)
        clean_text = clean_text.strip()
        
        keywords = json.loads(clean_text)
        print("Parsed keywords:", keywords)
        
        # Filter tags in Python
        local_start = time.time()
        matched_tags = []
        for tag_id, name in all_tags:
            name_lower = name.lower()
            if any(kw.lower() in name_lower for kw in keywords):
                matched_tags.append(name)
        local_duration = time.time() - local_start
        
        total_duration = gemini_duration + local_duration
        print(f"Finished local filtering in {local_duration*1000:.2f}ms")
        print(f"Total approach duration: {total_duration:.2f}s")
        print(f"Matched {len(matched_tags)} tags out of {len(tags)}")
        print("Sample matched tags:", matched_tags[:15])
        
    except Exception as e:
        print("Failed query expansion approach:", e)

if __name__ == "__main__":
    test_speed()
