import os
import re
def process_file(input_file_path, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8-sig') as file_write:
        with open(input_file_path, 'r', encoding='utf-8-sig') as file_read:  # 使用utf-8-sig编码格式打开文件
            lines = file_read.readlines()   # 保存整个文件的数据
        # 创建正则表达式
        re_pattern_comments = re.compile(r'\s*;')
        re_pattern_print = re.compile(r'PRINTFORM([A-z])\s', re.I)
        re_pattern_unicode = re.compile(r'%UNICODE\(0x2665\)\s*\*\s*\d+\s*%', re.I)
        total_num_of_lines = len(lines)
        # 循环处理每一句文本
        for num_of_lines in range(0, total_num_of_lines):
            final_output = ''
            search_result = ''
            origin_line_print_l_or_w = ''
            if re_pattern_comments.search(lines[num_of_lines]) == None:
                if re_pattern_print.search(lines[num_of_lines]):
                    if re_pattern_unicode.search(lines[num_of_lines]):
                        search_result = lines[num_of_lines]
                        search_result = re_pattern_print.sub('CALL HPH_PRINT,@"', str(search_result))
                        for counter in range(1, 10):
                            re_pattern_unicode_dynamic = re.compile(r'%UNICODE\(0x2665\)\s*\*\s*' + str(counter) + r'\s*', re.I)
                            search_result = re_pattern_unicode_dynamic.sub('HPH' * counter, str(search_result))
                            counter += 1
                        origin_line_print_l_or_w = re_pattern_print.search(lines[num_of_lines])
                        if origin_line_print_l_or_w.group(1) == 'l' or origin_line_print_l_or_w.group(1) == 'L':
                            search_result = search_result.replace('\n','')
                            search_result = search_result + '","L"\n'
                        elif origin_line_print_l_or_w.group(1) == 'w' or origin_line_print_l_or_w.group(1) == 'W':
                            search_result = search_result.replace('\n','')
                            search_result = search_result + '","W"\n'
            if search_result:
                final_output = search_result
            else:
                final_output = lines[num_of_lines]
            # 输出
            file_write.write(final_output)
    print('处理完成，点击退出脚本')
    os.system('pause')
    exit()


# input_file_path = input('请输入待处理文件路径（绝对路径或相对路径均可）\n')
# output_file_path = input('请输入输出文件路径（绝对路径或相对路径均可），注意要输入文件名和文件类型，否则会报错\n')
# print(input_file_path)
# print(output_file_path)
# os.system("pause")
# process_file(input_file_path, output_file_path)

def process_charadata():
    #创建正则范式
    re_pattern_filename_incluede = re.compile(r'chara_data', re.I)
    re_pattern_filename_extract = re.compile(r'\d+')
    re_pattern_filecontent_extract = re.compile('CFLAG:CHARA:差し替え適用', re.I)
    #生成输出文件夹路径，由于生成的输出文件夹和递归文件夹在一个路径下因此最后需要break防止无限递归
    if os.path.exists("./ERB/キャラデータ/output"):
        os.rmdir("./ERB/キャラデータ/output")
    os.makedirs("./ERB/キャラデータ/output")
    for root, _, filenames in os.walk("./ERB/キャラデータ"):#忽略子目录文件名，因为目前没有子目录
        for filename in filenames:
            if re_pattern_filename_incluede.search(filename):
                with open(os.path.join(root,filename), 'r', encoding='utf-8-sig') as file_read:
                    lines = file_read.readlines()
                    total_num_of_lines = len(lines)
                with open(os.path.join(root,"output",filename), 'w', encoding='utf-8-sig') as file_write:
                    for num_of_lines in range(0, total_num_of_lines):
                        temp = ''
                        if re_pattern_filecontent_extract.search(lines[num_of_lines]) and re_pattern_filename_extract.search(filename):
                            temp = re_pattern_filecontent_extract.sub(f"CFLAG:{re_pattern_filename_extract.search(filename).group()}:差し替え適用", str(lines[num_of_lines]))
                        if temp == "":
                            file_write.write(lines[num_of_lines])
                        else:
                            file_write.write(temp)
                    print(f'{filename}处理完成')
        if "output" in _:
            break
    print('全部文件处理完成')
    
process_charadata()
exit()