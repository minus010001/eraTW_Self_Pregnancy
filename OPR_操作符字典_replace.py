import os
import csv
import re
import sys

def detect_and_read(filepath):
    with open(filepath, 'rb') as f:
        raw_head = f.read(4)
    if raw_head.startswith(b'\xef\xbb\xbf'):
        enc = 'utf-8-sig'
    else:
        enc = None
    if enc:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError:
            pass
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(), 'utf-8'
    except UnicodeDecodeError:
        pass
    try:
        with open(filepath, 'r', encoding='cp932') as f:
            return f.read(), 'cp932'
    except UnicodeDecodeError:
        pass
    return None, None

def load_dictionary(csv_path):
    replacements = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                const_name = row[0].strip()
                original_str = row[1].strip()
                if const_name and original_str:
                    replacements.append((const_name, original_str))
    replacements.sort(key=lambda x: len(x[1]), reverse=True)
    return replacements

def apply_replacements(content, replacements):
    for const_name, original_str in replacements:
        pattern = '"' + re.escape(original_str) + '"'
        content = re.sub(pattern, const_name, content)
    return content

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = sorted([f for f in os.listdir(script_dir) if f.lower().endswith('.csv')])
    if not csv_files:
        print("CSV dictionary not found in script directory")
        return 1
    csv_path = os.path.join(script_dir, csv_files[0])
    print(f"Dictionary: {csv_files[0]}")
    replacements = load_dictionary(csv_path)
    print(f"Rules: {len(replacements)}")
    erb_files = []
    for root, dirs, files in os.walk(script_dir):
        for f in files:
            if f.lower().endswith('.erb'):
                erb_files.append(os.path.join(root, f))
    print(f"ERB files: {len(erb_files)}")
    modified_count = 0
    total_hits = 0
    for filepath in erb_files:
        content, encoding = detect_and_read(filepath)
        if content is None:
            print(f"  SKIP (encoding): {os.path.relpath(filepath, script_dir)}")
            continue
        hits = 0
        for const_name, original_str in replacements:
            hits += len(re.findall('"' + re.escape(original_str) + '"', content))
        if hits == 0:
            continue
        new_content = apply_replacements(content, replacements)
        with open(filepath, 'w', encoding=encoding, newline='') as f:
            f.write(new_content)
        rel = os.path.relpath(filepath, script_dir)
        print(f"  {hits} hits | {encoding} | {rel}")
        modified_count += 1
        total_hits += hits
    print(f"\nDone. {modified_count} files, {total_hits} replacements.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
