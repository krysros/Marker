import sys
import time
import os

sys.path.insert(0, os.path.abspath("."))

from marker.utils.langchain_ai import invoke_text

started = time.time()
try:
    res = invoke_text("Hello, say Hi in Polish", model="gemini-2.5-flash-lite")
    print(f"Success in {time.time() - started:.2f}s:", res)
except Exception as e:
    print(f"Failed in {time.time() - started:.2f}s:", e)
