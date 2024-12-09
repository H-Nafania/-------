import tkinter as tk
from tkinter import filedialog, messagebox
import os
from struct import unpack
import shutil

# Tkinterウインドウを作成
root = tk.Tk()
root.attributes('-topmost', True)
root.withdraw()

folder_path = filedialog.askdirectory(title="画像フォルダを選択してください。")
# 破損画僧を移動するフォルダを作成
out_folder_path = os.path.join(folder_path, 'broken')
os.makedirs(out_folder_path, exist_ok=True)
# out_folder_path = filedialog.askdirectory(title="ログ出力先フォルダを作成してください。")

csvString = '破損JPEG'

if not folder_path:
    messagebox.showerror("エラー", "フォルダが選択されませんでした。")
else:
    # フォルダ内の全てのファイルについて処理を行う
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".JPG") or filename.endswith(".JPEG"):
            # ファイルのフルパスを取得
            input_file_path = os.path.join(folder_path, filename)
            with open(input_file_path, 'rb') as f:
                data = f.read()
            startmarker, = unpack(">H", data[0:2])
            if startmarker == 0xffd8:
                flag_s = 1
            else:
                flag_s = 0
            endmarker , = unpack(">H", data[-2:])
            if endmarker == 0xffd9:
                flag_e = 1
            else:
                flag_e = 0
            if flag_s * flag_e == 0:
                csvString = csvString + '\n' + filename
                # 破損ファイルをbrokenフォルダに移動
                new_path = os.path.join(out_folder_path, filename)
                shutil.copy2(input_file_path, new_path)

with open(os.path.join(out_folder_path, 'broken_files.csv'), mode='w') as ff:
    ff.write(csvString)

messagebox.showinfo("完了しました。")

# root.mainloop()

