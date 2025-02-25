import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import json
import sys
import os

CONFIG_FILE = "config.json"


def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funcionando tanto en desarrollo como en el ejecutable."""
    try:
        # PyInstaller crea una carpeta temporal _MEIPASS donde se ubican los recursos.
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class WSLManager:
    def __init__(self, root):
        # Configuración del título, geometría y centrado de la ventana
        self.root = root
        self.root.title("WSL Manager v2 - by @GUIRATEC")
        width, height = 700, 320
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        # Establecer el icono (archivo wsl.ico en la misma carpeta)
        self.root.iconbitmap(resource_path("wsl.ico"))

        # Cargar la configuración (ruta para exportar)
        self.load_config()

        # Crear el CTkTabview para organizar las secciones
        self.tabview = ctk.CTkTabview(root, width=680, height=280)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        self.tabview.add("Configuración")
        self.tabview.add("Instalar Distro")
        self.tabview.add("Ejecutar Distro")
        self.tabview.add("Mover Distro")
        self.tabview.add("Mover Distro desde Archivo Local")
        self.tabview.add("Eliminar Distro")

        # Crear el contenido de cada pestaña
        self.create_config_tab()
        self.create_install_tab()
        self.create_execute_tab()
        self.create_move_tab()
        self.create_local_move_tab()
        self.create_delete_tab()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"export_path": ""}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)
        messagebox.showinfo(
            "Configuración", "¡Configuración guardada exitosamente!")

    def create_config_tab(self):
        tab = self.tabview.tab("Configuración")

        label_export = ctk.CTkLabel(tab, text="Ruta para exportar distros:")
        label_export.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.export_entry = ctk.CTkEntry(tab, width=350)
        self.export_entry.grid(row=0, column=1, padx=5, pady=5)
        self.export_entry.insert(0, self.config.get("export_path", ""))

        btn_export = ctk.CTkButton(
            tab, text="Seleccionar carpeta", command=self.select_export_folder)
        btn_export.grid(row=0, column=2, padx=5, pady=5)

        btn_save = ctk.CTkButton(
            tab, text="Guardar Configuración", command=self.update_config)
        btn_save.grid(row=1, column=1, pady=10)

    def select_export_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.export_entry.delete(0, "end")
            self.export_entry.insert(0, folder)

    def update_config(self):
        self.config["export_path"] = self.export_entry.get().replace("\0", "")
        self.save_config()

    def create_install_tab(self):
        tab = self.tabview.tab("Instalar Distro")

        btn_refresh_online = ctk.CTkButton(
            tab, text="Actualizar lista de distros online", command=self.refresh_online_distros)
        btn_refresh_online.pack(pady=5)

        self.online_combo = ctk.CTkComboBox(tab, width=300)
        self.online_combo.pack(pady=5)
        self.online_combo.set("")

        btn_install = ctk.CTkButton(
            tab, text="Instalar Distro", command=self.install_distro)
        btn_install.pack(pady=5)

        self.online_list = []
        self.refresh_online_distros()

    def refresh_online_distros(self):
        try:
            result = subprocess.run(
                ["wsl", "--list", "--online"], capture_output=True, check=True)
            stdout_clean = result.stdout.decode(
                "utf-8", errors="replace").replace("\0", "")
            lines = stdout_clean.splitlines()
            distros = []
            for line in lines:
                parts = line.split()
                if parts:
                    if parts[0].lower() in ["name", "distribucion"]:
                        continue
                    distros.append(parts[0])
            self.online_list = distros
            self.online_combo.configure(values=distros)
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros online: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros online: {str(e)}")

    def install_distro(self):
        distro = self.online_combo.get().replace("\0", "")
        if not distro:
            messagebox.showwarning(
                "Advertencia", "Seleccione una distro para instalar.")
            return
        try:
            cmd = ["wsl", "--install", "-d", distro]
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Instalar Distro",
                                f"La instalación de {distro} ha comenzado.")
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror(
                "Error", f"Error al instalar la distro: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al instalar la distro: {str(e)}")

    def create_execute_tab(self):
        tab = self.tabview.tab("Ejecutar Distro")

        btn_refresh_installed = ctk.CTkButton(
            tab, text="Actualizar lista de distros instaladas", command=self.refresh_installed_distros)
        btn_refresh_installed.pack(pady=5)

        self.installed_combo = ctk.CTkComboBox(tab, width=300)
        self.installed_combo.pack(pady=5)
        self.installed_combo.set("")

        btn_execute = ctk.CTkButton(
            tab, text="Ejecutar Distro", command=self.execute_distro)
        btn_execute.pack(pady=5)

        self.refresh_installed_distros()

    def refresh_installed_distros(self):
        try:
            result = subprocess.run(
                ["wsl", "--list"], capture_output=True, check=True)
            stdout_clean = result.stdout.decode(
                "utf-8", errors="replace").replace("\0", "")
            lines = stdout_clean.splitlines()
            distros = []
            for line in lines:
                line_clean = line.replace("\0", "")
                if line_clean.strip() == "" or "Windows Subsystem" in line_clean or "distro" in line_clean.lower():
                    continue
                distro_name = line_clean.replace("*", "").strip()
                if distro_name:
                    distros.append(distro_name)
            self.installed_combo.configure(values=distros)
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros instaladas: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros instaladas: {str(e)}")

    def execute_distro(self):
        distro = self.installed_combo.get().replace("\0", "")
        if not distro:
            messagebox.showwarning(
                "Advertencia", "Seleccione una distro para ejecutar.")
            return
        try:
            cmd = f'start cmd /k wsl -d {distro}'
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al ejecutar la distro: {str(e)}")

    def create_move_tab(self):
        tab = self.tabview.tab("Mover Distro")

        btn_refresh_move = ctk.CTkButton(
            tab, text="Actualizar lista de distros instaladas", command=self.refresh_installed_distros_move)
        btn_refresh_move.pack(pady=5)

        self.move_combo = ctk.CTkComboBox(tab, width=300)
        self.move_combo.pack(pady=5)
        self.move_combo.set("")

        label_import = ctk.CTkLabel(tab, text="Ruta para importar distros:")
        label_import.pack(pady=5)

        self.new_import_entry = ctk.CTkEntry(tab, width=350)
        self.new_import_entry.pack(pady=5)

        btn_new_import = ctk.CTkButton(
            tab, text="Seleccionar carpeta", command=self.select_new_import_folder)
        btn_new_import.pack(pady=5)

        btn_move = ctk.CTkButton(
            tab, text="Mover Distro", command=self.move_distro)
        btn_move.pack(pady=10)

    def select_new_import_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.new_import_entry.delete(0, "end")
            self.new_import_entry.insert(0, folder)

    def refresh_installed_distros_move(self):
        try:
            result = subprocess.run(
                ["wsl", "--list"], capture_output=True, check=True)
            stdout_clean = result.stdout.decode(
                "utf-8", errors="replace").replace("\0", "")
            lines = stdout_clean.splitlines()
            distros = []
            for line in lines:
                line_clean = line.replace("\0", "")
                if line_clean.strip() == "" or "Windows Subsystem" in line_clean or "distro" in line_clean.lower():
                    continue
                distro_name = line_clean.replace("*", "").strip()
                if distro_name:
                    distros.append(distro_name)
            self.move_combo.configure(values=distros)
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros instaladas: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros instaladas: {str(e)}")

    def move_distro(self):
        distro = self.move_combo.get().replace("\0", "")
        if not distro:
            messagebox.showwarning(
                "Advertencia", "Seleccione una distro para mover.")
            return

        export_path = self.config.get("export_path", "").replace("\0", "")
        if not export_path:
            messagebox.showwarning(
                "Advertencia", "Configure la ruta para exportar distros en la pestaña de Configuración.")
            return

        import_path = self.new_import_entry.get().replace("\0", "")
        if not import_path:
            messagebox.showwarning(
                "Advertencia", "Seleccione la ruta para importar distros en esta pestaña.")
            return

        tar_file = os.path.join(export_path, f"{distro}-ex.tar")
        try:
            subprocess.run(["wsl", "--shutdown"], check=True)
            subprocess.run(["wsl", "--export", distro, tar_file], check=True)
            subprocess.run(["wsl", "--unregister", distro], check=True)
            dest_folder = os.path.join(import_path, distro)
            subprocess.run(["wsl", "--import", distro,
                           dest_folder, tar_file], check=True)
            messagebox.showinfo(
                "Mover Distro", f"La distro {distro} se movió correctamente a la ruta:\n{dest_folder}")
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror("Error", f"Error al mover la distro: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al mover la distro: {str(e)}")

    def create_local_move_tab(self):
        tab = self.tabview.tab("Mover Distro desde Archivo Local")

        btn_scan = ctk.CTkButton(
            tab, text="Buscar archivos exportados", command=self.scan_exported_files)
        btn_scan.pack(pady=5)

        self.local_files_combo = ctk.CTkComboBox(tab, width=300)
        self.local_files_combo.pack(pady=5)
        self.local_files_combo.set("")

        label_local_import = ctk.CTkLabel(
            tab, text="Ruta para importar distros:")
        label_local_import.pack(pady=5)

        self.local_import_entry = ctk.CTkEntry(tab, width=350)
        self.local_import_entry.pack(pady=5)

        btn_local_import = ctk.CTkButton(
            tab, text="Seleccionar carpeta", command=self.select_local_import_folder)
        btn_local_import.pack(pady=5)

        btn_move_local = ctk.CTkButton(
            tab, text="Mover Distro desde Archivo Local", command=self.move_distro_from_local_file)
        btn_move_local.pack(pady=10)

    def scan_exported_files(self):
        export_path = self.config.get("export_path", "").replace("\0", "")
        if not export_path:
            messagebox.showwarning(
                "Advertencia", "Configure la ruta para exportar distros en la pestaña de Configuración.")
            return
        try:
            files = [f for f in os.listdir(
                export_path) if f.lower().endswith("-ex.tar")]
            if not files:
                messagebox.showinfo(
                    "Información", "No se encontraron archivos exportados en la carpeta.")
            else:
                self.local_files_combo.configure(values=files)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al escanear archivos exportados: {str(e)}")

    def select_local_import_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.local_import_entry.delete(0, "end")
            self.local_import_entry.insert(0, folder)

    def move_distro_from_local_file(self):
        export_path = self.config.get("export_path", "").replace("\0", "")
        if not export_path:
            messagebox.showwarning(
                "Advertencia", "Configure la ruta para exportar distros en la pestaña de Configuración.")
            return
        tar_file_name = self.local_files_combo.get().replace("\0", "")
        if not tar_file_name:
            messagebox.showwarning(
                "Advertencia", "Seleccione un archivo exportado.")
            return
        tar_file = os.path.join(export_path, tar_file_name)
        import_path = self.local_import_entry.get().replace("\0", "")
        if not import_path:
            messagebox.showwarning(
                "Advertencia", "Seleccione la ruta para importar distros en esta pestaña.")
            return
        # Derivar el nombre de la distro eliminando el sufijo "-ex.tar"
        if tar_file_name.lower().endswith("-ex.tar"):
            distro_name = tar_file_name[:-7]
        else:
            distro_name = os.path.splitext(tar_file_name)[0]
        dest_folder = os.path.join(import_path, distro_name)
        try:
            cmd = ["wsl", "--import", distro_name, dest_folder, tar_file]
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Mover Distro desde Archivo Local",
                                f"La distro {distro_name} se movió correctamente a la ruta:\n{dest_folder}")
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror(
                "Error", f"Error al mover la distro desde archivo local: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al mover la distro desde archivo local: {str(e)}")

    def create_delete_tab(self):
        tab = self.tabview.tab("Eliminar Distro")

        btn_refresh_delete = ctk.CTkButton(
            tab, text="Actualizar lista de distros instaladas", command=self.refresh_installed_distros_delete)
        btn_refresh_delete.pack(pady=5)

        self.delete_combo = ctk.CTkComboBox(tab, width=300)
        self.delete_combo.pack(pady=5)
        self.delete_combo.set("")

        btn_delete = ctk.CTkButton(
            tab, text="Eliminar Distro", command=self.delete_distro)
        btn_delete.pack(pady=5)

        self.refresh_installed_distros_delete()

    def refresh_installed_distros_delete(self):
        try:
            result = subprocess.run(
                ["wsl", "--list"], capture_output=True, check=True)
            stdout_clean = result.stdout.decode(
                "utf-8", errors="replace").replace("\0", "")
            lines = stdout_clean.splitlines()
            distros = []
            for line in lines:
                line_clean = line.replace("\0", "")
                if line_clean.strip() == "" or "Windows Subsystem" in line_clean or "distro" in line_clean.lower():
                    continue
                distro_name = line_clean.replace("*", "").strip()
                if distro_name:
                    distros.append(distro_name)
            self.delete_combo.configure(values=distros)
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros instaladas: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al obtener la lista de distros instaladas: {str(e)}")

    def delete_distro(self):
        distro = self.delete_combo.get().replace("\0", "")
        if not distro:
            messagebox.showwarning(
                "Advertencia", "Seleccione una distro para eliminar.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la distro {distro}?"):
            return
        try:
            subprocess.run(["wsl", "--unregister", distro], check=True)
            messagebox.showinfo("Eliminar Distro",
                                f"La distro {distro} ha sido eliminada.")
            self.refresh_installed_distros_delete()
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(
                "utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror(
                "Error", f"Error al eliminar la distro: {err}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al eliminar la distro: {str(e)}")


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = WSLManager(root)
    root.mainloop()
