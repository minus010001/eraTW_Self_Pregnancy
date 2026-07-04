import os
import glob
import struct
import xml.etree.ElementTree as ET

def write_string(f, s):
    if s is None:
        s = ""
    b = s.encode('utf-8')
    f.write(struct.pack('<i', len(b)))
    f.write(b)

def build_index():
    xml_files = glob.glob("resources/**/*.xml", recursive=True)
    
    print(f"\n🔍 共找到 {len(xml_files)} 个 XML 文件，开始按顺序解析（utf-8-sig → utf-8 → shift_jis）...\n")
    
    resources = {}
    success_count = 0
    fail_list = []

    # 用户指定顺序：utf8bom(utf-8-sig) → utf8 → shift_jis
    encodings_to_try = ["utf-8-sig", "utf-8", "shift_jis"]

    for path in sorted(xml_files):
        parsed = False
        for encoding in encodings_to_try:
            try:
                # 使用指定的 encoding 解析
                tree = ET.parse(path, parser=ET.XMLParser(encoding=encoding))
                root = tree.getroot()
                
                for child in root:
                    if child.tag == 'i':
                        name = child.get('name')
                        src = child.get('src')
                        param = child.get('param', "")
                        if name:
                            resources[name] = (0, src, param)
                    
                    elif child.tag == 'a':
                        name = child.get('name')
                        width = int(child.get('width', 0))
                        height = int(child.get('height', 0))
                        frames = []
                        for f in child.findall('f'):
                            f_src = f.get('src')
                            f_param = f.get('param', "")
                            frames.append((f_src, f_param))
                        
                        if name:
                            resources[name] = (1, width, height, frames)
                
                success_count += 1
                parsed = True
                print(f"✅ {path}  (编码: {encoding})")
                break  # 解析成功就跳出循环
                
            except Exception as e:
                # 仅在最后一个编码失败时才记录
                if encoding == encodings_to_try[-1]:
                    fail_list.append(path)
                    print(f"❌ {path}  （{encoding} 也失败，已跳过）")
                continue  # 尝试下一个编码
        
        # 如果所有编码都失败，这里已经打印过了

    # 写入二进制索引
    out_path = "resources.idx"
    with open(out_path, "wb") as f:
        f.write(b'RESX')
        f.write(struct.pack('<i', 1))
        f.write(struct.pack('<i', len(resources)))
        
        for name, data in resources.items():
            write_string(f, name)
            type_id = data[0]
            f.write(struct.pack('b', type_id))
            
            if type_id == 0:
                write_string(f, data[1])
                write_string(f, data[2])
            elif type_id == 1:
                f.write(struct.pack('<i', data[1]))
                f.write(struct.pack('<i', data[2]))
                frames = data[3]
                f.write(struct.pack('<i', len(frames)))
                for f_src, f_param in frames:
                    write_string(f, f_src)
                    write_string(f, f_param)

    print("\n" + "="*70)
    print(f"🎉 构建完成！")
    print(f"   成功解析 XML: {success_count} 个")
    print(f"   总资源数量: {len(resources)} 个")
    print(f"   保存到 {out_path}  ({os.path.getsize(out_path)/1024:.1f} KB)")
    
    if fail_list:
        print(f"   跳过 {len(fail_list)} 个无法解析的 XML（这些大多是游戏原版或非标准 XML）")

if __name__ == "__main__":
    build_index()