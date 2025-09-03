import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Arquivos")
        self.root.geometry("900x600")


        self.current_path = os.path.expanduser("~")


        path_frame = tk.Frame(root)
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        self.path_var = tk.StringVar(value=self.current_path)
        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(path_frame, text="Ir", command=self.load_files).pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="Voltar", command=self.go_back).pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(root, columns=("name", "type", "size"), show="headings")
        self.tree.heading("name", text="Nome")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("size", text="Tamanho")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)  

        # Botões de ação
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Excluir", command=self.delete_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Copiar", command=self.copy_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Mover", command=self.move_item).pack(side=tk.LEFT, padx=5, pady=5)

        self.load_files()

    def load_files(self):
        """Carrega arquivos e pastas no TreeView"""
        self.tree.delete(*self.tree.get_children())
        path = self.path_var.get()

        if not os.path.exists(path):
            messagebox.showerror("Erro", "Caminho inválido!")
            return

        self.current_path = path

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

    def on_double_click(self, event):
        """Abrir pasta ou arquivo com duplo clique"""
        selected = self.tree.selection()
        if not selected:
            return
        file_name = self.tree.item(selected[0])["values"][0]
        path = os.path.join(self.current_path, file_name)

        if os.path.isdir(path):
            self.path_var.set(path)
            self.load_files()
        else:
            try:
                os.startfile(path)  
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def go_back(self):
        """Voltar para a pasta anterior"""
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.path_var.set(parent)
            self.load_files()

    def delete_item(self):
        """Excluir arquivo/pasta"""
        selected = self.tree.selection()
        if not selected:
            return
        file_name = self.tree.item(selected[0])["values"][0]
        path = os.path.join(self.current_path, file_name)
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
        src = os.path.join(self.current_path, file_name)
        dest = filedialog.askdirectory()
        if dest:
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(dest, file_name))
                else:
                    shutil.copy2(src, dest)
                messagebox.showinfo("Sucesso", "Arquivo/Pasta copiado!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def move_item(self):
        """Mover arquivo/pasta"""
        selected = self.tree.selection()
        if not selected:
            return
        file_name = self.tree.item(selected[0])["values"][0]
        src = os.path.join(self.current_path, file_name)
        dest = filedialog.askdirectory()
        if dest:
            try:
                shutil.move(src, dest)
                self.load_files()
                messagebox.showinfo("Sucesso", "Arquivo/Pasta movido!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()
