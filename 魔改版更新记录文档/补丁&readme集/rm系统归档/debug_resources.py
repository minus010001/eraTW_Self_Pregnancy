import struct
import json
import os

def read_string(f):
    """读取 length-prefixed UTF-8 字符串"""
    length = struct.unpack('<i', f.read(4))[0]
    if length == 0:
        return ""
    return f.read(length).decode('utf-8')

def debug_resources_idx(input_file="resources.idx", output_file="resources_debug.json"):
    if not os.path.exists(input_file):
        print(f"❌ 未找到 {input_file} 文件！请先运行 mkResourceIndex.py 生成它")
        return

    with open(input_file, "rb") as f:
        # 1. 读取头部
        magic = f.read(4)
        version = struct.unpack('<i', f.read(4))[0]
        count = struct.unpack('<i', f.read(4))[0]

        print(f"✅ 成功打开 {input_file}")
        print(f"   魔数: {magic}")
        print(f"   版本: {version}")
        print(f"   总资源数: {count}")

        resources = {}

        for i in range(count):
            name = read_string(f)
            type_id = struct.unpack('b', f.read(1))[0]   # 1 byte

            if type_id == 0:  # 静态图
                src = read_string(f)
                param = read_string(f)
                resources[name] = {
                    "type": "image",
                    "src": src,
                    "param": param
                }
            elif type_id == 1:  # 动画
                width = struct.unpack('<i', f.read(4))[0]
                height = struct.unpack('<i', f.read(4))[0]
                frame_count = struct.unpack('<i', f.read(4))[0]
                frames = []
                for _ in range(frame_count):
                    f_src = read_string(f)
                    f_param = read_string(f)
                    frames.append({"src": f_src, "param": f_param})

                resources[name] = {
                    "type": "anime",
                    "width": width,
                    "height": height,
                    "frames": frames
                }
            else:
                print(f"⚠️ 未知类型 {type_id}，资源名: {name}")

        # 2. 保存为纯文本 JSON（带缩进，超级好看）
        with open(output_file, "w", encoding="utf-8") as out:
            json.dump(resources, out, ensure_ascii=False, indent=2)

        print(f"🎉 调试完成！共解析 {len(resources)} 个资源")
        print(f"   已保存为 → {output_file}  （用任意文本编辑器打开即可查看）")
        print(f"   文件大小: {os.path.getsize(output_file) / 1024:.1f} KB")

if __name__ == "__main__":
    debug_resources_idx()