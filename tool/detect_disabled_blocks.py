#!/usr/bin/env python3
"""
detect_disabled_blocks.py
=========================
检测 ERB 文件中被检查标志（LOCAL/LOCAL:1）错误封闭的文本块。

背景
----
eraTheWorld 口上模板使用 `LOCAL = 0` / `LOCAL:1 = 0` 作为"记入チェック"开关：
  - `= 0`：该块不显示（禁用）
  - `= 1`：该块显示（启用）

模板默认值是 `= 0`（占位符），口上作者填入内容后改为 `= 1`。
但上游合并/翻译过程中，部分**已有内容的块**被错误地保留为 `= 0`，
导致对话文本被"封闭"而无法在游戏中显示。

检测模式
--------
1. **TRUE_DISABLED**（真禁用）：`LOCAL = 0` 后跟 `IF LOCAL` 块，块内有实际文本
   → 候选修复（改为 `= 1`）
2. **TEMPLATE_PLACEHOLDER**（模板占位符）：`LOCAL = 0` 后跟 `IF LOCAL` 块，块内为空
   → 假阳性，不修改
3. **BOM_CORRUPTION**（BOM 腐蚀）：首行 BOM 替换了 `;` 注释标记
   → 首行注释丢失
4. **GUARD_UNWRAP_CANDIDATE**（守卫解包候选）：`IF LOCAL:1 && X` 且 `LOCAL:1 = 0`
   → 死代码，可解包守卫

用法
----
    python detect_disabled_blocks.py <directory> [options]

    python detect_disabled_blocks.py d:\\eratw-chs\\ERB --format text
    python detect_disabled_blocks.py d:\\eratw-chs\\ERB --format json --output report.json
    python tool/detect_disabled_blocks.py d:\\eratw-chs\\ERB --only-true-disabled
    python tool/detect_disabled_blocks.py ERB --fix

退出码
------
  0  扫描完成（无论是否发现）
  1  参数错误
  2  路径不存在
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# LOCAL 赋值行：LOCAL = 0 / LOCAL:1 = 0 / LOCAL = 1 等
# 允许前导空白（Tab/空格），允许 = 两侧空白，允许行尾注释
RE_LOCAL_ASSIGN = re.compile(
    r'^\s*LOCAL(?::(\d+))?\s*=\s*(\d+)\s*(?:;.*)?$',
    re.IGNORECASE
)

# 用于替换：只匹配 LOCAL 赋值部分（不含前导空白）
# 用此版本可以保留原始缩进
RE_LOCAL_ASSIGN_CORE = re.compile(
    r'LOCAL(?::(\d+))?\s*=\s*\d+',
    re.IGNORECASE
)

# IF LOCAL / IF LOCAL:1 && ... 守卫行
RE_IF_LOCAL = re.compile(
    r'^\s*IF\s+LOCAL(?::(\d+))?(?:\s*&&\s*(.+?))?\s*(?:;.*)?$',
    re.IGNORECASE
)

# ELSEIF LOCAL:1 && ... 守卫行（也可能是被错误守卫的）
RE_ELSEIF_LOCAL = re.compile(
    r'^\s*ELSEIF\s+LOCAL(?::(\d+))?(?:\s*&&\s*(.+?))?\s*(?:;.*)?$',
    re.IGNORECASE
)

# PRINT 系列命令（有实际文本输出的行）
# 匹配所有 PRINT 开头的命令：PRINT, PRINTL, PRINTW, PRINTS, PRINTV, PRINTFORM,
# PRINTFORML, PRINTFORMW, PRINTFORMDW, PRINTFORMDL, PRINTD, PRINTDL, PRINTDATA,
# PRINTBUTTON, PRINTPLAIN, PRINTPLAINFORM, PRINTSW, PRINTVL, PRINTSL 等
# 关键：捕获命令名后的所有内容，用于判断是否有实际文本
RE_PRINT_CMD = re.compile(
    r'^\s*(PRINT[A-Z]*)\b\s*(.*?)\s*(?:;.*)?$',
    re.IGNORECASE
)

# PRINTDATA / DATALIST / DATA 等数据块内的 DATA 行（含实际内容）
RE_DATA_LINE = re.compile(r'^\s*DATA(?:L|W|S|FORM|FORML|FORMW|FORMDL)?\b\s*(.*?)\s*(?:;.*)?$', re.IGNORECASE)

# CALL 语句（调用其他函数，可能有输出）
RE_CALL = re.compile(r'^\s*CALL\s+\S+', re.IGNORECASE)

# 注释行
RE_COMMENT = re.compile(r'^\s*;')

# 空行或纯空白行
RE_BLANK = re.compile(r'^\s*$')

# RETURN 语句
RE_RETURN = re.compile(r'^\s*RETURN\b', re.IGNORECASE)

# IF/ELSEIF/ELSE/ENDIF/SIF/SELECTCASE/CASE/ENDSELECT 控制流
RE_CONTROL_FLOW = re.compile(
    r'^\s*(IF|ELSEIF|ELSE|ENDIF|SIF|SELECTCASE|CASE|ENDSELECT|WHILE|WEND|DO|LOOP|FOR|NEXT|REPEAT|REND|CONTINUE|BREAK)\b',
    re.IGNORECASE
)

# 函数标签行 @FUNC_NAME
RE_FUNC_LABEL = re.compile(r'^\s*@')

# PRINT 命令名集合（用于判断是否是 PRINT 行）
PRINT_COMMANDS = {
    'PRINTFORMW', 'PRINTFORML', 'PRINTFORMDW', 'PRINTFORM', 'PRINTL',
    'PRINTD', 'PRINTDATA', 'PRINTS', 'PRINTSW', 'PRINTV', 'PRINTBUTTON',
    'PRINTPLAIN', 'PRINTPLAINFORM', 'PRINT', 'PRINTW', 'PRINTVL', 'PRINTSINGLE',
}


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """单个检测结果"""
    file_path: str          # 相对路径
    line_no: int            # LOCAL 赋值行号（1-based）
    guard_type: str         # "LOCAL" / "LOCAL:1"
    current_value: int      # 当前值（0=禁用, 1=启用）
    finding_type: str       # TRUE_DISABLED / TEMPLATE_PLACEHOLDER / BOM_CORRUPTION / GUARD_UNWRAP_CANDIDATE
    if_block_start: int     # IF LOCAL 块起始行号
    if_block_end: int       # ENDIF 行号
    has_content: bool       # 块内是否有实际内容
    content_preview: str    # 块内前几行预览
    function_name: str      # 所在函数名（@标签）
    suggestion: str         # 修复建议


@dataclass
class ScanResult:
    """扫描结果汇总"""
    total_files: int = 0
    total_local_zeros: int = 0
    true_disabled: int = 0
    template_placeholders: int = 0
    bom_corruptions: int = 0
    guard_unwrap_candidates: int = 0
    findings: List[Finding] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 文件读取（编码检测）
# ---------------------------------------------------------------------------

def read_erb_file(path: Path) -> Tuple[Optional[List[str]], Optional[bytes]]:
    """
    读取 ERB 文件，自动检测编码。

    尝试顺序：UTF-8-sig → UTF-8 → Shift-JIS → GBK

    Returns:
        (lines, raw_bytes) — lines 为按行分割的列表（保留行尾），
        raw_bytes 为原始字节（用于 BOM 检测）。
        读取失败返回 (None, None)。
    """
    try:
        raw = path.read_bytes()
    except (OSError, PermissionError):
        return None, None

    # 尝试多种编码
    for enc in ('utf-8-sig', 'utf-8', 'shift-jis', 'gbk', 'cp932'):
        try:
            text = raw.decode(enc)
            # 统一换行符：将 \r\n / \r → \n
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            lines = text.split('\n')
            return lines, raw
        except (UnicodeDecodeError, LookupError):
            continue

    return None, None


# ---------------------------------------------------------------------------
# BOM 腐蚀检测
# ---------------------------------------------------------------------------

def detect_bom_corruption(raw_bytes: bytes, lines: List[str]) -> Optional[Finding]:
    """
    检测 BOM 腐蚀：首行 BOM 替换了 `;` 注释标记。

    现象：文件以 UTF-8 BOM (EF BB BF) 开头，首行应是注释分隔线 `;---...`
    但 `;` 被删除，首行变成 `---...`（纯短横线，无注释标记）。

    正常文件：BOM + `;---...` 或 无BOM + `;---...` 或 BOM + `@FUNC...`
    腐蚀文件：BOM + `---...`（`;` 丢失，首行为纯短横线）

    注意：不腐蚀的情况（合法首行）：
    - BOM + `@FUNC_NAME` — 函数标签
    - BOM + `#DIM` — 预处理指令
    - BOM + `[SKIPSTART]` — 跳过块
    - BOM + 其他非注释行 — 合法代码

    Returns:
        Finding 或 None
    """
    if not raw_bytes or not lines:
        return None

    # 检查是否有 UTF-8 BOM
    has_utf8_bom = raw_bytes[:3] == b'\xef\xbb\xbf'
    if not has_utf8_bom:
        return None

    # 检查首行（跳过 BOM 字符）
    first_line = lines[0] if lines else ''
    if first_line.startswith('\ufeff'):
        first_line = first_line[1:]

    stripped = first_line.lstrip()

    # BOM 腐蚀的特定模式：首行以短横线开头（应是 ;--- 分隔线但 ; 丢失）
    # 这是 commit d653ddd 中观察到的唯一 BOM 腐蚀模式
    if stripped.startswith('-') and not stripped.startswith(';'):
        # 确认是分隔线模式（至少 3 个连续短横线）
        dash_count = len(stripped) - len(stripped.lstrip('-'))
        if dash_count >= 3:
            return Finding(
                file_path='',  # 由调用者填充
                line_no=1,
                guard_type='BOM',
                current_value=-1,
                finding_type='BOM_CORRUPTION',
                if_block_start=1,
                if_block_end=1,
                has_content=False,
                content_preview=first_line[:80],
                function_name='',
                suggestion='将首行 BOM 替换为 ;（恢复注释分隔线标记）'
            )

    return None


# ---------------------------------------------------------------------------
# LOCAL 赋值检测
# ---------------------------------------------------------------------------

def find_local_assignments(lines: List[str]) -> List[Tuple[int, str, Optional[int], int]]:
    """
    查找所有 LOCAL / LOCAL:N 赋值行。

    Returns:
        [(line_idx, guard_type, sub_index, value), ...]
        line_idx: 0-based 行索引
        guard_type: "LOCAL" / "LOCAL:1"
        sub_index: None (LOCAL) 或 int (LOCAL:N)
        value: 0 或 1
    """
    results = []
    for idx, line in enumerate(lines):
        m = RE_LOCAL_ASSIGN.match(line)
        if m:
            sub_idx_str = m.group(1)
            value_str = m.group(2)
            sub_idx = int(sub_idx_str) if sub_idx_str else None
            value = int(value_str)
            guard_type = f"LOCAL:{sub_idx}" if sub_idx is not None else "LOCAL"
            results.append((idx, guard_type, sub_idx, value))
    return results


def find_enclosing_function(lines: List[str], line_idx: int) -> str:
    """
    向上查找包含当前行的函数标签（@FUNC_NAME）。
    """
    for i in range(line_idx, -1, -1):
        if RE_FUNC_LABEL.match(lines[i]):
            return lines[i].strip()
    return ''


# ---------------------------------------------------------------------------
# IF 块提取
# ---------------------------------------------------------------------------

def find_if_block_for_local(
    lines: List[str],
    local_line_idx: int,
    sub_idx: Optional[int]
) -> Optional[Tuple[int, int]]:
    """
    查找 LOCAL 赋值之后的 IF LOCAL / IF LOCAL:N && ... 块。

    在 local_line_idx 之后搜索（跳过注释和空行），找到第一个匹配的 IF 行，
    然后追踪 IF/ENDIF 嵌套找到匹配的 ENDIF。

    Returns:
        (if_start_idx, endif_idx) 或 None
    """
    expected_local = f"LOCAL:{sub_idx}" if sub_idx is not None else "LOCAL"

    # 向下搜索 IF LOCAL 行（跳过注释、空行、其他 LOCAL 赋值）
    if_start_idx = None
    for i in range(local_line_idx + 1, min(local_line_idx + 20, len(lines))):
        line = lines[i]
        # 跳过注释和空行
        if RE_COMMENT.match(line) or RE_BLANK.match(line):
            continue
        # 跳过 ;--- 分隔线
        if line.strip().startswith(';'):
            continue

        # 检查是否是 IF LOCAL 行
        m = RE_IF_LOCAL.match(line)
        if m:
            if_sub_idx_str = m.group(1)
            if_sub_idx = int(if_sub_idx_str) if if_sub_idx_str else None
            # 检查 sub_idx 是否匹配
            if if_sub_idx == sub_idx:
                if_start_idx = i
                break
        # 如果遇到其他非 IF 语句，停止搜索
        elif not RE_LOCAL_ASSIGN.match(line):
            # 遇到非注释、非空、非 LOCAL 赋值的语句
            # 可能是 IF LOCAL 块的守卫被删除了，或者结构不同
            break

    if if_start_idx is None:
        return None

    # 追踪 IF/ENDIF 嵌套，找到匹配的 ENDIF
    depth = 0
    for i in range(if_start_idx, len(lines)):
        line = lines[i]
        stripped = line.strip()

        # 跳过注释行（不参与嵌套计数）
        if RE_COMMENT.match(line):
            continue

        # SIF 是单行 IF，不增加嵌套深度
        if re.match(r'^\s*SIF\b', line, re.IGNORECASE):
            continue

        # 统计 IF / ELSEIF / ELSE / ENDIF
        # 注意：ELSEIF 不改变深度
        if re.match(r'^\s*IF\b', line, re.IGNORECASE):
            depth += 1
        elif re.match(r'^\s*ENDIF\b', line, re.IGNORECASE):
            depth -= 1
            if depth == 0:
                return (if_start_idx, i)

    # ENDIF 未找到（语法错误）
    return (if_start_idx, len(lines) - 1)


# ---------------------------------------------------------------------------
# 内容检测
# ---------------------------------------------------------------------------

def line_has_print_content(line: str) -> bool:
    """
    检查一行是否有实际 PRINT 输出内容（保守策略，减少假阳性）。

    判定规则：
    - PRINT 命令 + 非空文本 → True（有实际对话文本）
    - PRINT 命令 + 空白     → False（模板占位符，如 `PRINTFORMW `）
    - CALL 语句             → True（调用函数，可能有输出）
    - DATA 行 + 非空文本    → True（PRINTDATA 块内的数据行）
    - 其他语句              → False（赋值/控制流等不算"文本内容"）

    示例：
      PRINTFORMW 「text」  → True
      PRINTFORMW           → False（空输出）
      PRINTFORMDL          → False（空输出，模板占位符）
      CALL M_KOJO_K15_X    → True
      TFLAG:193 = 0        → False（地文设置，非文本）
    """
    stripped = line.strip()

    # 跳过注释和空行
    if not stripped or stripped.startswith(';'):
        return False

    # 检查 PRINT 命令
    m = RE_PRINT_CMD.match(line)
    if m:
        text_after = m.group(2).strip()
        # PRINT 命令后无文本 = 模板占位符
        if not text_after:
            return False
        # 有实际文本
        return True

    # 检查 DATA 行（PRINTDATA 块内）
    m_data = RE_DATA_LINE.match(line)
    if m_data:
        text_after = m_data.group(1).strip()
        if text_after:
            return True
        return False

    # 检查 CALL 语句（调用其他函数，可能有输出）
    if RE_CALL.match(line):
        return True

    # 其他语句（赋值、控制流、RETURN 等）不算"文本内容"
    return False


def block_has_real_content(lines: List[str], start_idx: int, end_idx: int) -> Tuple[bool, str]:
    """
    检查 IF 块内（start_idx+1 到 end_idx-1）是否有实际内容。

    Returns:
        (has_content, preview) — has_content 为 True 时有实际内容
    """
    content_lines = []
    preview_parts = []

    for i in range(start_idx + 1, end_idx):
        line = lines[i]
        if line_has_print_content(line):
            return True, '\n'.join(lines[start_idx:max(start_idx + 5, i + 1)])
        # 收集非空行用于预览
        stripped = line.strip()
        if stripped and not stripped.startswith(';'):
            if len(preview_parts) < 5:
                preview_parts.append(f"  L{i+1}: {stripped[:80]}")

    return False, '\n'.join(preview_parts) if preview_parts else '(empty block)'


# ---------------------------------------------------------------------------
# 主扫描逻辑
# ---------------------------------------------------------------------------

def scan_file(path: Path, base_dir: Path) -> List[Finding]:
    """
    扫描单个 ERB 文件，返回所有检测结果。
    """
    lines, raw = read_erb_file(path)
    if lines is None:
        return []

    rel_path = str(path.relative_to(base_dir)) if base_dir else str(path)
    findings = []

    # 1. BOM 腐蚀检测
    bom_finding = detect_bom_corruption(raw, lines)
    if bom_finding:
        bom_finding.file_path = rel_path
        findings.append(bom_finding)

    # 2. LOCAL 赋值检测
    local_assigns = find_local_assignments(lines)

    for line_idx, guard_type, sub_idx, value in local_assigns:
        # 只关注 = 0 的（禁用状态）
        if value != 0:
            continue

        # 查找对应的 IF 块
        block_range = find_if_block_for_local(lines, line_idx, sub_idx)
        if block_range is None:
            # 没有 IF 块，可能是 LOCAL 被用作普通变量
            continue

        if_start, endif_end = block_range
        has_content, preview = block_has_real_content(lines, if_start, endif_end)
        func_name = find_enclosing_function(lines, line_idx)

        if has_content:
            # 真禁用：有内容但被 LOCAL = 0 封闭
            suggestion = f'将 {guard_type} = 0 改为 {guard_type} = 1'
            # 检查是否是 IF LOCAL:1 && X 模式（可解包守卫）
            if_line = lines[if_start]
            m = RE_IF_LOCAL.match(if_line)
            if m and m.group(2):  # 有 && 条件
                suggestion += f'，或解包守卫：IF {guard_type} && X → IF X'

            findings.append(Finding(
                file_path=rel_path,
                line_no=line_idx + 1,
                guard_type=guard_type,
                current_value=0,
                finding_type='TRUE_DISABLED',
                if_block_start=if_start + 1,
                if_block_end=endif_end + 1,
                has_content=True,
                content_preview=preview,
                function_name=func_name,
                suggestion=suggestion
            ))
        else:
            # 模板占位符：空块
            findings.append(Finding(
                file_path=rel_path,
                line_no=line_idx + 1,
                guard_type=guard_type,
                current_value=0,
                finding_type='TEMPLATE_PLACEHOLDER',
                if_block_start=if_start + 1,
                if_block_end=endif_end + 1,
                has_content=False,
                content_preview=preview,
                function_name=func_name,
                suggestion='无需修改（模板占位符）'
            ))

    return findings


def scan_directory(
    root_dir: Path,
    file_pattern: str = '*.ERB',
    only_true_disabled: bool = False
) -> ScanResult:
    """
    递归扫描目录下所有 ERB 文件。
    """
    result = ScanResult()

    for path in sorted(root_dir.rglob(file_pattern)):
        result.total_files += 1
        findings = scan_file(path, root_dir)

        for f in findings:
            result.total_local_zeros += 1 if f.finding_type != 'BOM_CORRUPTION' else 0

            if f.finding_type == 'TRUE_DISABLED':
                result.true_disabled += 1
            elif f.finding_type == 'TEMPLATE_PLACEHOLDER':
                result.template_placeholders += 1
            elif f.finding_type == 'BOM_CORRUPTION':
                result.bom_corruptions += 1
            elif f.finding_type == 'GUARD_UNWRAP_CANDIDATE':
                result.guard_unwrap_candidates += 1

            if only_true_disabled and f.finding_type != 'TRUE_DISABLED':
                continue

            result.findings.append(f)

    return result


# ---------------------------------------------------------------------------
# 修复模式
# ---------------------------------------------------------------------------

def detect_encoding(raw_bytes: bytes) -> Tuple[str, bool]:
    """
    检测文件的文本编码与是否带 BOM。

    Returns:
        (encoding_name, has_bom)
    """
    has_bom = raw_bytes[:3] == b'\xef\xbb\xbf'
    # 候选编码（按可能性排序）
    candidates = ['utf-8', 'shift-jis', 'gbk', 'cp932']
    if has_bom:
        # 优先 utf-8-sig
        return 'utf-8-sig', True
    for enc in candidates:
        try:
            raw_bytes.decode(enc)
            return enc, False
        except UnicodeDecodeError:
            continue
    return 'utf-8', False  # fallback


def fix_file(
    path: Path,
    dry_run: bool = False
) -> Tuple[List[Finding], List[Finding], List[str]]:
    """
    修复单个文件：仅将 TRUE_DISABLED 类型的 LOCAL = 0 改为 LOCAL = 1。

    修复策略：
    - 只改 `LOCAL = 0` / `LOCAL:N = 0` → `LOCAL = 1` / `LOCAL:N = 1`
    - **不**改 IF 守卫解包（需要人工判断上下文）
    - **不**改 BOM 腐蚀（需要重写文件头）
    - **不**改模板占位符（空块，保留 0 是正确的）
    - 按行号从大到小修改，避免行号偏移
    - 保留原文件编码和 BOM

    Args:
        path: ERB 文件路径
        dry_run: True 时只返回将要修改的 Finding，不实际写文件

    Returns:
        (modified_findings, skipped_findings, original_lines_before_modify)：
        - modified: 实际修改的（dry_run 时为将要修改的）
        - skipped: 跳过的（TEMPLATE_PLACEHOLDER / BOM_CORRUPTION 等）
        - original_lines: 修改前的内容（用于事后生成 diff 报告）
    """
    lines, raw = read_erb_file(path)
    if lines is None:
        return [], [], []

    # 1. 先扫描获得所有 Finding
    base_dir = path.parent
    all_findings = scan_file(path, base_dir)

    # 2. 筛选 TRUE_DISABLED（这是唯一会被修复的）
    true_disabled = [f for f in all_findings if f.finding_type == 'TRUE_DISABLED']
    skipped = [f for f in all_findings if f.finding_type != 'TRUE_DISABLED']

    # 保留原内容（用于事后 diff 显示）
    original_lines_snapshot = lines[:]

    if not true_disabled or dry_run:
        return true_disabled, skipped, original_lines_snapshot

    # 3. 按行号从大到小排序（避免行号偏移）
    true_disabled_sorted = sorted(true_disabled, key=lambda f: f.line_no, reverse=True)

    # 4. 准备新内容
    new_lines = lines[:]
    for f in true_disabled_sorted:
        idx = f.line_no - 1  # 0-based
        original_line = new_lines[idx]
        # 替换：LOCAL = 0 → LOCAL = 1（保留前导空白和尾部注释）
        # 用 RE_LOCAL_ASSIGN_CORE 匹配核心部分（不含前导空白），保留缩进
        m = RE_LOCAL_ASSIGN_CORE.search(original_line)
        if not m:
            continue
        sub_idx = m.group(1)
        # 重建新行：保留前导空白和尾部
        new_local = f"LOCAL:{sub_idx} = 1" if sub_idx else "LOCAL = 1"
        new_line = original_line[:m.start()] + new_local + original_line[m.end():]
        new_lines[idx] = new_line

    # 5. 检测原编码并写回（保留换行符风格）
    encoding, has_bom = detect_encoding(raw)

    # 重建文本（保留原换行符风格）
    # 检查原文件用 \r\n 还是 \n
    if raw and b'\r\n' in raw:
        line_sep = '\r\n'
    else:
        line_sep = '\n'

    new_text = line_sep.join(new_lines)

    # 写回时编码处理：
    # - 如果原文件是 utf-8-sig (有 BOM)，用 'utf-8-sig' 编码，Python 会自动加 BOM
    # - 如果原文件是 utf-8 (无 BOM)，用 'utf-8' 编码，不要手动加 BOM
    # - 其他编码：手动添加 BOM（如果有）
    if encoding == 'utf-8-sig':
        # utf-8-sig 编码会自动添加 BOM
        write_encoding = 'utf-8-sig'
        new_text_bytes = new_text.encode(write_encoding)
    else:
        write_encoding = encoding
        new_text_bytes = new_text.encode(write_encoding)
        if has_bom:
            # 手动添加 BOM
            new_text_bytes = b'\xef\xbb\xbf' + new_text_bytes

    # 6. 写回文件
    try:
        path.write_bytes(new_text_bytes)
    except (OSError, PermissionError) as e:
        print(f'错误: 无法写入 {path}: {e}', file=sys.stderr)
        return [], skipped, original_lines_snapshot

    return true_disabled, skipped, original_lines_snapshot


def format_fix_diff(path: Path, findings: List[Finding], original_lines: Optional[List[str]] = None) -> str:
    """
    格式化单个文件的 diff 输出（仿 git diff 风格）。

    显示修改前后的 LOCAL 赋值行 + 上下文 3 行。

    Args:
        path: 文件路径
        findings: 修复的 findings
        original_lines: 修改前的行内容（关键：用于显示真实的 -OLD 行）
                       如果为 None，会从文件读取（修复后的内容，无法显示 -OLD）
    """
    if original_lines is None:
        # fallback：读当前文件（修改后）
        lines, _ = read_erb_file(path)
    else:
        lines = original_lines
    if lines is None:
        return ''

    out = []
    out.append(f'--- a/{path}')
    out.append(f'+++ b/{path}')

    for f in findings:
        line_idx = f.line_no - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue

        old_line = lines[line_idx]
        # 重建新行（用 core regex 保留缩进）
        m = RE_LOCAL_ASSIGN_CORE.search(old_line)
        if not m:
            continue
        sub_idx = m.group(1)
        new_local = f"LOCAL:{sub_idx} = 1" if sub_idx else "LOCAL = 1"
        new_line = old_line[:m.start()] + new_local + old_line[m.end():]

        # hunk header
        hunk_start = max(0, line_idx - 2)
        hunk_end = min(len(lines) - 1, line_idx + 2)
        out.append(f'@@ -{f.line_no},{hunk_end - hunk_start + 1} +{f.line_no},{hunk_end - hunk_start + 1} @@')

        for i in range(hunk_start, hunk_end + 1):
            if i == line_idx:
                out.append(f'-{old_line}')
                out.append(f'+{new_line}')
            else:
                out.append(f' {lines[i]}')

        out.append(f'@@ 修复: {f.suggestion}')
        out.append('')

    return '\n'.join(out)


# ---------------------------------------------------------------------------
# 报告输出
# ---------------------------------------------------------------------------

def format_text_report(result: ScanResult) -> str:
    """生成文本格式报告"""
    lines = []
    lines.append('=' * 70)
    lines.append('ERB 被检查标志错误封闭文本块 — 检测报告')
    lines.append('=' * 70)
    lines.append('')
    lines.append('扫描汇总：')
    lines.append(f'  扫描文件数     : {result.total_files}')
    lines.append(f'  LOCAL=0 总数   : {result.total_local_zeros}')
    lines.append(f'  真禁用(候选)   : {result.true_disabled}')
    lines.append(f'  模板占位符     : {result.template_placeholders}')
    lines.append(f'  BOM 腐蚀       : {result.bom_corruptions}')
    lines.append(f'  守卫解包候选   : {result.guard_unwrap_candidates}')
    lines.append('')

    # 按文件分组
    by_file = {}
    for f in result.findings:
        by_file.setdefault(f.file_path, []).append(f)

    # 只显示真禁用和 BOM 腐蚀（模板占位符太多）
    true_findings = [f for f in result.findings if f.finding_type in
                     ('TRUE_DISABLED', 'BOM_CORRUPTION', 'GUARD_UNWRAP_CANDIDATE')]

    if not true_findings:
        lines.append('未发现被错误封闭的文本块。')
        return '\n'.join(lines)

    lines.append(f'需关注的发现（{len(true_findings)} 项）：')
    lines.append('-' * 70)

    current_file = ''
    for f in sorted(true_findings, key=lambda x: (x.file_path, x.line_no)):
        if f.file_path != current_file:
            current_file = f.file_path
            lines.append('')
            lines.append(f'文件: {f.file_path}')

        lines.append(f'  L{f.line_no} [{f.finding_type}] {f.guard_type} = {f.current_value}')
        if f.function_name:
            lines.append(f'    函数: {f.function_name}')
        lines.append(f'    IF块: L{f.if_block_start}-L{f.if_block_end}')
        lines.append(f'    建议: {f.suggestion}')
        if f.content_preview:
            for preview_line in f.content_preview.split('\n')[:5]:
                lines.append(f'    {preview_line}')
        lines.append('')

    return '\n'.join(lines)


def format_json_report(result: ScanResult) -> str:
    """生成 JSON 格式报告"""
    data = {
        'summary': {
            'total_files': result.total_files,
            'total_local_zeros': result.total_local_zeros,
            'true_disabled': result.true_disabled,
            'template_placeholders': result.template_placeholders,
            'bom_corruptions': result.bom_corruptions,
            'guard_unwrap_candidates': result.guard_unwrap_candidates,
        },
        'findings': [
            {
                'file_path': f.file_path,
                'line_no': f.line_no,
                'guard_type': f.guard_type,
                'current_value': f.current_value,
                'finding_type': f.finding_type,
                'if_block_start': f.if_block_start,
                'if_block_end': f.if_block_end,
                'has_content': f.has_content,
                'content_preview': f.content_preview,
                'function_name': f.function_name,
                'suggestion': f.suggestion,
            }
            for f in result.findings
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_csv_report(result: ScanResult) -> str:
    """生成 CSV 格式报告"""
    lines = ['file_path,line_no,guard_type,current_value,finding_type,if_block_start,if_block_end,has_content,function_name,suggestion']
    for f in result.findings:
        # CSV 转义：双引号包裹含逗号的字段
        def esc(s):
            s = str(s)
            if ',' in s or '"' in s or '\n' in s:
                return f'"{s.replace(chr(34), chr(34)+chr(34))}"'
            return s
        lines.append(','.join([
            esc(f.file_path),
            esc(f.line_no),
            esc(f.guard_type),
            esc(f.current_value),
            esc(f.finding_type),
            esc(f.if_block_start),
            esc(f.if_block_end),
            esc(f.has_content),
            esc(f.function_name),
            esc(f.suggestion),
        ]))
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    # 配置 stdout/stderr 为 UTF-8，避免 PowerShell GBK 编码问题
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description='检测/修复 ERB 文件中被检查标志（LOCAL/LOCAL:1）错误封闭的文本块',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 仅检测
  python detect_disabled_blocks.py d:\\eratw-chs\\ERB
  python detect_disabled_blocks.py d:\\eratw-chs\\ERB --format json --output report.json
  python detect_disabled_blocks.py d:\\eratw-chs\\ERB --only-true-disabled

  # 修复模式（修改后用 git diff 审阅，git checkout 撤回不需要的）
  python detect_disabled_blocks.py d:\\eratw-chs\\ERB --fix --dry-run
  python detect_disabled_blocks.py d:\\eratw-chs\\ERB --fix
  python detect_disabled_blocks.py d:\\eratw-chs\\ERB --fix --only-true-disabled
        """
    )
    parser.add_argument('directory', help='要扫描的目录路径')
    parser.add_argument('--format', choices=['text', 'json', 'csv'],
                        default='text', help='输出格式（默认: text）')
    parser.add_argument('--output', '-o', help='输出文件路径（默认: stdout）')
    parser.add_argument('--only-true-disabled', action='store_true',
                        help='只输出真禁用结果（过滤模板占位符）')
    parser.add_argument('--file', default='*.ERB',
                        help='文件 glob 模式（默认: *.ERB）')
    parser.add_argument('--fix', action='store_true',
                        help='修复模式：将 TRUE_DISABLED 的 LOCAL=0 改为 LOCAL=1')
    parser.add_argument('--dry-run', action='store_true',
                        help='干运行：只显示将要修改的内容，不实际写文件（需配合 --fix）')

    args = parser.parse_args()

    root = Path(args.directory)
    if not root.exists():
        print(f'错误: 路径不存在: {root}', file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f'错误: 不是目录: {root}', file=sys.stderr)
        return 2

    if args.dry_run and not args.fix:
        print('错误: --dry-run 必须配合 --fix 使用', file=sys.stderr)
        return 1

    # 修复模式
    if args.fix:
        return run_fix_mode(root, args)

    # 扫描
    result = scan_directory(
        root,
        file_pattern=args.file,
        only_true_disabled=args.only_true_disabled
    )

    # 生成报告
    if args.format == 'text':
        report = format_text_report(result)
    elif args.format == 'json':
        report = format_json_report(result)
    elif args.format == 'csv':
        report = format_csv_report(result)

    # 输出
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f'报告已写入: {args.output}', file=sys.stderr)
    else:
        # 输出到 stdout，处理 PowerShell GBK 编码问题
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
        print(report)

    # 控制台摘要
    print(f'\n--- 摘要 ---', file=sys.stderr)
    print(f'扫描 {result.total_files} 个文件', file=sys.stderr)
    print(f'真禁用(候选修复): {result.true_disabled}', file=sys.stderr)
    print(f'模板占位符(假阳性): {result.template_placeholders}', file=sys.stderr)
    print(f'BOM 腐蚀: {result.bom_corruptions}', file=sys.stderr)

    return 0


def run_fix_mode(root: Path, args) -> int:
    """
    修复模式主流程。

    流程：
    1. 递归遍历所有匹配文件
    2. 对每个文件调用 fix_file() 获取 TRUE_DISABLED findings
    3. dry_run=True 时：只显示 diff
       dry_run=False 时：实际修改文件 + 输出 diff 报告
    """
    # 收集所有 erb 文件
    erb_files = sorted(root.rglob(args.file))
    if not erb_files:
        print(f'未找到匹配 {args.file} 的文件', file=sys.stderr)
        return 0

    # 修复结果统计
    total_files = 0
    total_modified = 0
    total_skipped = 0
    all_diffs = []

    for path in erb_files:
        # 获取该文件所有 findings
        all_findings = scan_file(path, root)
        true_disabled = [f for f in all_findings if f.finding_type == 'TRUE_DISABLED']

        if not true_disabled:
            continue

        total_files += 1

        if args.dry_run:
            # dry-run：只显示 diff，不修改
            modified = true_disabled
            skipped = [f for f in all_findings if f.finding_type != 'TRUE_DISABLED']
            # dry-run 时读当前文件作为 original_lines
            orig_lines, _ = read_erb_file(path)
        else:
            # 实际修复
            modified, skipped, orig_lines = fix_file(path, dry_run=False)

        total_modified += len(modified)
        total_skipped += len(skipped)

        # 生成该文件的 diff
        if modified and orig_lines is not None:
            diff_text = format_fix_diff(path, modified, original_lines=orig_lines)
            all_diffs.append((path, len(modified), diff_text))

    # 输出报告
    report_lines = []
    report_lines.append('=' * 70)
    mode_label = '【DRY-RUN 预览】' if args.dry_run else '【修复完成】'
    report_lines.append(f'ERB LOCAL 守卫修复 {mode_label}')
    report_lines.append('=' * 70)
    report_lines.append('')
    report_lines.append('汇总：')
    report_lines.append(f'  扫描文件数 : {len(erb_files)}')
    report_lines.append(f'  涉及文件数 : {total_files}')
    report_lines.append(f'  修复/预览  : {total_modified} 处')
    report_lines.append(f'  跳过非真禁用: {total_skipped} 处')
    report_lines.append('')

    if not all_diffs:
        report_lines.append('未发现需要修复的 TRUE_DISABLED 块。')
    else:
        report_lines.append(f'修改详情（{len(all_diffs)} 个文件）：')
        report_lines.append('-' * 70)
        for path, count, diff_text in all_diffs:
            report_lines.append(f'\n文件: {path} （{count} 处修改）')
            report_lines.append('-' * 70)
            report_lines.append(diff_text)

    if not args.dry_run:
        report_lines.append('')
        report_lines.append('=' * 70)
        report_lines.append('提示：')
        report_lines.append('  - 用 `git diff` 查看所有修改')
        report_lines.append('  - 用 `git checkout -- <file>` 撤回整个文件')
        report_lines.append('  - 用 `git checkout -p <file>` 交互式撤回部分修改')
        report_lines.append('=' * 70)

    report = '\n'.join(report_lines)

    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f'报告已写入: {args.output}', file=sys.stderr)
    else:
        # 输出到 stdout，处理 PowerShell GBK 编码问题
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
        print(report)

    # 控制台摘要
    print(f'\n--- 修复摘要 ---', file=sys.stderr)
    print(f'扫描 {len(erb_files)} 个文件，{total_files} 个有 TRUE_DISABLED', file=sys.stderr)
    print(f'{"将" if args.dry_run else "已"}修改: {total_modified} 处', file=sys.stderr)
    print(f'跳过: {total_skipped} 处（非 TRUE_DISABLED）', file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
