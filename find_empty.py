import re
with open('marker/locale/pl/LC_MESSAGES/messages.po', encoding='utf-8') as f:
    content = f.read()
blocks = re.split(r'\n\n', content)
for block in blocks:
    if 'msgstr ""' in block and 'msgid ""' not in block:
        for line in block.strip().splitlines():
            if line.startswith('msgid') or line.startswith('msgstr'):
                print(line)
        print()
