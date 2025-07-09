import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel, StringVar, OptionMenu
import pandas as pd
import random
import os
from datetime import datetime

# -----------------------------------
# Variable global que contiene los nombres de ganadores excluidos durante la sesión actual
excluir_ganadores = set()

# -----------------------------------
# Creamos el nombre del archivo donde se guardarán todos los sorteos de esta sesión
session_start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Timestamp para nombrar el archivo
session_filename = f"sorteo_{session_start_time}.txt"             # Nombre del archivo txt único por sesión
os.makedirs("resultados", exist_ok=True)                           # Creamos carpeta resultados si no existe
session_filepath = os.path.join("resultados", session_filename)    # Ruta completa del archivo

# -----------------------------------
# Función para verificar si un valor es numérico (int o float)
def is_number(value):
    try:
        float(value)
        return True
    except:
        return False

# -----------------------------------
# Filtra columnas del dataframe que contienen datos no numéricos (ejemplo: nombres)
def filter_valid_colums(df):
    valid_columns = []
    for col in df.columns:
        serie = df[col].dropna()  # Quitamos valores NaN para no afectar la validación
        if len(serie) == 0:
            continue  # Saltar columnas vacías
        # Comprobamos si la columna contiene algún dato NO numérico
        if serie.apply(lambda x: not is_number(x)).any():
            valid_columns.append(col)  # Si contiene, es columna válida para nombres
    return valid_columns

# -----------------------------------
# Ventana para que el usuario seleccione la columna que contiene los nombres
def ask_column_name(columns, root):
    placeholder = "-- Selecciona una columna --"
    selected_column = None

    def on_close():
        root.quit()
        root.destroy()

    # Loop para que el usuario seleccione una columna válida
    while selected_column is None:
        top = Toplevel(root)  # Nueva ventana emergente
        top.title("Seleccionar columna")
        top.protocol("WM_DELETE_WINDOW", on_close)

        tk.Label(top, text="Selecciona la columna que contiene los nombres:").pack(pady=10)

        var = StringVar(top)
        var.set(placeholder)

        options = [placeholder] + columns
        dropdown = OptionMenu(top, var, *options)  # Desplegable con columnas
        dropdown.pack(pady=5)

        # Botón Aceptar que valida la selección
        def submit():
            choice = var.get()
            if choice == placeholder:
                messagebox.showerror("Error", "Debes seleccionar una columna válida.", parent=top)
            else:
                nonlocal selected_column
                selected_column = choice
                top.destroy()  # Cierra ventana si hay selección válida

        tk.Button(top, text="Aceptar", command=submit).pack(pady=10)

        top.grab_set()    # Evita interacción con ventana principal mientras está abierta
        top.wait_window() # Espera a que se cierre la ventana para continuar

    return selected_column

# -----------------------------------
# Solicita al usuario la cantidad de nombres a seleccionar para el sorteo
def ask_number(max_value, root):
    while True:
        count_str = simpledialog.askstring(
            "Cantidad", f"¿Cuántos nombres deseas seleccionar? (Máximo {max_value}):", parent=root
        )
        if count_str is None:
            return None  # Usuario canceló
        try:
            count = int(count_str)
            if count <= 0:
                raise ValueError  # No permitimos números menores o iguales a 0
            if count > max_value:
                messagebox.showerror("Error", f"Solo hay {max_value} nombres disponibles.", parent=root)
            else:
                return count  # Cantidad válida
        except ValueError:
            messagebox.showerror("Error", "Debes ingresar un número válido y mayor a 0.", parent=root)

# -----------------------------------
# Pregunta al usuario si quiere excluir los ganadores anteriores del sorteo actual
def ask_exclusion_option(root):
    respuesta = messagebox.askyesno("Excluir ganadores anteriores", "¿Deseas excluir a los ganadores del sorteo anterior?")
    return respuesta

# -----------------------------------
# Función principal que controla la selección de archivo CSV y proceso del sorteo
def select_file_and_process(root):
    global excluir_ganadores, session_filepath

    # Abrimos un diálogo para seleccionar archivo CSV
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo CSV",
        filetypes=[("Archivos CSV", "*.csv")],
        parent=root
    )
