import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import psutil
import platform

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Arquivos Avançado")
        self.root.geometry("1100x600")

        # Frames principais
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame, width=700)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(main_frame, width=400, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Caminho inicial
        self.current_path = os.path.expanduser("~")

        # Barra de caminho
        path_frame = tk.Frame(left_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        self.path_var = tk.StringVar(value=self.current_path)
        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(path_frame, text="Ir", command=self.load_files).pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="Voltar", command=self.go_back).pack(side=tk.LEFT, padx=5)

        # Lista de arquivos
        self.tree = ttk.Treeview(left_frame, columns=("name", "type", "size"), show="headings")
        self.tree.heading("name", text="Nome")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("size", text="Tamanho")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Botões de ação
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Excluir", command=self.delete_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Copiar", command=self.copy_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Mover", command=self.move_item).pack(side=tk.LEFT, padx=5, pady=5)

        # Painel direito: informações do sistema
        self.info_label = tk.Label(right_frame, text="", justify=tk.LEFT, anchor="nw", bg="#f0f0f0", font=("Consolas", 10))
        self.info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.load_files()
        self.update_system_info()

    def load_files(self):
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
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.path_var.set(parent)
            self.load_files()

    def delete_item(self):
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

    def update_system_info(self):
        """Exibe informações da memória e discos"""
        try:
            # Memória
            mem = psutil.virtual_memory()
            mem_info = (
                f"Memória RAM:\n"
                f"  Total: {mem.total // (1024**2)} MB\n"
                f"  Usada: {mem.used // (1024**2)} MB\n"
                f"  Livre: {mem.available // (1024**2)} MB\n"
            )
            # Alguns sistemas têm 'cached'
            if hasattr(mem, "cached"):
                mem_info += f"  Cache: {mem.cached // (1024**2)} MB\n"
            mem_info += "\n"

            # Disco principal
            disk = psutil.disk_usage("/")
            partitions = psutil.disk_partitions()
            fs_info = ""
            for p in partitions:
                fs_info += f"  {p.device} → {p.fstype}\n"

            disk_info = (
                f"Disco:\n"
                f"  Total: {disk.total // (1024**3)} GB\n"
                f"  Usado: {disk.used // (1024**3)} GB\n"
                f"  Livre: {disk.free // (1024**3)} GB\n"
                f"Sistemas de Arquivos:\n{fs_info}\n"
            )

            # SSD ou HD (simplificado)
            try:
                ssd_info = "SSD detectado" if "SSD" in platform.platform() else "HDD ou não detectado"
            except:
                ssd_info = "Não foi possível detectar"

            self.info_label.config(text=mem_info + disk_info + "Tipo: " + ssd_info)
        except Exception as e:
            self.info_label.config(text="Erro ao obter informações do sistema: " + str(e))

        # Atualiza a cada 3 segundos
        self.root.after(3000, self.update_system_info)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()
