import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

from analisis import analizar
from reporte import generar_pdf

columnas_detectadas = []
ruta_archivo_seleccionado = ""


def seleccionar_y_preparar_archivo():
    global ruta_archivo_seleccionado
    
    archivo = filedialog.askopenfilename(
        title="Seleccionar perfil del detector",
        filetypes=[("Archivos de texto/CSV", "*.txt *.csv"), ("Todos", "*.*")]
    )
    if not archivo:
        return
        
    ruta_archivo_seleccionado = archivo
    lbl_archivo.config(text=f"Archivo: {os.path.basename(archivo)}")
    
    try:
        try:
            df_temp = pd.read_csv(archivo, sep=',', engine='python', nrows=5)
        except:
            df_temp = pd.read_csv(archivo, sep=None, engine='python', nrows=5)
        # sacar la columna 'Unnamed' si existe
        df_temp = df_temp.loc[:, ~df_temp.columns.str.contains('^Unnamed')]

        columnas = list(df_temp.columns)
        
        # Cargar los nombres de las columnas en los menús desplegables
        combo_pos['values'] = columnas
        combo_dos['values'] = columnas
        
        # Pre-selección inteligente automática
        for i, col in enumerate(columnas):
            col_lower = str(col).lower()
            if any(k in col_lower for k in ['cm', 'mm', 'pos', 'dist', 'x']):
                combo_pos.current(i)
            if any(k in col_lower for k in ['cu', 'gy', 'dosis', 'dose', 'val', '%', 'roi']):
                combo_dos.current(i)
                
    except Exception as e:
        messagebox.showerror("Error de lectura", f"No se pudieron precargar las columnas del archivo:\n{str(e)}")
    

def ejecutar_analisis():
    if not ruta_archivo_seleccionado:
        messagebox.showwarning("Falta archivo", "Por favor, seleccione un archivo primero.")
        return
    # seleccionar los índices de las columnas según la selección del usuario
    idx_dos = combo_dos.current()
    idx_pos = combo_pos.current()
    if idx_pos == -1 or idx_dos == -1:
        messagebox.showwarning("Falta selección", "Por favor, asigne las columnas de Posición y Dosis.")
        return
    unidades_dist = combo_unidades.get()

    try:
        # Leer ahora sí el archivo completo
        try:
            df = pd.read_csv(ruta_archivo_seleccionado, sep=',', engine='python')
        except:
            df = pd.read_csv(ruta_archivo_seleccionado, sep=None, engine='python')

        # Limpiar Unnamed también en el archivo completo por seguridad
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Creamos el DataFrame 'perfil' definitivo con todos los datos numéricos
        perfil = pd.DataFrame({
            'pos': df.iloc[:, idx_pos].astype(float),
            'dos': df.iloc[:, idx_dos].astype(float)
        })
    
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error durante el análisis:\n{str(e)}")
    try:
        # Ejecutar el análisis flexible importado
        from analisis import analizar
        res = analizar(perfil, idx_pos=idx_pos, idx_dos=idx_dos, unidades_dist=unidades_dist)
        
        resultado_txt = (
            f"Tamaño de Campo (FWHM): {res['field_size']:.2f} cm\n"
            f"--------------------------------------------------\n"
            f"Planicidad = {res['planicidad']:.3f} %   --> "
            f"{'OK' if res['planicidad'] < 2.0 else 'REVISAR'}\n\n"
            
            f"Simetría Puntual Máx = {res['simetria']:.3f} %   --> "
            f"{'OK' if abs(res['simetria']) < 2.0 else 'REVISAR'}\n\n"
            
            f"Simetría por Áreas = {res['Sarea']:.3f} %   --> "
            f"{'OK' if abs(res['Sarea']) < 2.0 else 'REVISAR'}"
        )
        
        texto_resultado.delete("1.0", tk.END)
        texto_resultado.insert(tk.END, resultado_txt)

    # Generar reporte en PDF
        nombre_sugerido = "reporte_QA.pdf"
        
        pdf_file = filedialog.asksaveasfilename(
            title="Guardar Reporte PDF",
            initialfile=nombre_sugerido,       # Nombre por defecto
            defaultextension=".pdf",          
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        
        if not pdf_file:
            messagebox.showwarning("Análisis cancelado", "No se generó el reporte PDF porque no se seleccionó un destino.")
            return
        
        texto_notas = notas_input.get("1.0", tk.END).strip()

        pdf_file = generar_pdf(
            field_size= res['field_size'],
            planicidad=res['planicidad'], 
            simetria=res['simetria'], 
            Sarea=res['Sarea'], 
            img_plot=res['img_plot'], 
            notas= texto_notas,
            ruta_salida=pdf_file
        )

        messagebox.showinfo("PDF generado", f"Reporte guardado como:\n{pdf_file}")
        
        time.sleep(0.5) 
        if os.path.exists(res['img_plot']):
            os.remove(res['img_plot'])
    
    
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error durante el análisis:\n{str(e)}")



# --- CONSTRUCCIÓN DE LA INTERFAZ ---
root = tk.Tk()
root.title("QA - Planicidad y Simetria de Perfiles")
root.geometry("750x650")

#
btn_Cargar = tk.Button(root, text="1. Cargar Archivo", command=seleccionar_y_preparar_archivo, width=25)
btn_Cargar.pack(pady=5)

lbl_archivo = tk.Label(root, text="Archivo: Ninguno", font=("Arial", 10, "italic"))
lbl_archivo.pack()

# Panel de Configuración de Formato ---
frame_config = tk.LabelFrame(root, text=" Configuración del Formato del Detector ", padx=10, pady=10)
frame_config.pack(padx=15, pady=10, fill="x")

tk.Label(frame_config, text="Columna Posición:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
combo_pos = ttk.Combobox(frame_config, state="readonly", width=15)
combo_pos.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_config, text="Unidades:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
combo_unidades = ttk.Combobox(frame_config, values=["cm", "mm"], state="readonly", width=5)
combo_unidades.current(0)
combo_unidades.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_config, text="Columna Dosis:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
combo_dos = ttk.Combobox(frame_config, state="readonly", width=15)
combo_dos.grid(row=1, column=1, padx=5, pady=5)

# 
btn_Analizar = tk.Button(root, text="2. Calcular y Generar Reporte", command=ejecutar_analisis, width=25, bg="#d4edda")
btn_Analizar.pack(pady=5)


texto_resultado = tk.Text(root, width=80, height=11, font=("Consolas", 10))
texto_resultado.pack(padx=10, pady=5)

tk.Label(root, text="Notas del análisis (energía, lineal, observaciones):").pack()
notas_input = tk.Text(root, width=80, height=4)  
notas_input.pack(padx=10, pady=5)

root.mainloop()