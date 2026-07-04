import re
import sys
import os


def parse_rename_csv(filepath):
    """解析 _Rename.csv，建立日文↔中文物品名称映射"""
    jp_to_cn = {}
    cn_to_jp = {}
    name_to_id = {}
    id_to_cn = {}
    id_to_jp = {}

    current_section = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith(';'):
                if '素材道具' in stripped and '素材アイテム' not in stripped and '素材道具（汉）' not in stripped:
                    current_section = 'chinese'
                elif '素材アイテム' in stripped:
                    current_section = 'japanese'
                continue

            if ',' not in stripped:
                continue
            parts = stripped.split(',', 1)
            try:
                item_id = int(parts[0].strip())
                name = parts[1].strip()
                if current_section == 'japanese':
                    if item_id not in id_to_jp:
                        id_to_jp[item_id] = name
                elif current_section == 'chinese':
                    if item_id not in id_to_cn:
                        id_to_cn[item_id] = name
            except ValueError:
                pass

    for item_id, jp_name in id_to_jp.items():
        name_to_id[jp_name] = item_id
        if item_id in id_to_cn:
            cn_name = id_to_cn[item_id]
            jp_to_cn[jp_name] = cn_name
            cn_to_jp[cn_name] = jp_name

    for item_id, cn_name in id_to_cn.items():
        name_to_id[cn_name] = item_id

    return jp_to_cn, cn_to_jp, name_to_id


def extract_case_items(stripped):
    """从 CASE [[item1]], [[item2]], ... 中提取物品名称列表"""
    case_match = re.match(
        r'CASE\s+(\[\[.+?\]\](?:\s*,\s*\[\[.+?\]\])*)',
        stripped
    )
    if case_match:
        return re.findall(r'\[\[(.+?)\]\]', case_match.group(1))
    return None


def collect_until_endselect(lines, start_idx):
    """从 start_idx 开始收集直到匹配的 ENDSELECT，返回 (block_lines, end_idx)"""
    depth = 0
    started = False
    for i in range(start_idx, len(lines)):
        s = lines[i].strip()
        if s == 'SELECTCASE ARGS' or s == 'SELECTCASE ARG':
            depth += 1
            started = True
            continue
        if started and s == 'ENDSELECT':
            depth -= 1
            if depth == 0:
                return lines[start_idx + 1:i], i
    return None, -1


def parse_types_shops_from_case(stripped):
    """从 CASE "TYPE:xxx", "SHOP:yyy" 中提取 types 和 shops"""
    types = []
    shops = []
    matches = re.findall(r'"([^"]+)"', stripped)
    for m in matches:
        if m.startswith('TYPE:'):
            types.append(m[5:])
        elif m.startswith('SHOP:'):
            shops.append(m[5:])
    return types, shops


def analyze_sales_code(sales_code_lines, item_name):
    """
    分析 SALES 代码块，返回 (sales_mode, condition_key)
    """
    code = ' '.join(sales_code_lines)
    code = re.sub(r';.*', '', code)
    code = code.strip()

    if not code:
        return 'UNIQUE', ''

    if 'RETURN 99' in code and 'IF' not in code:
        return 'INFINITE', ''

    if 'RETURN 1' in code and 'IF' not in code:
        return 'NOSALE', ''

    if 'ITEMSALES:' in code:
        return 'STOCK', ''

    has_complex = any(x in code for x in ['TALENT:', 'ABL:', 'FINDCHARA', 'SUMCARRAY', 'ALLSAMES', 'MAGIC_DLC'])
    has_return_neg2 = 'RETURN -2' in code

    if not has_complex and not has_return_neg2 and 'ITEM:ARG' in code:
        if 'RETURN -1' in code and 'RETURN 0' in code:
            return 'UNIQUE', ''

    if has_complex or has_return_neg2:
        return 'CONDITIONAL', item_name

    return 'UNIQUE', ''


def analyze_buy_code(buy_code_lines):
    """分析购买代码块，返回购买函数名或特殊标记"""
    code_lines = [re.sub(r';.*', '', l).strip() for l in buy_code_lines]
    code_lines = [l for l in code_lines if l]
    code = ' '.join(code_lines)
    code = re.sub(r'\s+', ' ', code).strip()

    if not code:
        return 'ITEM_BUY_NONE'

    if code == 'CALL SHOP_ASK(ARG, ARG:1)':
        return ''

    if 'CALL ITEM_MATOMEGAI(ARG, ARG:1)' in code:
        return ''

    if 'PRINTFORMW' in code:
        return 'CUSTOM'

    has_complex = False
    if 'TALENT:' in code and ('=' in code or '++' in code or '--' in code):
        has_complex = True
    if 'ABL:' in code and ('=' in code or '++' in code or '--' in code):
        has_complex = True
    if 'JUEL:' in code or 'EXP:' in code:
        has_complex = True
    if 'PRINTFORMW' in code:
        has_complex = True

    if has_complex:
        return 'CUSTOM'

    return ''


def make_condition_key(item_name):
    return item_name.replace('【', '').replace('】', '')


def make_buy_func_name(item_name):
    name = item_name.replace('【', '').replace('】', '')
    return f'ITEM_BUY_{name}'


def parse_sales_block(block_lines):
    types = []
    shops = []
    has_sales = False
    has_buy = False
    sales_code_lines = []
    buy_code_lines = []
    current_case = None
    current_lines = []

    def flush_case():
        nonlocal current_case, current_lines, has_sales, has_buy
        if current_case == 'SALES':
            has_sales = True
            sales_code_lines.extend(current_lines)
        elif current_case == '購入':
            has_buy = True
            buy_code_lines.extend(current_lines)
        elif current_case and (current_case.startswith('TYPE:') or current_case.startswith('SHOP:')):
            pass
        current_lines = []

    for line in block_lines:
        stripped = line.strip()

        if not stripped or stripped.startswith(';'):
            continue

        case_match = re.match(r'^CASE\s+(.*)', stripped)
        if case_match:
            flush_case()
            values = re.findall(r'"([^"]+)"', case_match.group(1))
            if values:
                current_case = values[0]
                for v in values:
                    if v.startswith('TYPE:'):
                        types.append(v[5:])
                    elif v.startswith('SHOP:'):
                        shops.append(v[5:])
                    elif v not in ('SALES', '購入'):
                        types.append(v)
            else:
                current_case = None
        else:
            if current_case == 'SALES' or current_case == '購入':
                current_lines.append(stripped)

    flush_case()

    return types, shops, has_sales, has_buy, sales_code_lines, buy_code_lines


def parse_add_item_modlist(filepath):
    """解析 Add_Item.ERB 中的 @Add_ItemModList 函数，返回覆盖规则字典"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找到 @Add_ItemModList(ARG, ARGS, ARG:1)
    func_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('@Add_ItemModList('):
            func_start = i
            break
    if func_start == -1:
        print('  [警告] 未找到 @Add_ItemModList 函数', file=sys.stderr)
        return {}

    # 跳过函数定义行，解析 SELECTCASE ARG
    i = func_start + 1
    while i < len(lines) and not lines[i].strip():
        i += 1

    if i >= len(lines) or lines[i].strip() != 'SELECTCASE ARG':
        print('  [警告] @Add_ItemModList 没有 SELECTCASE ARG', file=sys.stderr)
        return {}

    i += 1

    overrides = {}

    # 解析顶层 CASE [[item]] 块
    while i < len(lines):
        stripped = lines[i].strip()

        if not stripped or stripped.startswith(';'):
            i += 1
            continue

        if stripped == 'ENDSELECT':
            break

        if not stripped.startswith('CASE '):
            i += 1
            continue

        # 提取物品名
        item_names = extract_case_items(stripped)
        if item_names is None:
            i += 1
            continue

        i += 1

        # 跳过空白和注释
        while i < len(lines) and (not lines[i].strip() or (lines[i].strip().startswith(';') and not lines[i].strip().startswith(';SHOP_COND:'))):
            i += 1

        if i >= len(lines):
            break

        # 检查是否有内部 SELECTCASE ARGS
        if lines[i].strip() != 'SELECTCASE ARGS':
            continue

        # 收集内部块
        block_lines, end_idx = collect_until_endselect(lines, i)
        if block_lines is None:
            continue

        i = end_idx + 1

        # 解析内部块
        mod_types = []
        mod_shops = []
        mod_sales_lines = []
        mod_buy_lines = []
        has_mod_sales = False
        has_mod_buy = False
        current_case = None
        current_lines = []

        def flush_mod():
            nonlocal current_case, current_lines, has_mod_sales, has_mod_buy
            if current_case == 'SALES':
                has_mod_sales = True
                mod_sales_lines.extend(current_lines)
            elif current_case == '購入':
                has_mod_buy = True
                mod_buy_lines.extend(current_lines)
            current_lines = []

        for bline in block_lines:
            bs = bline.strip()
            if not bs or bs.startswith(';'):
                continue
            cm = re.match(r'^CASE\s+(.*)', bs)
            if cm:
                flush_mod()
                values = re.findall(r'"([^"]+)"', cm.group(1))
                if values:
                    current_case = values[0]
                    for v in values:
                        if v.startswith('TYPE:'):
                            mod_types.append(v[5:])
                        elif v.startswith('SHOP:'):
                            mod_shops.append(v[5:])
                else:
                    current_case = None
            else:
                if current_case in ('SALES', '購入'):
                    current_lines.append(bs)

        flush_mod()

        # 保存覆盖规则
        for name in item_names:
            overrides[name] = {
                'types_add': mod_types,
                'shops_add': mod_shops,
                'sales_lines': mod_sales_lines if has_mod_sales else None,
                'buy_lines': mod_buy_lines if has_mod_buy else None,
            }

    return overrides


def generate_qol_call(item_name, types, shops, sales_mode, sales_cond='', buy_func='', is_custom=0, shop_cond=''):
    types_str = '/'.join(types) if types else ''
    shops_str = '/'.join(shops) if shops else ''

    parts = [f'CALL QOL_ITEM_DATA_SET([[{item_name}]], "{types_str}", "{shops_str}", "{sales_mode}"']

    if sales_cond or buy_func or is_custom or shop_cond:
        parts.append(f'"{sales_cond}"')
        if buy_func or is_custom or shop_cond:
            parts.append(f'"{buy_func}"')
            if is_custom or shop_cond:
                parts.append('1' if is_custom else '0')
                if shop_cond:
                    parts.append(f'"{shop_cond}"')

    return ', '.join(parts) + ')\n'


def find_override_key(name, mod_overrides, cn_to_jp):
    """通过名称或日文→中文映射查找 override 键"""
    if name in mod_overrides:
        return name
    if name in cn_to_jp and cn_to_jp[name] in mod_overrides:
        return cn_to_jp[name]
    return None


def main():
    if len(sys.argv) < 3:
        print('Usage: python convert_itemdata.py <path_to_ITEMDATA.ERB> <path_to_Add_Item.ERB> [output_file]', file=sys.stderr)
        sys.exit(1)

    itemdata_path = sys.argv[1]
    add_item_path = sys.argv[2]

    # 支持输出到文件（解决 Windows 控制台编码问题）
    output_file = None
    if len(sys.argv) >= 4:
        output_file = sys.argv[3]

    # 解析 _Rename.csv 建立日文↔中文名称映射（从脚本所在目录推导 CSV 路径）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'CSV', '_Rename.csv')
    print(f'; 解析名称映射: {csv_path}', file=sys.stderr)
    jp_to_cn, cn_to_jp, name_to_id = parse_rename_csv(csv_path)
    print(f'; 发现 {len(jp_to_cn)} 个日文→中文名称映射', file=sys.stderr)

    # 1. 先解析 Add_ItemModList 覆盖规则
    print('; 解析 Add_ItemModList 覆盖规则...', file=sys.stderr)
    mod_overrides = parse_add_item_modlist(add_item_path)
    print(f'; 发现 {len(mod_overrides)} 个有覆盖规则的道具', file=sys.stderr)

    # 2. 解析 ITEMDATA.ERB
    with open(itemdata_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    all_items = []
    matched_overrides = set()
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()

        if not stripped or stripped.startswith(';'):
            i += 1
            continue

        if not stripped.startswith('CASE '):
            i += 1
            continue

        item_names = extract_case_items(stripped)
        if item_names is None:
            i += 1
            continue

        i += 1

        while i < len(lines) and (not lines[i].strip() or (lines[i].strip().startswith(';') and not lines[i].strip().startswith(';SHOP_COND:'))):
            i += 1

        if i >= len(lines):
            break

        shop_cond = ''
        if lines[i].strip().startswith(';SHOP_COND:'):
            shop_cond = lines[i].strip().split(':', 1)[1].strip()
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith(';')):
                i += 1

        if i >= len(lines):
            break

        if lines[i].strip() != 'SELECTCASE ARGS':
            for name in item_names:
                types = []
                shops = []
                # 应用 Add_ItemModList 覆盖（通过名称映射）
                override_key = find_override_key(name, mod_overrides, cn_to_jp)
                if override_key:
                    ov = mod_overrides[override_key]
                    types.extend(ov['types_add'])
                    shops.extend(ov['shops_add'])
                    matched_overrides.add(override_key)

                all_items.append({
                    'name': name,
                    'types': types,
                    'shops': shops,
                    'sales_mode': 'NOSALE',
                    'sales_cond': '',
                    'buy_func': '',
                    'is_custom': 0,
                    'shop_cond': '',
                })
            continue

        block_lines, end_idx = collect_until_endselect(lines, i)
        if block_lines is None:
            print(f'  [警告] 无法找到 SELECTCASE 的结尾: {item_names}', file=sys.stderr)
            continue

        i = end_idx + 1

        types, shops, has_sales, has_buy, sales_code_lines, buy_code_lines = parse_sales_block(block_lines)

        for name in item_names:
            override_key = find_override_key(name, mod_overrides, cn_to_jp)
            if override_key:
                matched_overrides.add(override_key)

            sales_mode, sales_cond = 'NOSALE', ''

            # 检查 Add_ItemModList 是否有 SALES 覆盖（通过名称映射）
            if override_key and mod_overrides[override_key]['sales_lines'] is not None:
                sales_mode, sales_cond = analyze_sales_code(mod_overrides[override_key]['sales_lines'], name)
            elif has_sales:
                sales_mode, sales_cond = analyze_sales_code(sales_code_lines, name)
            elif types or shops:
                sales_mode = 'NOSALE'

            buy_func = ''
            is_custom = 0

            # 检查 Add_ItemModList 是否有 購入 覆盖（通过名称映射）
            if override_key and mod_overrides[override_key]['buy_lines'] is not None:
                buy_func = analyze_buy_code(mod_overrides[override_key]['buy_lines'])
                if buy_func == 'CUSTOM':
                    buy_func = ''
                    is_custom = 1
            elif has_buy:
                buy_func = analyze_buy_code(buy_code_lines)
                if buy_func == 'CUSTOM':
                    buy_func = ''
                    is_custom = 1

            if sales_cond:
                sales_cond = make_condition_key(sales_cond)

            # Add_ItemModList 来源的道具标记为 is_custom（不自动生成 buy_func）
            has_mod_override = override_key is not None

            if buy_func == 'ITEM_BUY_NONE' and is_custom:
                pass
            elif is_custom and not buy_func:
                generated = make_buy_func_name(name)
                buy_func = generated

            # Add_ItemModList 来源：标记 is_custom，保持默认购买行为
            if has_mod_override:
                is_custom = 1

            # 特殊标记：折畳傘和圣诞节禮物有自定义购买函数
            if name == '折畳傘' or name == '圣诞节禮物':
                is_custom = 1

            # 应用 Add_ItemModList 的类型和商店覆盖（追加，通过名称映射）
            merged_types = list(types)
            merged_shops = list(shops)
            if override_key:
                ov = mod_overrides[override_key]
                for t in ov['types_add']:
                    if t not in merged_types:
                        merged_types.append(t)
                for s in ov['shops_add']:
                    if s not in merged_shops:
                        merged_shops.append(s)

            all_items.append({
                'name': name,
                'types': merged_types,
                'shops': merged_shops,
                'sales_mode': sales_mode,
                'sales_cond': sales_cond,
                'buy_func': buy_func if buy_func else '',
                'is_custom': is_custom,
                'shop_cond': shop_cond,
            })

    # 处理仅在 Add_ItemModList 中的道具（叠加在 ITEMDATA 注册表末尾，实现 override 语义）
    for key, ov in mod_overrides.items():
        if key in matched_overrides:
            continue

        # 确定输出名称：优先使用中文名
        output_name = jp_to_cn.get(key, key)

        # 分析 SALES
        sales_mode, sales_cond = 'NOSALE', ''
        if ov['sales_lines'] is not None:
            sales_mode, sales_cond = analyze_sales_code(ov['sales_lines'], key)

        # 分析 購入
        buy_func = ''
        is_custom = 1
        if ov['buy_lines'] is not None:
            buy_func = analyze_buy_code(ov['buy_lines'])
            if buy_func == 'CUSTOM':
                buy_func = ''
                is_custom = 1

        if sales_cond:
            sales_cond = make_condition_key(sales_cond)

        # Add_ItemModList 定义的道具：使用默认名称生成购买函数
        if is_custom and not buy_func:
            generated = make_buy_func_name(output_name)
            buy_func = generated

        all_items.append({
            'name': output_name,
            'types': ov['types_add'],
            'shops': ov['shops_add'],
            'sales_mode': sales_mode,
            'sales_cond': sales_cond,
            'buy_func': buy_func if buy_func else '',
            'is_custom': is_custom,
            'shop_cond': '',
        })

    # 输出（支持输出到文件解决编码问题）
    if output_file:
        import io
        old_stdout = sys.stdout
        sys.stdout = io.open(output_file, 'w', encoding='utf-8')

    print('; 由 ITEMDATA.ERB + Add_ItemModList 自动转换生成（Add_ItemModList 项叠加在末尾实现 override）')
    print('@QOL_ITEM_DATA_REGISTER')
    print('#LOCALSIZE 1')
    print('#LOCALSSIZE 1')
    print()

    for item in all_items:
        print(generate_qol_call(
            item['name'],
            item['types'],
            item['shops'],
            item['sales_mode'],
            item['sales_cond'],
            item['buy_func'],
            item['is_custom'],
            item.get('shop_cond', ''),
        ), end='')

    print()
    print(f'; 总计转换 {len(all_items)} 个道具')

    if output_file:
        sys.stdout.close()
        sys.stdout = old_stdout
        print(f'; 输出已写入: {output_file}', file=sys.stderr)


if __name__ == '__main__':
    main()
