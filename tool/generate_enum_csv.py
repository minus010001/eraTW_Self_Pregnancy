# tool/generate_enum_csv.py
# 枚举映射生成
# 用法：在终端根目录运行 python tool/generate_enum_csv.py

import os
import re
import csv
import sys

# --- 手动修正字典 ---
# 格式: ("类名", ID数字): "强制显示的名称"
# 用于处理那些返回动态名称（如函数调用）导致正则无法提取的情况
MANUAL_FIXED_NAMES = {
    ("上半身内衣_はだけ不可", 13): "特有胸罩", 
    ("上半身内衣_はだけ不可", 23): "特有泳衣",
    
    ("下半身内衣_ずらし可能", 18): "特有胖次",
    ("下半身内衣_ずらし可能", 35): "特有泳裤",
    
    ("衣装セット", 47): "特有泳装",
    ("レオタード", 14): "特有泳衣",
}

def generate_enum_csv(input_dir, output_file_path):
    # 使用字典存储数据以自动去重: key=(type_name, id_int), value=item_name
    data_map = {}

    # --- 正则表达式定义 ---
    re_old_def = re.compile(r'^@(.+?)(\d+)\(ARG,\s*O_DATA,\s*V_NAME\)')
    re_new_def = re.compile(r'^@F(.+?)(\d+)\(ARG,\s*O_DATA\)')
    re_case_name = re.compile(r'^\s*CASE\s*"名前"')
    re_old_name = re.compile(r'CALLF\s*MAKE_STR\(V_NAME,\s*"(.*?)"\)')
    re_new_name = re.compile(r'RETURNF\s*"(.*?)"')

    file_count = 0
    print(f"正在扫描目录: {input_dir} ...")

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.upper().endswith('.ERB'):
                filepath = os.path.join(root, file)
                file_count += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
                        current_type = None
                        current_id = None
                        current_mode = None 
                        waiting_for_name = False
                        # 标记是否已经通过字典找到名字，如果是，则跳过后续的 CASE 扫描
                        name_already_found = False 

                        for line in f:
                            line = line.strip()
                            
                            # 1. 检查是否是函数定义行
                            match = None
                            mode = None
                            
                            old_match = re_old_def.search(line)
                            if old_match:
                                match = old_match
                                mode = 'OLD'
                            else:
                                new_match = re_new_def.search(line)
                                if new_match:
                                    match = new_match
                                    mode = 'NEW'
                            
                            if match:
                                current_type = match.group(1)
                                current_id = int(match.group(2))
                                current_mode = mode
                                waiting_for_name = False
                                name_already_found = False

                                # [新增逻辑] 优先检查手动字典
                                if (current_type, current_id) in MANUAL_FIXED_NAMES:
                                    fixed_name = MANUAL_FIXED_NAMES[(current_type, current_id)]
                                    data_map[(current_type, current_id)] = fixed_name
                                    name_already_found = True # 标记已找到，后续不再正则提取
                                continue

                            # 如果已经通过字典找到了名字，跳过后续解析，直到下一个函数定义
                            if name_already_found:
                                continue

                            # 2. 常规提取逻辑：寻找 CASE "名前"
                            if current_type is not None:
                                if re_case_name.search(line):
                                    waiting_for_name = True
                                    continue
                                
                                # 3. 提取返回值
                                if waiting_for_name:
                                    extracted_name = None
                                    
                                    if current_mode == 'OLD':
                                        name_match = re_old_name.search(line)
                                        if name_match: extracted_name = name_match.group(1)
                                    elif current_mode == 'NEW':
                                        name_match = re_new_name.search(line)
                                        if name_match: extracted_name = name_match.group(1)
                                    
                                    if extracted_name:
                                        data_map[(current_type, current_id)] = extracted_name
                                        waiting_for_name = False 
                                        current_type = None # 提取完成，重置

                except Exception as e:
                    print(f"读取文件出错 {filepath}: {e}")

    # 转换为列表并排序
    all_items = []
    for (type_name, item_id), item_name in data_map.items():
        all_items.append((type_name, item_id, item_name))

    print(f"共扫描 {file_count} 个文件，提取到 {len(all_items)} 条数据。")

    all_items.sort(key=lambda x: (x[0], x[1]))

    try:
        with open(output_file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["编号", "类名_对象名"])
            for type_name, item_id, item_name in all_items:
                combined_name = f"{type_name}_{item_name}"
                writer.writerow([item_id, combined_name])     
        print(f"成功生成文件: {output_file_path}")
    except IOError as e:
        print(f"写入文件失败: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_dir_target = os.path.join(project_root, "ERB", "OBJ", "CLASS")
    output_file_target = os.path.join(project_root, "Global_Enum_Index.csv")

    if not os.path.exists(input_dir_target):
        print(f"错误：找不到输入目录 '{input_dir_target}'。")
    else:
        generate_enum_csv(input_dir_target, output_file_target)