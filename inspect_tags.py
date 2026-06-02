import sqlite3


def _unicode_lower(s: str | None) -> str | None:
    return s.lower() if s else s


conn = sqlite3.connect("marker.sqlite")
conn.create_function("unicode_lower", 1, _unicode_lower)
cur = conn.cursor()

res_lower = cur.execute("""
    SELECT name, COUNT(*) FROM tags
    GROUP BY lower(name)
    HAVING COUNT(*) > 1
""").fetchall()

res_unilower = cur.execute("""
    SELECT name, COUNT(*) FROM tags
    GROUP BY unicode_lower(name)
    HAVING COUNT(*) > 1
""").fetchall()

with open("dups_out.txt", "w", encoding="utf-8") as f:
    f.write("Duplicates with lower():\n")
    for r in res_lower:
        f.write(f"{r[0]} - {r[1]}\n")
    f.write("\nDuplicates with unicode_lower():\n")
    for r in res_unilower:
        f.write(f"{r[0]} - {r[1]}\n")

conn.close()
