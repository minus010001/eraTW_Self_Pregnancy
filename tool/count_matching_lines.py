import os
import re
import sys

def count_matching_lines(folder_path, pattern):
    """
    统计文件夹中所有文件匹配正则表达式的行数
    """
    regex = re.compile(pattern)
    total_count = 0
    file_count = 0
    
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # 可以根据需要过滤文件类型
            if filename.endswith('.ERB') or filename.endswith('.ERH'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='shift_jis', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.match(line):
                                total_count += 1
                    file_count += 1
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return total_count, file_count

def main():
    if len(sys.argv) != 2:
        print("Usage: python count_matching_lines.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        sys.exit(1)
    
    # 用户提供的正则表达式
    pattern = r'^(?![ \t]*;.*$)[ \t]*(PRINT(FORM)?D?[LW]?\s+\S+.*|DATAFORM\s+\S+.*|(TRY)?CALL (ASK_M.*|PRINT_DIALOGUE.*|(K2_)?HPH_PRINT.*|SPTALK.*|CHARA_TEXT.*|PRINT_STR.*|COLORMESSAGE.*|K17_人形台词.*|(K17_)?CHOICE.*))'
    
    total, files_scanned = count_matching_lines(folder_path, pattern)
    
    print(f"扫描文件数: {files_scanned}")
    print(f"匹配行数: {total}")

if __name__ == "__main__":
    main()
