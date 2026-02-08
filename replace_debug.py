import re

with open('session.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace print(f"[DEBUG] with debug_log(f"
content = re.sub(r'print\(f"\[DEBUG\]', r'debug_log(f"', content)
content = re.sub(r'print\(f\'\[DEBUG\]', r'debug_log(f\'', content)
content = re.sub(r'print\("\[DEBUG\]', r'debug_log("', content)

with open('session.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Replaced all print DEBUG statements with debug_log')
