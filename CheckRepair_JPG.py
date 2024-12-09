import traceback
import csv
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar
from ttkbootstrap import Progressbar
import os
from struct import unpack
import shutil


def check_error_img(input_file_path) -> str:
    with open(input_file_path, 'rb') as f:
        data = f.read()

    # スタートマーカーが「0xffd8」でないと破損
    startmarker, = unpack(">H", data[0:2])
    flag_s = 1 if startmarker == 0xffd8 else 0

    # エンドマーカーが「0xffd9」でないと破損
    endmarker, = unpack(">H", data[-2:])
    flag_e = 1 if endmarker == 0xffd9 else 0

    return "NG" if flag_s * flag_e == 0 else "OK"


def resave_img(file_path) -> str:
    try:
        img = Image.open(file_path)
        # 透明度を持つ画像を白背景のRGBに変換
        if img.mode in ('RGBA', 'LA'):
            alpha = img.split()[3]
        elif img.mode == 'P' and 'transparency' in img.info:
            img = img.convert('RGBA')
            alpha = img.split()[3]
        else:
            img = img.convert('RGB')
            alpha = None

        if alpha is not None:
            background = Image.new('RGB', img.size, (255, 255, 255))  # 白背景
            background.paste(img, mask=alpha)  # アルファチャンネルをマスクとして使用
            img = background

        img.load()
        img.save(file_path)
        return "OK"
    except Exception as e:
        return str(e)

def main():
    # Tkinterウインドウを作成
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()

    folder_path = filedialog.askdirectory(title="画像フォルダを選択してください。")

    # 破損画像を移動するフォルダを作成
    out_folder_path = os.path.join(folder_path, 'broken')
    os.makedirs(out_folder_path, exist_ok=True)

    repaired_folder_path = os.path.join(out_folder_path, 'repaired')
    # out_folder_path = filedialog.askdirectory(title="ログ出力先フォルダを作成してください。")

    if not folder_path:
        messagebox.showerror("エラー", "フォルダが選択されませんでした。")
    else:
        res_dict = {}
        # フォルダ内の全てのファイルについて処理を行う
        files = [f for f in os.listdir(
            folder_path) if f.lower().endswith((".jpg", ".jpeg"))]
        files_size = len(files)

        # プログレスバーを作成
        progress = tk.Toplevel(root)
        progress.title("処理中")
        text_var = StringVar()
        tk.Label(progress, textvariable=text_var).pack(pady=10, padx=10)
        progress_bar = Progressbar(
            progress, length=300, mode='determinate', maximum=files_size)
        progress_bar.pack(pady=10, padx=10)
        progress.update()

        for i, filename in enumerate(files):
            text_var.set(f"処理中({i+1}/{files_size})")
            # ファイルのフルパスを取得
            input_file_path = os.path.join(folder_path, filename)
            output_file_path = os.path.join(out_folder_path, filename)
            repaired_file_path = os.path.join(repaired_folder_path, filename)

            if check_error_img(input_file_path) == "NG":
                # CSV書き込み
                res_dict[filename] = ""

                shutil.copy2(input_file_path, output_file_path)
                res_resave = resave_img(output_file_path)
                if res_resave == "OK":
                    res_dict[filename] = "修復済み"
                    if not os.path.exists(repaired_folder_path):
                        os.mkdir(repaired_folder_path)
                    shutil.move(output_file_path, repaired_file_path)
                else:
                    res_dict[filename] = res_resave

            # プログレスバーを更新
            progress_bar['value'] = i + 1
            progress.update()
        progress.destroy()
    with open(os.path.join(out_folder_path, 'broken_files.csv'), mode='w') as ff:
        writer = csv.writer(ff, lineterminator="\n")
        writer.writerow(["破損ファイル", "修復結果"])
        for k, v in res_dict.items():
            writer.writerow([k, v])

    messagebox.showinfo("完了", "完了しました。\n修復済み画像は手動で上書きしてください。")


if __name__ == '__main__':
    main()
