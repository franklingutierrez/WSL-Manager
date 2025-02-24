#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WSL Manager – Script para administrar distribuciones WSL

Requisitos:
    - Python 3.x
    - Tkinter (incluido en la mayoría de instalaciones de Python)
    
Pasos previos:
    1. Crear un entorno virtual:
         python -m venv env
         env\Scripts\activate   (en Windows)
    2. Ejecutar este script desde el entorno virtual.

La aplicación permite:
    1. Configurar la ruta de exportación (usada en: wsl --export <Distro> <ruta>\distro-ex.tar)
    2. Configurar la ruta de importación (usada en: wsl --import <Distro> <ruta>\distro <archivo tar>)
    3. Consultar y guardar la configuración para uso posterior.
    4. Consultar las distribuciones disponibles en línea (wsl --list --online) e instalarlas.
    5. Listar las distribuciones instaladas (wsl --list) y ejecutarlas.
    6. Mover una distribución a otra ubicación usando:
           wsl --shutdown
           wsl --export <Distro> <export_path>\<Distro>-ex.tar
           wsl --unregister <Distro>
           wsl --import <Distro> <import_path>\<Distro> <export_path>\<Distro>-ex.tar

Consulta la documentación de Microsoft para WSL:
https://learn.microsoft.com/en-us/windows/wsl/
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import json
import os

CONFIG_FILE = 'config.json'

class WSLManager:
    def __init__(self, master):
        self.master = master
        master.title("WSL Manager")
        master.geometry("600x400")
        master.configure(bg="lightblue")
        
        self.load_config()
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')
        
        self.create_config_tab()
        self.create_install_tab()
        self.create_execute_tab()
        self.create_move_tab()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"export_path": "", "import_path": ""}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)
        messagebox.showinfo("Configuración", "¡Configuración guardada exitosamente!")

    def create_config_tab(self):
        self.config_frame = tk.Frame(self.notebook, bg="lightyellow")
        self.notebook.add(self.config_frame, text="Configuración")
        
        tk.Label(self.config_frame, text="Ruta para exportar distros:", bg="lightyellow", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.export_entry = tk.Entry(self.config_frame, width=50)
        self.export_entry.grid(row=0, column=1, padx=5, pady=5)
        self.export_entry.insert(0, self.config.get("export_path", ""))
        tk.Button(self.config_frame, text="Seleccionar carpeta", command=self.select_export_folder, bg="darkblue", fg="white").grid(row=0, column=2, padx=5)
        
        tk.Label(self.config_frame, text="Ruta para importar distros:", bg="lightyellow", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.import_entry = tk.Entry(self.config_frame, width=50)
        self.import_entry.grid(row=1, column=1, padx=5, pady=5)
        self.import_entry.insert(0, self.config.get("import_path", ""))
        tk.Button(self.config_frame, text="Seleccionar carpeta", command=self.select_import_folder, bg="darkblue", fg="white").grid(row=1, column=2, padx=5)
        
        tk.Button(self.config_frame, text="Guardar Configuración", command=self.update_config, bg="green", fg="white", font=("Arial", 10, "bold")).grid(row=2, column=1, pady=10)

    def select_export_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.export_entry.delete(0, tk.END)
            self.export_entry.insert(0, folder)

    def select_import_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.import_entry.delete(0, tk.END)
            self.import_entry.insert(0, folder)

    def update_config(self):
        self.config["export_path"] = self.export_entry.get().replace("\0", "")
        self.config["import_path"] = self.import_entry.get().replace("\0", "")
        self.save_config()

    def create_install_tab(self):
        self.install_frame = tk.Frame(self.notebook, bg="lightgreen")
        self.notebook.add(self.install_frame, text="Instalar Distro")
        
        tk.Button(self.install_frame, text="Actualizar lista de distros online", command=self.refresh_online_distros, bg="blue", fg="white").pack(pady=5)
        self.online_combo = ttk.Combobox(self.install_frame, width=40)
        self.online_combo.pack(pady=5)
        tk.Button(self.install_frame, text="Instalar Distro", command=self.install_distro, bg="purple", fg="white").pack(pady=5)
        
        self.online_list = []
        self.refresh_online_distros()

    def refresh_online_distros(self):
        try:
            # Ejecuta el comando y limpia la salida de posibles caracteres nulos
            result = subprocess.run(["wsl", "--list", "--online"], capture_output=True, check=True)
            stdout_clean = result.stdout.decode("utf-8", errors="replace").replace("\0", "")
            lines = stdout_clean.splitlines()
            distros = []
            for line in lines:
                line_clean = line.replace("\0", "")
                parts = line_clean.split()
                if parts:
                    # Omitir encabezados (ajusta según la salida)
                    if parts[0].lower() in ['name', 'distribucion']:
                        continue
                    distros.append(parts[0])
            self.online_list = distros
            self.online_combo['values'] = distros
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode("utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror("Error", f"Error al obtener la lista de distros online: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener la lista de distros online: {str(e)}")

    def install_distro(self):
        # Sanitizamos la cadena para eliminar caracteres nulos
        distro = self.online_combo.get().replace("\0", "")
        if not distro:
            messagebox.showwarning("Advertencia", "Seleccione una distro para instalar.")
            return
        try:
            cmd = ["wsl", "--install", "-d", distro]
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Instalar Distro", f"La instalación de {distro} ha comenzado.")
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode("utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror("Error", f"Error al instalar la distro: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al instalar la distro: {str(e)}")

    def create_execute_tab(self):
        self.execute_frame = tk.Frame(self.notebook, bg="lightcyan")
        self.notebook.add(self.execute_frame, text="Ejecutar Distro")
        
        tk.Button(self.execute_frame, text="Actualizar lista de distros instaladas", command=self.refresh_installed_distros, bg="blue", fg="white").pack(pady=5)
        self.installed_combo = ttk.Combobox(self.execute_frame, width=40)
        self.installed_combo.pack(pady=5)
        tk.Button(self.execute_frame, text="Ejecutar Distro", command=self.execute_distro, bg="orange", fg="white").pack(pady=5)
        self.refresh_installed_distros()

    def refresh_installed_distros(self):
        try:
            result = subprocess.run(["wsl", "--list"], capture_output=True, check=True)
            stdout_clean = result.stdout.decode("utf-8", errors="replace").replace("\0", "")
            lines = stdout_clean.splitlines()
            distros = []
            for line in lines:
                line_clean = line.replace("\0", "")
                if line_clean.strip() == "" or "Windows Subsystem" in line_clean or "distro" in line_clean.lower():
                    continue
                distro_name = line_clean.replace("*", "").strip()
                if distro_name:
                    distros.append(distro_name)
            self.installed_combo['values'] = distros
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode("utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror("Error", f"Error al obtener la lista de distros instaladas: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener la lista de distros instaladas: {str(e)}")

    def execute_distro(self):
        distro = self.installed_combo.get().replace("\0", "")
        if not distro:
            messagebox.showwarning("Advertencia", "Seleccione una distro para ejecutar.")
            return
        try:
            # Este comando requiere abrir la terminal de Windows; usamos shell=True para ejecutar la cadena completa.
            cmd = f'start cmd /k wsl -d {distro}'
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar la distro: {str(e)}")

    def create_move_tab(self):
        self.move_frame = tk.Frame(self.notebook, bg="lavender")
        self.notebook.add(self.move_frame, text="Mover Distro")
        
        tk.Button(self.move_frame, text="Actualizar lista de distros instaladas", command=self.refresh_installed_distros_move, bg="blue", fg="white").pack(pady=5)
        self.move_combo = ttk.Combobox(self.move_frame, width=40)
        self.move_combo.pack(pady=5)
        tk.Button(self.move_frame, text="Mover Distro", command=self.move_distro, bg="red", fg="white").pack(pady=5)

    def refresh_installed_distros_move(self):
        try:
            result = subprocess.run(["wsl", "--list"], capture_output=True, check=True)
            stdout_clean = result.stdout.decode("utf-8", errors="replace").replace("\0", "")
            lines = stdout_clean.splitlines()
            distros = []
            for line in lines:
                line_clean = line.replace("\0", "")
                if line_clean.strip() == "" or "Windows Subsystem" in line_clean or "distro" in line_clean.lower():
                    continue
                distro_name = line_clean.replace("*", "").strip()
                if distro_name:
                    distros.append(distro_name)
            self.move_combo['values'] = distros
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode("utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror("Error", f"Error al obtener la lista de distros instaladas: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener la lista de distros instaladas: {str(e)}")

    def move_distro(self):
        distro = self.move_combo.get().replace("\0", "")
        if not distro:
            messagebox.showwarning("Advertencia", "Seleccione una distro para mover.")
            return
        export_path = self.config.get("export_path", "").replace("\0", "")
        import_path = self.config.get("import_path", "").replace("\0", "")
        if not export_path or not import_path:
            messagebox.showwarning("Advertencia", "Configure las rutas de exportación e importación en la pestaña de Configuración.")
            return
        
        tar_file = os.path.join(export_path, f"{distro}-ex.tar")
        try:
            subprocess.run(["wsl", "--shutdown"], check=True)
            subprocess.run(["wsl", "--export", distro, tar_file], check=True)
            subprocess.run(["wsl", "--unregister", distro], check=True)
            dest_folder = os.path.join(import_path, distro)
            subprocess.run(["wsl", "--import", distro, dest_folder, tar_file], check=True)
            messagebox.showinfo("Mover Distro", f"La distro {distro} se movió correctamente.")
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode("utf-8", errors="replace").replace("\0", "") if e.stderr else ""
            messagebox.showerror("Error", f"Error al mover la distro: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al mover la distro: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WSLManager(root)
    root.mainloop()
