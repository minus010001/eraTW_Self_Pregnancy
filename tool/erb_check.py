# -*- coding: utf-8 -*-
# 语法检查器 for ERA BASIC 脚本文件 (.ERB)
# 用法：python erb_check.py ./文件夹名 （可选：--fix）
# 用法：python erb_check.py ./CHECK --fix

import sys
import os
import re

class ErbLinter:
    def __init__(self, indent_char='\t'):
        self.indent_char = indent_char
        self.indent_level = 0
        self.formatted_lines = []
        self.errors = []
        self.warnings = []
        self.stack = []

        # --- 1. 定义缩进规则 ---
        # 1=开始(下行+1), 2=结束(本行-1), 3=中间(本行-1,下行不变)
        self.rules = {
            'IF': 1, 'SELECTCASE': 1, 'FOR': 1, 'WHILE': 1, 'DO': 1, 'REPEAT': 1,
            'DATALIST': 1, 'TRYCALLLIST': 1, 'NOSKIP': 1,
            
            # --- 修改点 1：将 CASE/CASEELSE 视为起始块 ---
            'CASE': 1, 'CASEELSE': 1,
            
            'ENDIF': 2, 'ENDSELECT': 2, 'NEXT': 2, 'WEND': 2, 'LOOP': 2, 'REND': 2,
            'ENDLIST': 2, 'ENDCATCH': 2, 'ENDNOSKIP': 2,
            
            # ELSE/ELSEIF 仍然是中间块
            'ELSE': 3, 'ELSEIF': 3, 'DATAFORM': 3,
            
            'SIF': 4, 

            '[IF_DEBUG]': 1, '[IF_NDEBUG]': 1, '[IF': 1, '[ENDIF]': 2
        }

        # --- 2. 定义配对规则 ---
        self.pairs = {
            'ENDIF': ['IF'], 
            'ENDSELECT': ['SELECTCASE'], 
            'NEXT': ['FOR'],
            'WEND': ['WHILE'], 
            'LOOP': ['DO'], 
            'REND': ['REPEAT'],
            'ENDLIST': ['DATALIST', 'TRYCALLLIST'],
            '[ENDIF]': ['[IF_DEBUG]', '[IF_NDEBUG]', '[IF']
        }

        # --- 3. 动态生成 PRINTDATA ---
        pd_bases = ['PRINTDATA', 'PRINTDATAK', 'PRINTDATAD']
        pd_suffixes = ['', 'L', 'W']
        self.rules['ENDDATA'] = 2
        self.pairs['ENDDATA'] = [] 
        for base in pd_bases:
            for suffix in pd_suffixes:
                variant = base + suffix
                self.rules[variant] = 1 
                self.pairs['ENDDATA'].append(variant)

    def parse_line(self, line):
        line = line.strip()
        if not line: return None, "", "", ""
        
        comment = ""
        code = line
        if line.startswith(';#;'): code, comment = line, ""
        else:
            if line.startswith('//'): code, comment = "", line
            elif ';' in line:
                parts = line.split(';', 1)
                code = parts[0].strip()
                comment = ';' + parts[1]
                if not code: code, comment = "", line
        if not code: return None, "", "", comment
        parts = code.split(None, 1)
        return parts[0].upper(), parts[1] if len(parts) > 1 else "", code, comment

    def analyze_select_case_start(self, args):
        match = re.search(r'RAND:(\d+)', args, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def check_syntax_and_logic(self, keyword, args, line_num):
        if not keyword: return
        if keyword in ['ELSE', 'CASEELSE'] and args: self.errors.append(f"Line {line_num}: Syntax Error - '{keyword}' should not have conditions.")
        if keyword in ['ELSEIF', 'CASE'] and not args: self.errors.append(f"Line {line_num}: Syntax Error - '{keyword}' requires a condition.")
        if self.stack:
            parent = self.stack[-1]
            parent_kw = parent['keyword']
            if keyword in ['CASE', 'CASEELSE'] and parent_kw not in ['SELECTCASE', 'CASE', 'CASEELSE']: self.errors.append(f"Line {line_num}: Syntax Error - '{keyword}' found outside of SELECTCASE.")
            if keyword in ['ELSE', 'ELSEIF'] and parent_kw != 'IF': self.errors.append(f"Line {line_num}: Syntax Error - '{keyword}' found outside of IF.")
            if keyword == 'CASE' and parent_kw == 'SELECTCASE' and parent.get('rand_max'):
                rand_max = parent['rand_max']
                case_args = args.replace(',', ' ').split()
                for arg in case_args:
                    if arg.isdigit() and int(arg) >= rand_max: self.warnings.append(f"Line {line_num}: Logic Warning - 'CASE {int(arg)}' unreachable for RAND:{rand_max}.")
                range_match = re.search(r'(\d+)\s*TO\s*(\d+)', args, re.IGNORECASE)
                if range_match and int(range_match.group(1)) >= rand_max: self.warnings.append(f"Line {line_num}: Logic Warning - Range '{range_match.group(0)}' unreachable for RAND:{rand_max}.")
        if keyword in ['IF', 'ELSEIF', 'SIF'] and re.search(r'\bRAND:1\b', args, re.IGNORECASE): self.warnings.append(f"Line {line_num}: Logic Warning - 'RAND:1' is always 0 (False).")

    def process_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
        except:
            with open(file_path, 'r', encoding='shift-jis') as f: lines = f.readlines()

        self.indent_level, self.formatted_lines, self.stack, self.errors, self.warnings = 0, [], [], [], []
        next_indent_bonus = 0

        for i, raw_line in enumerate(lines):
            line_num = i + 1
            keyword, args, code, comment = self.parse_line(raw_line)
            if keyword is None:
                curr = max(0, self.indent_level + next_indent_bonus)
                self.formatted_lines.append("" if not comment else (self.indent_char * curr) + comment)
                continue

            # --- 修改点 2: CASE/ENDSELECT 特殊处理 ---
            # 如果遇到 CASE，且当前在另一个 CASE 块里，先弹出一层
            if keyword in ['CASE', 'CASEELSE']:
                if self.stack and self.stack[-1]['keyword'] in ['CASE', 'CASEELSE']:
                    self.indent_level -= 1
                    self.stack.pop()
            
            # 如果遇到 ENDSELECT，且当前在 CASE 块里，也先弹出一层
            elif keyword == 'ENDSELECT':
                if self.stack and self.stack[-1]['keyword'] in ['CASE', 'CASEELSE']:
                    self.indent_level -= 1
                    self.stack.pop()
            # ------------------------------------

            rtype = self.rules.get(keyword, 0)
            self.check_syntax_and_logic(keyword, args, line_num)

            offset = 0
            if rtype == 2: # End
                self.indent_level -= 1
                if self.stack: self.stack.pop()
                else: self.errors.append(f"Line {line_num}: Extra closing tag '{keyword}'.")
            elif rtype == 3: # Middle
                offset = -1

            if keyword.startswith('@'):
                self.indent_level, self.stack, next_indent_bonus, offset = 0, [], 0, 0

            if self.indent_level < 0: self.indent_level = 0
            print_level = max(0, self.indent_level + offset + next_indent_bonus)

            final_line = f"{self.indent_char * print_level}{code}"
            if comment: final_line += f" {comment}"
            self.formatted_lines.append(final_line)

            next_indent_bonus = 1 if rtype == 4 else 0
            if rtype == 1:
                self.indent_level += 1
                ctx = {'keyword': keyword, 'line': line_num, 'rand_max': None}
                if keyword == 'SELECTCASE': ctx['rand_max'] = self.analyze_select_case_start(args)
                self.stack.append(ctx)

    def report(self):
        if self.errors:
            for e in self.errors: print(f"\033[91m[ERROR] {e}\033[0m")
        if self.warnings:
            for w in self.warnings: print(f"\033[93m[WARN ] {w}\033[0m")
        if self.stack:
            for item in self.stack: print(f"\033[91m[FATAL] Unclosed block '{item['keyword']}' from Line {item['line']}\033[0m")

    def save_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.formatted_lines))
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False

def process_target(target_path, is_batch=False, apply_fix=False):
    linter = ErbLinter()
    linter.process_file(target_path)
    has_issues = linter.errors or linter.warnings or linter.stack
    if has_issues:
        if is_batch: print(f"\n📂 Checking: {target_path}")
        linter.report()
    elif not is_batch:
        print("\033[92mAll checks passed. Syntax looks good!\033[0m")
    if apply_fix:
        linter.save_file(target_path)
        if not is_batch: print(f"💾 File updated: {target_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python erb_check.py <file_or_dir> [--fix]")
        sys.exit(1)
    input_path = sys.argv[1]
    apply_fix = '--fix' in sys.argv
    if apply_fix: print("⚠️  FIX MODE: Files will be re-indented.")
    if os.path.isfile(input_path): process_target(input_path, False, apply_fix)
    elif os.path.isdir(input_path):
        print(f"🚀 Batch processing: {input_path}")
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith('.erb'):
                    process_target(os.path.join(root, file), True, apply_fix)