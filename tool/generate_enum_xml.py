# tool/generate_enum_xml.py
# 枚举XML生成工具
# 用法：在终端根目录运行 python tool/generate_enum_xml.py
# 输出：会在项目根目录下生成 EnumXML 文件夹，内部包含分类后的 xml 文件

import os
import re
import html

# --- 手动修正字典 ---
# 格式: ("类名", ID数字): "强制显示的名称"
MANUAL_FIXED_NAMES = {
    ("上半身内衣_はだけ不可", 13): "特有胸罩",
    ("上半身内衣_はだけ不可", 23): "特有泳衣",

    ("下半身内衣_ずらし可能", 18): "特有胖次",
    ("下半身内衣_ずらし可能", 35): "特有泳裤",
    
    ("衣装セット", 47): "特有泳装",
    ("レオタード", 14): "特有泳衣",
}

def escape_xml(text):
    return html.escape(str(text), quote=True)

def generate_enum_xml(input_dir, output_dir):
    # 数据结构: { "类型名": { ID: "名字" } }
    class_data = {}

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
                        name_already_found = False

                        for line in f:
                            line = line.strip()
                            
                            # 1. 匹配函数头
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
                                    
                                    if current_type not in class_data:
                                        class_data[current_type] = {}
                                    class_data[current_type][current_id] = fixed_name
                                    
                                    name_already_found = True
                                continue
                            
                            if name_already_found:
                                continue

                            # 2. 常规提取
                            if current_type is not None:
                                if re_case_name.search(line):
                                    waiting_for_name = True
                                    continue
                                
                                if waiting_for_name:
                                    extracted_name = None
                                    if current_mode == 'OLD':
                                        name_match = re_old_name.search(line)
                                        if name_match: extracted_name = name_match.group(1)
                                    elif current_mode == 'NEW':
                                        name_match = re_new_name.search(line)
                                        if name_match: extracted_name = name_match.group(1)
                                    
                                    if extracted_name:
                                        if current_type not in class_data:
                                            class_data[current_type] = {}
                                        class_data[current_type][current_id] = extracted_name
                                        
                                        waiting_for_name = False 
                                        current_type = None 

                except Exception as e:
                    print(f"读取文件出错 {filepath}: {e}")

    # --- 生成 XML ---
    print(f"扫描完成，开始生成 XML...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_xml_count = 0
    for type_name, items in class_data.items():
        sorted_ids = sorted(items.keys())

        # ID2NAME
        xml_lines_id2name = ["<map>"]
        for item_id in sorted_ids:
            name = items[item_id]
            xml_lines_id2name.append(f"    <p><k>{item_id}</k><v>{escape_xml(name)}</v></p>")
        xml_lines_id2name.append("</map>")
        
        with open(os.path.join(output_dir, f"{type_name}_ID2NAME.xml"), 'w', encoding='utf-8') as f:
            f.write("\n".join(xml_lines_id2name))
        total_xml_count += 1

        # NAME2ID
        xml_lines_name2id = ["<map>"]
        for item_id in sorted_ids:
            name = items[item_id]
            xml_lines_name2id.append(f"    <p><k>{escape_xml(name)}</k><v>{item_id}</v></p>")
        xml_lines_name2id.append("</map>")

        with open(os.path.join(output_dir, f"{type_name}_NAME2ID.xml"), 'w', encoding='utf-8') as f:
            f.write("\n".join(xml_lines_name2id))
        total_xml_count += 1

    print(f"生成完毕！共 {total_xml_count} 个文件已保存至 {output_dir}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_dir_target = os.path.join(project_root, "ERB", "OBJ", "CLASS")
    output_dir_target = os.path.join(project_root, "EnumXML")

    if not os.path.exists(input_dir_target):
        print(f"错误：找不到输入目录 '{input_dir_target}'。")
    else:
        generate_enum_xml(input_dir_target, output_dir_target)