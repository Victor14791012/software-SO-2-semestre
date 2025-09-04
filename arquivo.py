import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import psutil
import platform


def format_size(size):
    """Formata o tamanho do arquivo em KB, MB, GB"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


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
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Button(path_frame, text="Ir", command=self.load_files).pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="Voltar", command=self.go_back).pack(side=tk.LEFT, padx=5)

        # Lista de arquivos com scrollbar
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("name", "type", "size"),
                                 show="headings", selectmode="extended")
        self.tree.heading("name", text="Nome")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("size", text="Tamanho")

        self.tree.column("name", width=400)
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("size", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)  

        # Botões de ação
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Excluir", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Copiar", command=self.copy_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Mover", command=self.move_item).pack(side=tk.LEFT, padx=5)

        # Painel direito: informações do sistema
        self.info_label = tk.Label(
            right_frame, text="", justify=tk.LEFT, anchor="nw",
            bg="#f0f0f0", font=("Consolas", 10)
        )
        self.info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Menu de contexto
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Abrir", command=self.open_item)
        self.context_menu.add_command(label="Copiar", command=self.copy_item)
        self.context_menu.add_command(label="Mover", command=self.move_item)
        self.context_menu.add_command(label="Excluir", command=self.delete_item)

        self.load_files()
        self.update_system_info()

    def load_files(self):
        """Carrega os arquivos e pastas no diretório atual"""
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
                    self.tree.insert("", tk.END, values=(item, "Arquivo", format_size(size)))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def on_double_click(self, event):
        self.open_item()

    def open_item(self):
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
        """Volta para a pasta pai"""
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.path_var.set(parent)
            self.load_files()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        for sel in selected:
            file_name = self.tree.item(sel)["values"][0]
            path = os.path.join(self.current_path, file_name)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        self.load_files()

    def copy_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        dest = filedialog.askdirectory()
        if not dest:
            return
        for sel in selected:
            file_name = self.tree.item(sel)["values"][0]
            src = os.path.join(self.current_path, file_name)
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(dest, file_name))
                else:
                    shutil.copy2(src, dest)
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        messagebox.showinfo("Sucesso", "Arquivo(s)/Pasta(s) copiado(s)!")

    def move_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        dest = filedialog.askdirectory()
        if not dest:
            return
        for sel in selected:
            file_name = self.tree.item(sel)["values"][0]
            src = os.path.join(self.current_path, file_name)
            try:
                shutil.move(src, dest)
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        self.load_files()
        messagebox.showinfo("Sucesso", "Arquivo(s)/Pasta(s) movido(s)!")

    def show_context_menu(self, event):
        """Exibe o menu de contexto ao clicar com botão direito"""
        try:
            self.tree.selection_set(self.tree.identify_row(event.y)) 
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def update_system_info(self):
        """Exibe informações da memória e discos"""
        try:
            mem = psutil.virtual_memory()
            mem_info = (
                f"Memória RAM:\n"
                f"  Total: {mem.total // (1024**2)} MB\n"
                f"  Usada: {mem.used // (1024**2)} MB\n"
                f"  Livre: {mem.available // (1024**2)} MB\n"
            )
            if hasattr(mem, "cached"):
                mem_info += f"  Cache: {mem.cached // (1024**2)} MB\n"
            mem_info += "\n"

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

            try:
                ssd_info = "SSD detectado" if "SSD" in platform.platform() else "HDD ou não detectado"
            except:
                ssd_info = "Não foi possível detectar"

            self.info_label.config(text=mem_info + disk_info + "Tipo: " + ssd_info)
        except Exception as e:
            self.info_label.config(text="Erro ao obter informações do sistema: " + str(e))

        self.root.after(3000, self.update_system_info)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()
