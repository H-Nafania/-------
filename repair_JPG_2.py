import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image

# Tkinterウインドウを作成
root = tk.Tk()
root.attributes('-topmost', True)
root.withdraw()

folder_path = filedialog.askdirectory(title="修復したい画像のフォルダを選択してください。")

csvString = '修復不能JPEG, エラー'

if not folder_path:
    messagebox.showerror("エラー", "フォルダが選択されませんでした。")
else:
    # フォルダ内の全てのファイルについて処理を行う
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg")):
            # ファイルのフルパスを取得
            input_file_path = os.path.join(folder_path, filename)
            try:
                img = Image.open(input_file_path)
                # JPGファイルはRGB以外だと破損の可能性あり
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.load()
                img.save(input_file_path)
            except Exception as e:
                csvString = csvString + '\n' + filename + "," + str(e)

with open(os.path.join(folder_path, 'unable_to_repair.csv'), mode='w') as ff:
    ff.write(csvString)

messagebox.showinfo("完了しました。")

def resave_img(file_path) -> str:
    if filename.lower().endswith((".jpg", ".jpeg")):
        try:
            img = Image.open(input_file_path)
            # JPGファイルはRGB以外だと破損の可能性あり
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.load()
            img.save(file_path)
            return "OK"
        except Exception as e:
            return str(e)