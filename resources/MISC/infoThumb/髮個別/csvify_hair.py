import os
import csv
from PIL import Image

def generate_image_csv(directory):
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    prefix = 'bodyGraph_M_口外_髮_'; 
    #prefix = input("請輸入要加在 title 前面的固定前綴詞: ")
    chara_list_path = os.path.join(directory, "chara_list.txt")

    if not os.path.isfile(chara_list_path):
        print("找不到 chara_list.txt 檔案！")
        return

    output_file = os.path.basename(directory.rstrip(os.sep)) + ".csv"
    missing_file = "missing_images.txt"
    missing_entries = []

    with open(chara_list_path, 'r', encoding="utf-8") as chara_file, \
         open(output_file, 'w', encoding="utf-8") as out_file:

        reader = csv.reader(chara_file)
        for row in reader:
            if len(row) < 2:
                continue
            chara_id = row[0].strip()
            name = row[1].strip()

            # 嘗試找到對應圖片
            image_file = None
            for file_name in os.listdir(directory):
                if any(file_name.lower().endswith(ext) for ext in image_extensions):
                    if name in os.path.splitext(file_name)[0]:
                        image_file = file_name
                        break

            if image_file:
                try:
                    with Image.open(os.path.join(directory, image_file)) as img:
                        width, height = img.size
                except Exception as e:
                    print(f"無法讀取圖片 {image_file}: {e}")
                    continue

                title = f"{prefix}{chara_id}"
                out_file.write(f"{title},{image_file},0,0,{height},{width}\n")
            else:
                missing_entries.append(f"{chara_id},{name}")

    print(f"圖片資料已輸出至 {output_file}")

    if missing_entries:
        print("\n⚠️ 下列角色在資料夾中找不到對應圖片：")
        for missing in missing_entries:
            print(" -", missing)
        
        # 如果你也想寫入檔案
        with open(missing_file, 'w', encoding='utf-8') as mf:
            mf.write("找不到對應圖片的角色：\n")
            for missing in missing_entries:
                mf.write(missing + "\n")
        print(f"\n❗ 缺少圖片清單已寫入：{missing_file}")
    else:
        print("\n✅ 所有角色都有對應圖片！")

if __name__ == "__main__":
    directory = os.getcwd()
    generate_image_csv(directory)
