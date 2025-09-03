import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Arquivos")
        self.root.geometry("800x500")

    
        self.current_path = os.path.expanduser("~")

        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        self.path_var = tk.StringVar(value=self.current_path)
        path_entry = tk.Entry(frame, textvariable=self.path_var)
        path_entry.pack(fill=tk.X, padx=5, pady=5)

      
        self.tree = ttk.Treeview(frame, columns=("type", "size"), show="headings")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("size", text="Tamanho")
        self.tree.pack(fill=tk.BOTH, expand=True)

       
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Abrir Pasta", command=self.open_folder).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Abrir Arquivo", command=self.open_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Excluir", command=self.delete_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Copiar", command=self.copy_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Mover", command=self.move_item).pack(side=tk.LEFT, padx=5, pady=5)

        self.load_files()

    def load_files(self):
        """Carrega arquivos e pastas na TreeView"""
        self.tree.delete(*self.tree.get_children())
        path = self.path_var.get()

        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    self.tree.insert("", tk.END, values=(item, "Pasta", ""))
                else:
                    size = os.path.getsize(full_path)
                    self.tree.insert("", tk.END, values=(item, "Arquivo", f"{size} bytes"))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def open_folder(self):
        """Escolher pasta"""
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.load_files()

    def open_file(self):
        """Abrir arquivo selecionado"""
        selected = self.tree.selection()
        if not selected:
            return
        file_name = self.tree.item(selected[0])["values"][0]
        path = os.path.join(self.path_var.get(), file_name)
        try:
            os.startfile(path)  # Windows
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def delete_item(self):
        """Excluir arquivo/pasta"""
        selected = self.tree.selection()
        if not selected:
            return
        file_name = self.tree.item(selected[0])["values"][0]
        path = os.path.join(self.path_var.get(), file_name)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.load_files()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def copy_item(self):
        """Copiar arquivo/pasta"""
        selected = self.tree.selection()
        if not selected:
            return
        file_name = self.tree.item(selected[0])["values"][0]
        src = os.path.join(self.path_var.get(), file_name)
        dest = filedialog.askdirectory()
        if dest:
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(dest, file_name))
                else:
                    shutil.copy2(src, dest)
                messagebox.showinfo("Sucesso", "Arquivo/Pasta copiado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def move_item(self):
        """Mover arquivo/pasta"""
        selected = self.tree.selection()
        if not selected:
            return
        file_name = self.tree.item(selected[0])["values"][0]
        src = os.path.join(self.path_var.get(), file_name)
        dest = filedialog.askdirectory()
        if dest:
            try:
                shutil.move(src, dest)
                self.load_files()
                messagebox.showinfo("Sucesso", "Arquivo/Pasta movido com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()
