#!/usr/bin/env python3
r"""
ERB FORM 表达式转义缺失检测器

检测在 FORM 上下文中，函数调用未被 %...% 包裹的错误。

错误模式：
    PRINTFORMW 「...PRINT_MALE_CN("男人", TARGET)...」  (缺少 %...%)
正确：
    PRINTFORMW 「...%PRINT_MALE_CN("男人", TARGET)%...」

FORM 语法规则（参考 erabasic/form-syntax.md）：
- %字符串表达式%   字符串变量替换（包括函数调用）
- {整数表达式}     整数插值
- \@ 条件 ? 真 # 假 \@  FORM 三元运算符
- 在 FORM 普通文本区域，标识符(参数) 会被当作普通文本原样输出，不会调用函数

用法：
    python check_form_escape.py <file_or_dir> [file_or_dir ...]
    python check_form_escape.py "ERB/口上・メッセージ関連/個人口上/060 Parsee [パルスィ]"
    python check_form_escape.py "ERB/口上・メッセージ関連/個人口上/060 Parsee [パルスィ]/Parsee/M_KOJO_K60_2_イベント.ERB"
"""

import io
import re
import sys
from pathlib import Path
from typing import List, Tuple

# 强制 stdout 使用 UTF-8（避免 GBK 编码错误）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# FORM 上下文命令：参数走 AnalyseFormattedString（FORM 解析）
# 注意：PRINTS/PRINTSL/PRINTSW/PRINTDATA* 不在 FORM 列表中——它们的参数是普通字符串拼接
FORM_COMMANDS = [
    'PRINTFORM', 'PRINTFORMW', 'PRINTFORMWL', 'PRINTFORMD', 'PRINTFORMDW',
    'PRINTFORMS', 'PRINTFORMSW', 'PRINTFORMSL',
    'RETURNFORM', 'RETURNFORMW',
    'DATAFORM', 'PUTFORM',
]

# CALLFORM 系列：第一个参数（函数名）是 FORM
CALLFORM_COMMANDS = ['CALLFORM', 'TRYCALLFORM', 'JUMPFORM']

# 排除的标识符（关键字/HTML标签等）
EXCLUDE_IDENTS = {
    'IF', 'ELSEIF', 'ELSE', 'ENDIF', 'SIF',
    'WHILE', 'WEND', 'ENDWHILE',
    'FOR', 'NEXT',
    'REPEAT',
    'SELECTCASE', 'CASE', 'CASEELSE', 'ENDSELECT',
    'TO', 'STEP', 'IS',
    'AND', 'OR', 'NOT',
    'PRINT', 'PRINTL', 'PRINTW', 'PRINTV',
    'PRINTD', 'PRINTDL', 'PRINTDW',
    'CALL', 'CALLF', 'TRYCALL', 'TRYCALLF', 'JUMP',
    'RETURN', 'RETURNF',
    'GOTO',
    'BREAK', 'CONTINUE',
    'font', 'b', 'i', 's', 'u', 'div', 'p', 'br', 'img',
    'button', 'a', 'span',
}

# 整数变量名（CFLAG/TFLAG 等 = 整数赋值，不走 FORM 语法）
INT_VAR_PATTERN = re.compile(
    r'^(CFLAG|TFLAG|TCVAR|FLAG|ABL|TALENT|MARK|EXP|LOCAL|ARG|ARGS|LOCALS|'
    r'GLOBAL|SAVEDATA|ITEM|STAIN|PALAM|JUEL|EQUIP|TEQUIP|SELECTCOM|BASE|MAXBASE|'
    r'SOURCE|NOWEX|CUM|RELATION|DOWNBASE|EX|CDFLAG|TIME|YEAR|MONEY|DAY|TARGET|'
    r'PLAYER|MASTER|ASSI|RESULT|RESULTS|COUNT|LINECOUNT|CHARANUM|CHARA_ACTIVE|'
    r'ITEMSALES|ITEMPRICE|ABLUP|NO|NAME|CALLNAME|NICKNAME|MASTERNAME|CSTR|CSVTBL|'
    r'CDSTR\d*|STRLENS|TOOLTIP|ENUM|DAYS|CURRENTREDRAW|GETTIMES|PRICE|GETMONEY|'
    r'A|T|U)(\b|:|$)',
    re.IGNORECASE
)


def is_form_context(line: str) -> Tuple[bool, str, str]:
    """
    判断该行是否为 FORM 上下文。

    返回 (是否FORM, 参数部分, 命令名)
    """
    stripped = line.lstrip()

    # 跳过注释行
    if stripped.startswith(';'):
        return False, '', ''
    # 跳过空行
    if not stripped:
        return False, '', ''
    # 跳过 # 预处理行
    if stripped.startswith('#'):
        return False, '', ''
    # 跳过 @ 标签行
    if stripped.startswith('@'):
        return False, '', ''

    upper = stripped.upper()

    # 检查 FORM 命令
    for cmd in FORM_COMMANDS:
        if upper.startswith(cmd):
            rest_idx = len(cmd)
            if rest_idx < len(stripped) and stripped[rest_idx] in ' \t':
                return True, stripped[rest_idx + 1:], cmd
            elif rest_idx == len(stripped):
                return False, '', ''

    # 检查 CALLFORM 系列（参数走 FORM，但作为函数名拼接，整行检查意义不大）
    # 返回特殊标记，让 find_unescaped_calls 跳过整行
    for cmd in CALLFORM_COMMANDS:
        if upper.startswith(cmd):
            rest_idx = len(cmd)
            if rest_idx < len(stripped) and stripped[rest_idx] in ' \t':
                return True, '__SKIP_CALLFORM__', cmd

    # 检查字符串赋值（= 走 FORM，'= 走表达式）
    # 注意：字符串变量赋值（VAR = value）走 FORM 语法，但脚本难以判断函数返回类型
    # 因此暂时不检测此模式，留给运行时验证
    # 如果需要检测，可以基于以下规则：
    # - 左侧是已知字符串变量
    # - value 是字符串拼接（含 %...% / @{三元}@）
    # - 不含纯函数调用
    # m = re.match(r'^(\s*)([A-Za-z_][A-Za-z0-9_:]*(?::\d+)*)\s*=\s*(.*)$', line)
    # 暂时跳过

    return False, '', ''


def find_unescaped_calls(form_text: str) -> List[Tuple[str, int, str]]:
    r"""
    在 FORM 文本中查找未被 %...% 包裹的函数调用。

    状态机跟踪：
    - in_percent:        在 %...% 内
    - in_curly:          在 {...} 内
    - in_yenat:          在 \@...\@ 内
    - in_atsign_string:  在 @"..." 内（嵌套 FORM 字符串）

    排除模式：
    - @...?...#...@（错误的"裸"三元语法）—— 不是 FORM 三元，函数调用也不合法
    - @"..."（嵌套字符串）—— 内部是 FORM 语法
    """
    issues = []
    i = 0
    n = len(form_text)

    in_percent = False
    in_curly = False
    in_yenat = False
    in_atsign_string = False

    while i < n:
        c = form_text[i]

        # 处理转义
        if c == '\\' and i + 1 < n:
            if form_text[i + 1] == '@' and not in_percent and not in_curly and not in_atsign_string:
                # \@ 三元运算符开始
                in_yenat = True
                i += 2
                continue
            if form_text[i + 1] == '@' and in_yenat:
                # \@ 三元运算符结束
                in_yenat = False
                i += 2
                continue
            # 其他转义
            i += 2
            continue

        # 在 \@...\@ 内
        if in_yenat:
            i += 1
            continue

        # 在 @"..." 内（嵌套 FORM 字符串）—— 函数调用合法
        # 内部是完整的 FORM 语法（包含 %...% / {表达式} / \@三元 / "字符串"）
        if in_atsign_string:
            if c == '\\' and i + 1 < n:
                # 转义
                i += 2
                continue
            if c == '"':
                # 检查是否是 @"..." 的闭合
                # 简单判断：下一个非空字符不是字母（因为 @" 开始是 @，闭合后是函数参数）
                k = i + 1
                while k < n and form_text[k] in ' \t':
                    k += 1
                if k >= n or form_text[k] in ',) \t':
                    # 闭合
                    in_atsign_string = False
                    i += 1
                    continue
                # 内部字符串字面量的引号（吞掉这个引号）
                i += 1
                continue
            i += 1
            continue

        # 在 {...} 内（整数插值，所有内容合法）
        if in_curly:
            if c == '}':
                in_curly = False
            # 内部所有内容（变量、函数调用、运算符）都合法
            i += 1
            continue

        # 普通文本状态
        if c == '%':
            # 跳过整个 %...% 块（因为内部是表达式语法，函数调用合法）
            # 简单策略：找到下一个 % 作为结束（不考虑转义 \% 和嵌套 @"..."）
            end = i + 1
            depth_paren = 0
            depth_bracket = 0
            in_str = False  # 字符串字面量
            in_ats = False  # @"..." 嵌套
            while end < n:
                ec = form_text[end]
                if in_str:
                    if ec == '\\' and end + 1 < n:
                        end += 2
                        continue
                    if ec == '"':
                        in_str = False
                    end += 1
                    continue
                if in_ats:
                    if ec == '\\' and end + 1 < n:
                        end += 2
                        continue
                    if ec == '"':
                        in_ats = False
                    end += 1
                    continue
                if ec == '\\' and end + 1 < n:
                    end += 2
                    continue
                if ec == '"':
                    in_str = True
                    end += 1
                    continue
                if ec == '@' and end + 1 < n and form_text[end + 1] == '"':
                    in_ats = True
                    end += 2
                    continue
                if ec == '(':
                    depth_paren += 1
                elif ec == ')':
                    depth_paren -= 1
                elif ec == '[':
                    depth_bracket += 1
                elif ec == ']':
                    depth_bracket -= 1
                elif ec == '%' and depth_paren == 0 and depth_bracket == 0:
                    # 找到 % 结束（不在括号/字符串内）
                    i = end + 1
                    break
                end += 1
            else:
                # 没找到 %，放弃
                i = end
            continue
        elif c == '{':
            in_curly = True
            i += 1
            continue

        # 排除 @ 表达式（错误的"裸"三元语法）—— 不是 FORM 三元
        # 模式 1: @...?...#...@（无空格）
        # 模式 2: @ 函数(参数) ?...#...@ 或 @ 条件 ?...#...@（有空格）
        if c == '@':
            k = i + 1
            if k < n and form_text[k] == '"':
                # @" 不应出现在普通文本，忽略
                i += 1
                continue

            # 查找下一个 @
            end = form_text.find('@', k)
            if end > k:
                # 检查 @...@ 之间是否包含 ? 和 #（典型三元结构）
                inner = form_text[k:end]
                if '?' in inner and '#' in inner:
                    i = end + 1
                    continue

        # 检测函数调用：标识符(  模式
        # 启发式：只报告包含字符串字面量参数的函数调用
        # 因为这是 FORM 中调用函数的最强信号
        # 普通文本中"(...)"是常见表达，不应误报
        if c.isalpha() or c == '_':
            start = i
            while i < n and (form_text[i].isalnum() or form_text[i] == '_'):
                i += 1
            ident = form_text[start:i]

            # 跳过空白
            j = i
            while j < n and form_text[j] in ' \t':
                j += 1

            if j < n and form_text[j] == '(':
                if ident not in EXCLUDE_IDENTS:
                    # 找到匹配的 )，检查参数中是否含字符串字面量 "..."
                    depth = 1
                    k = j + 1
                    has_string_literal = False
                    has_chinese_or_jp = False
                    in_call_str = False
                    while k < n and depth > 0:
                        kc = form_text[k]
                        if in_call_str:
                            if kc == '\\' and k + 1 < n:
                                k += 2
                                continue
                            if kc == '"':
                                in_call_str = False
                                has_string_literal = True
                            k += 1
                            continue
                        if kc == '"':
                            in_call_str = True
                            k += 1
                            continue
                        if kc == '(':
                            depth += 1
                        elif kc == ')':
                            depth -= 1
                            if depth == 0:
                                break
                        # 检查中文字符
                        if '\u4e00' <= kc <= '\u9fff' or '\u3040' <= kc <= '\u309f' or '\u30a0' <= kc <= '\u30ff':
                            has_chinese_or_jp = True
                        k += 1

                    # 只报告：包含字符串字面量的函数调用
                    # 或：标识符是 _CN/_JP/_EN 后缀（中文本地化函数）
                    if has_string_literal or ident.endswith(('_CN', '_JP', '_EN')):
                        ctx_start = max(0, start - 30)
                        ctx_end = min(n, k + 1)
                        context = form_text[ctx_start:ctx_end]
                        issues.append((ident, start, context))
                i = j + 1
                continue
            # 不是函数调用
            continue

        i += 1

    return issues


def scan_file(filepath: Path) -> List[Tuple[int, str, str, str, str]]:
    """
    扫描单个 ERB 文件。

    返回 [(行号, 函数名, 上下文, 行内容, 命令名), ...]
    """
    issues = []

    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return issues

    for line_num, line in enumerate(lines, 1):
        line = line.rstrip('\r\n')

        is_form, form_text, cmd_name = is_form_context(line)
        if not is_form:
            continue

        # 跳过 CALLFORM 整行
        if form_text == '__SKIP_CALLFORM__':
            continue

        calls = find_unescaped_calls(form_text)
        for func_name, pos, context in calls:
            issues.append((line_num, func_name, context, line, cmd_name))

    return issues


def scan_path(path: Path):
    """
    扫描文件或目录。
    """
    all_issues = []

    if path.is_file():
        if path.suffix.upper() == '.ERB':
            issues = scan_file(path)
            for line_num, func_name, context, line, cmd in issues:
                all_issues.append((path, line_num, func_name, context, line, cmd))
    elif path.is_dir():
        for filepath in sorted(path.rglob('*.ERB')):
            issues = scan_file(filepath)
            for line_num, func_name, context, line, cmd in issues:
                all_issues.append((filepath, line_num, func_name, context, line, cmd))
    else:
        print(f"Path not found: {path}", file=sys.stderr)

    return all_issues


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    all_issues = []

    for path_str in sys.argv[1:]:
        path = Path(path_str)
        all_issues.extend(scan_path(path))

    if not all_issues:
        print("No issues found.")
        return

    print(f"Found {len(all_issues)} potential issues:\n")

    for filepath, line_num, func_name, context, line, cmd in all_issues:
        print(f"{'=' * 80}")
        print(f"File: {filepath}")
        print(f"Line: {line_num}  Command: {cmd}  Function: {func_name}")
        print(f"Context: ...{context}...")
        print(f"Full:   {line.strip()}")
        print()

    print(f"{'=' * 80}")
    print(f"Summary: {len(all_issues)} issues in {len(set(i[0] for i in all_issues))} files")

    func_counts = {}
    for _, _, func_name, _, _, _ in all_issues:
        func_counts[func_name] = func_counts.get(func_name, 0) + 1

    print(f"\nBy function ({len(func_counts)} unique):")
    for func, count in sorted(func_counts.items(), key=lambda x: -x[1]):
        print(f"  {func:40s} {count:4d}")


if __name__ == '__main__':
    main()
