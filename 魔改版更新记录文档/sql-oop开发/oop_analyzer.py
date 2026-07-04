#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F-OOP 函数语法分析器
用于静态分析 F-OOP 函数的运行时依赖，自动归类为 DATA 或 LOGIC
"""

import os
import re
import json
from collections import defaultdict

# 运行时依赖模式正则
RUNTIME_PATTERNS = {
    'GETBIT': r'GETBIT\s*\(\s*(TALENT|FLAG|CFLAG)\s*:\s*ARG\s*:[^)]*\)',
    'GETMETH': r'GETMETH_(INT|STR)\s*\(\s*[^,]+,\s*"[^"]+",\s*ARG',
    'FLAG': r'(FLAG|CFLAG|TALENT)\s*:\s*ARG\s*:',
    'FUNCTION_CALL': r'\b\w+\s*\(\s*ARG\s*\)',
    'CONDITION': r'(IF|SIF)\s+[^\n]+\b(THEN|ENDIF|ELSE)',
    'EVAL': r'EVAL[S]?\s*\(['
}

# 静态模式（编译时常量）
STATIC_PATTERNS = {
    'CONST_BITSHIFT': r'\{1<<[A-Z_]+\}',  # {1<<EQUIP_XXX}
    'CONST_ID': r'\{\[\[[^\]]+\]\]\}',      # {[[靴_鞋子]]}
    'STRING_LITERAL': r'"[^"]*"',          # "字符串"
    'NUMBER_LITERAL': r'\b\d+\b'            # 数字
}

def analyze_file(file_path):
    """分析单个 F-OOP 函数文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='shift_jis') as f:
            content = f.read()
    
    # 提取所有 F-OOP 函数
    functions = re.findall(r'@F([\w\u4e00-\u9fa5]+)(\d+)(\([^)]*\))[\s\S]+?(?=@F|$)', content)
    
    results = []
    for class_name, class_id, _ in functions:
        # 提取该函数的所有 CASE 块
        function_pattern = rf'@F{class_name}{class_id}\([^)]*\)[\s\S]+?(?=@F|$)'
        function_match = re.search(function_pattern, content)
        if not function_match:
            continue
        
        function_content = function_match.group(0)
        
        # 提取所有 CASE 块
        case_blocks = re.findall(r'CASE\s+"([^"]+)"[\s\S]+?(?=CASE|ENDSELECT|$)', function_content)
        
        for case_name in case_blocks:
            # 提取该 CASE 的内容
            case_pattern = rf'CASE\s+"{re.escape(case_name)}"[\s\S]+?(?=CASE|ENDSELECT|$)'
            case_match = re.search(case_pattern, function_content)
            if not case_match:
                continue
            
            case_content = case_match.group(0)
            
            # 检查是否有运行时依赖
            has_runtime = False
            runtime_types = []
            
            for pattern_name, pattern in RUNTIME_PATTERNS.items():
                if re.search(pattern, case_content):
                    has_runtime = True
                    runtime_types.append(pattern_name)
            
            # 检查是否只有静态内容
            has_static = False
            if not has_runtime:
                # 检查是否包含静态模式
                for pattern_name, pattern in STATIC_PATTERNS.items():
                    if re.search(pattern, case_content):
                        has_static = True
                        break
                
                # 检查是否只有 RETURN 常量
                if re.search(r'RETURNF\s+["\{][^\n]+', case_content):
                    has_static = True
            
            if has_runtime:
                category = 'LOGIC'
                dependency = ' | '.join(runtime_types)
            elif has_static:
                category = 'DATA'
                dependency = 'STATIC'
            else:
                category = 'UNKNOWN'
                dependency = 'UNKNOWN'
            
            results.append({
                'file': os.path.basename(file_path),
                'class_name': class_name,
                'class_id': class_id,
                'property': case_name,
                'category': category,
                'dependency': dependency
            })
    
    return results

def analyze_directory(directory):
    """分析目录下所有 F-OOP 函数文件"""
    all_results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.ERB'):
                file_path = os.path.join(root, file)
                print(f"分析: {file_path}")
                results = analyze_file(file_path)
                all_results.extend(results)
    
    return all_results

def generate_report(results, output_file):
    """生成分析报告"""
    # 按类名和ID分组
    grouped = defaultdict(list)
    for item in results:
        key = f"{item['class_name']}{item['class_id']}"
        grouped[key].append(item)
    
    # 生成JSON报告
    report = {
        'total_functions': len(grouped),
        'total_properties': len(results),
        'data_properties': sum(1 for r in results if r['category'] == 'DATA'),
        'logic_properties': sum(1 for r in results if r['category'] == 'LOGIC'),
        'unknown_properties': sum(1 for r in results if r['category'] == 'UNKNOWN'),
        'details': grouped
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成，报告已生成: {output_file}")
    print(f"总计: {len(grouped)} 个函数, {len(results)} 个属性")
    print(f"DATA: {report['data_properties']}, LOGIC: {report['logic_properties']}, UNKNOWN: {report['unknown_properties']}")

def generate_erb_functions(results, output_file):
    """生成 ERB SQL 管理函数"""
    # 提取需要回退的属性
    logic_properties = [r for r in results if r['category'] == 'LOGIC']
    
    erb_functions = '''
@INIT_OOP_SQL_SYSTEM
#FUNCTIONS
#LOCALSIZE 1
#LOCALSSIZE 1

; 连接数据库
SQL_CONNECT("oop_db", "Data Source=oop.db")

; 创建表结构
SQL_EXECUTE_NONQUERY("oop_db", "CREATE TABLE IF NOT EXISTS oop_properties (
    class_type TEXT,
    class_id INTEGER,
    property_name TEXT,
    property_value TEXT,
    is_logic INTEGER DEFAULT 0,
    dependency TEXT,
    PRIMARY KEY (class_type, class_id, property_name)
)")

; 初始化 MAP 缓存
CALL MAKE_ALL_OOP_MAP

; 导入静态数据
CALL IMPORT_STATIC_PROPERTIES

RETURNF 1

@import_static_properties
#FUNCTION
#LOCALSIZE 1
#LOCALSSIZE 1
#DIMS DYNAMIC class_type, class_id, property_name, property_value

; 这里将由分析器自动生成导入语句
'''
    
    # 生成导入语句
    static_properties = [r for r in results if r['category'] == 'DATA']
    for prop in static_properties:
        class_type = prop['class_name']
        class_id = prop['class_id']
        property_name = prop['property']
        # 这里需要从实际函数中提取值，暂时用占位符
        erb_functions += f'''
; {class_type}{class_id}.{property_name}
SQL_EXECUTE_NONQUERY("oop_db", "INSERT OR REPLACE INTO oop_properties VALUES ('{class_type}', {class_id}, '{property_name}', '<VALUE>', 0, 'STATIC')")
'''
    
    # 生成回退函数
    erb_functions += '''
RETURNF 1

@IS_OOP_PROPERTY_LOGIC(class_type, class_id, property_name)
#FUNCTION
#DIMS class_type, class_id, property_name
#LOCALSIZE 1
#LOCALSSIZE 1

#DIMS DYNAMIC result
result '= SQL_EXECUTE_SCALAR_LONG("oop_db", "SELECT is_logic FROM oop_properties WHERE class_type = '" + class_type + "' AND class_id = " + class_id + " AND property_name = '" + property_name + "'")

IF result == 0
    RETURNF 0
ELSE
    RETURNF 1
ENDIF

@GET_OOP_PROPERTY(class_type, class_id, property_name, arg)
#FUNCTION
#DIMS class_type, class_id, property_name, arg
#LOCALSIZE 1
#LOCALSSIZE 1

; 检查是否为逻辑属性
IF IS_OOP_PROPERTY_LOGIC(class_type, class_id, property_name)
    ; 回退到 ERB
    #DIMS DYNAMIC func_name
    func_name '= "F" + class_type + class_id
    RETURNF CALL_ERB_METHOD(func_name, arg, property_name)
ENDIF

; 从 SQL 获取
#DIMS DYNAMIC value
value '= SQL_EXECUTE_SCALAR_STRING("oop_db", "SELECT property_value FROM oop_properties WHERE class_type = '" + class_type + "' AND class_id = " + class_id + " AND property_name = '" + property_name + "'")

IF value != ""
    RETURNF value
ENDIF

; 回退到 ERB
#DIMS DYNAMIC func_name
func_name '= "F" + class_type + class_id
RETURNF CALL_ERB_METHOD(func_name, arg, property_name)
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(erb_functions)
    
    print(f"ERB 函数已生成: {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='F-OOP 函数语法分析器')
    parser.add_argument('directory', help='要分析的目录路径')
    parser.add_argument('--report', default='oop_analysis.json', help='分析报告输出文件')
    parser.add_argument('--erb', default='oop_sql_functions.erb', help='ERB 函数输出文件')
    args = parser.parse_args()
    
    results = analyze_directory(args.directory)
    generate_report(results, args.report)
    generate_erb_functions(results, args.erb)

if __name__ == '__main__':
    main()
