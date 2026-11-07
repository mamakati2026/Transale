import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk


def resource_path(relative_path):
  try:
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")
  return os.path.join(base_path, relative_path)


class InstallerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("CloudConvert Telepítő")
    self.root.geometry("450x550")
    self.root.resizable(False, False)

    # Ikon beállítása, ha létezik
    icon_path = resource_path("telepitoparancsikon.ico")
    if os.path.exists(icon_path):
      try:
        self.root.iconbitmap(icon_path)
      except Exception:
        pass

    # Címke
    self.title_label = tk.Label(
        root, text="CloudConvert Telepítő", font=("Arial", 16, "bold")
    )
    self.title_label.pack(pady=15)

    # 1. Lépés: Felhasználói hatáskör választó keret
    self.scope_frame = tk.LabelFrame(
        root, text=" Telepítés hatásköre ", font=("Arial", 10, "bold")
    )
    self.scope_frame.pack(fill="x", padx=20, pady=10)

    self.scope_var = tk.StringVar(value="current")
    tk.Radiobutton(
        self.scope_frame,
        text="Csak nekem (Aktuális felhasználó - Ajánlott)",
        variable=self.scope_var,
        value="current",
        font=("Arial", 9),
    ).pack(anchor="w", padx=10, pady=5)
    tk.Radiobutton(
        self.scope_frame,
        text="A gép összes felhasználójának (Mindenki)",
        variable=self.scope_var,
        value="all",
        font=("Arial", 9),
    ).pack(anchor="w", padx=10, pady=5)

    # Indító gomb a telepítéshez
    self.start_btn = tk.Button(
        root,
        text="Telepítés indítása",
        bg="#007ACC",
        fg="white",
        font=("Arial", 11, "bold"),
        command=self.start_installation,
        padx=10,
        pady=5,
    )
    self.start_btn.pack(pady=15)

    # 2. Folyamatsáv (Progress Bar)
    self.progress = ttk.Progressbar(
        root, orient="horizontal", length=380, mode="determinate"
    )

    # 3. Információs szöveg / Támogatott formátumok lista
    self.info_frame = tk.Frame(root)

    self.info_label = tk.Label(
        self.info_frame,
        text=(
            "A CloudConvert a következő főbb formátumokat támogatja:\n•"
            " Dokumentumok: PDF, DOCX, XLSX, PPTX, TXT, EPUB\n• Képek: JPG,"
            " PNG, WEBP, GIF, SVG, TIFF\n• Audió & Videó: MP4, AVI, MKV, MP3,"
            " WAV, FLAC\n• Archívumok: ZIP, RAR, 7Z, TAR.GZ"
        ),
        font=("Arial", 9),
        justify="left",
        bg="#F0F0F0",
        padx=10,
        pady=10,
    )
    self.info_label.pack(fill="both", expand=True)

    # Befejezés gomb (alapból rejtett)
    self.finish_btn = tk.Button(
        root,
        text="Befejezés",
        bg="#28A745",
        fg="white",
        font=("Arial", 11, "bold"),
        command=root.quit,
        padx=15,
        pady=5,
    )

  def start_installation(self):
    # Letiltjuk a választót és a gombot
    self.start_btn.config(state="disabled")

    # Megjelenítjük a kék folyamatcsíkot
    self.progress.pack(pady=10)
    self.progress["value"] = 0
    self.root.update_idletasks()

    # Háttérben futtatjuk a másolást, hogy ne fagyjon le az ablak
    threading.Thread(target=self.run_install_process).start()

  def run_install_process(self):
    scope = self.scope_var.get()

    # Célmappa meghatározása a választás alapján
    if scope == "all":
      base_dir = os.environ.get("ProgramFiles", "C:\\Program Files")
    else:
      base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))

    install_dir = os.path.join(base_dir, "CloudConvert")

    # Folyamat szimuláció (csík töltése)
    for i in range(1, 51):
      self.progress["value"] = i
      self.root.update_idletasks()
      import time

      time.sleep(0.01)

    # Mappa létrehozása
    try:
      if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    except Exception as e:
      messagebox.showerror(
          "Hiba", f"Nem sikerült létrehozni a mappát (jogosultság?):\n{e}"
      )
      self.start_btn.config(state="normal")
      return

    for i in range(51, 81):
      self.progress["value"] = i
      self.root.update_idletasks()
      time.sleep(0.01)

    # Fájlok átmásolása
    src_exe = resource_path("konvertalo.exe")
    dest_exe = os.path.join(install_dir, "konvertalo.exe")

    src_ico = resource_path("parancsikon.ico")
    dest_ico = os.path.join(install_dir, "parancsikon.ico")

    try:
      if os.path.exists(src_exe):
        shutil.copy2(src_exe, dest_exe)
      if os.path.exists(src_ico):
        shutil.copy2(src_ico, dest_ico)
    except Exception as e:
      messagebox.showerror("Hiba", f"Fájl másolási hiba:\n{e}")
      return

    for i in range(81, 101):
      self.progress["value"] = i
      self.root.update_idletasks()
      time.sleep(0.01)

    # Parancsikon létrehozása az asztalon
    if scope == "all":
      desktop_path = os.path.join(
          os.environ.get("PUBLIC", "C:\\Users\\Public"),
          "Desktop",
          "CloudConvert.lnk",
      )
    else:
      desktop_path = os.path.join(
          os.path.expanduser("~"), "Desktop", "CloudConvert.lnk"
      )

    ps_command = f"""
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{desktop_path}")
        $Shortcut.TargetPath = "{dest_exe}"
        $Shortcut.IconLocation = "{dest_ico}"
        $Shortcut.Save()
        """
    try:
      subprocess.run(
          ["powershell", "-Command", ps_command],
          stdout=subprocess.DEVNULL,
          stderr=subprocess.DEVNULL,
      )
    except Exception:
      pass

    # UI frissítése a fő szálon: megjelenítjük a konvertálható formátumokat és a Befejezés gombot
    self.root.after(0, self.show_success_ui)

  def show_success_ui(self):
    # Eltüntetjük a hatáskör választót és a start gombot
    self.scope_frame.pack_forget()
    self.start_btn.pack_forget()
    self.progress.pack_forget()

    # Megváltoztatjuk a címet
    self.title_label.config(text="Sikeres telepítés!")

    # Megjelenítjük a formátumok listáját és a Befejezés gombot
    self.info_frame.pack(fill="both", expand=True, padx=20, pady=10)
    self.finish_btn.pack(pady=15)


if __name__ == "__main__":
  root = tk.Tk()
  app = InstallerApp(root)
  root.mainloop()