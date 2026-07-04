import os
from PIL import Image

def list_images_in_directory(directory):
    # 定義支持的圖片格式
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    
    # 根據目前資料夾名稱設定輸出檔案名稱
    folder_name = os.path.basename(directory.rstrip(os.sep))
    output_file = f"{folder_name}.csv"

    # 讓使用者輸入前綴詞
    prefix = input("請輸入要加在 title 前面的固定前綴詞: ")

    with open(output_file, 'w', encoding="utf-8") as f:
        for file_name in os.listdir(directory):
            if any(file_name.lower().endswith(ext) for ext in image_extensions):
                # 去掉附檔名以取得 title
                title = os.path.splitext(file_name)[0]
                # 在 title 前添加前綴詞
                title_with_prefix = f"{prefix}{title}"
                # 打開圖片並獲取寬度和高度
                try:
                    with Image.open(os.path.join(directory, file_name)) as img:
                        width, height = img.size
                except Exception as e:
                    print(f"無法讀取圖片 {file_name}: {e}")
                    continue

                # 格式化並寫入到檔案
                f.write(f"{title_with_prefix},{file_name},0,0,{height},{width}\n")

    print(f"圖片列表已寫入到 {output_file}")

if __name__ == "__main__":
    # 指定目錄路徑
    directory = os.getcwd()  # 使用當前資料夾
    list_images_in_directory(directory)
