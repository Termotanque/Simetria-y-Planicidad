import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time

# Funciones auxiliares
from analisis import analizar
from reporte import generar_pdf

def ejecutar_analisis():
    texto_notas = notas_input.get("1.0", tk.END).strip()
    archivo = filedialog.askopenfilename(
        title="Seleccionar perfil",
        filetypes=[
            ("Archivos de texto", "*.txt"),
            ("CSV", "*.csv"),
            ("Todos", "*.*")
        ]
    )

    if not archivo:
        return

    try:
        # 1. Procesar el perfil con analisis.py
        res = analizar(archivo)
        
        # 2. Actualizar el cuadro de texto con resultados
        resultado_txt = (
            f"Archivo: {os.path.basename(archivo)}\n"
            f"Tamaño de Campo (FWHM): {res['field_size']:.2f} cm\n"
            f"--------------------------------------------------\n"
            f"Planicidad = {res['planicidad']:.3f} %   --> "
            f"{'OK' if res['planicidad'] < 2.0 else 'REVISAR'}\n\n"
            
            f"Simetría Puntual Máx = {res['simetria_puntual_max']:.3f} %   --> "
            f"{'OK' if abs(res['simetria_puntual_max']) < 2.0 else 'REVISAR'}\n\n"
            
            f"Simetría por Áreas = {res['Sarea']:.3f} %   --> "
            f"{'OK' if abs(res['Sarea']) < 2.0 else 'REVISAR'}"
        )
        
        texto_resultado.delete("1.0", tk.END)
        texto_resultado.insert(tk.END, resultado_txt)

# 3.  guardar el PDF
        nombre_sugerido = os.path.basename(archivo).replace(".csv", "").replace(".txt", "") + "_reporte_QA.pdf"
        
        pdf_file = filedialog.asksaveasfilename(
            title="Guardar Reporte PDF",
            initialfile=nombre_sugerido,       # Nombre por defecto
            defaultextension=".pdf",          
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        
        if not pdf_file:
            messagebox.showwarning("Análisis cancelado", "No se generó el reporte PDF porque no se seleccionó un destino.")
            return

        # 3. Generar el reporte PDF 
        pdf_file = generar_pdf(
            archivo=archivo,
            field_size= res['field_size'],
            planicidad=res['planicidad'], 
            simetria=res['simetria_puntual_max'], 
            Sarea=res['Sarea'], 
            img_plot=res['img_plot'], 
            notas=texto_notas,
            ruta_salida=pdf_file
        )

        messagebox.showinfo("PDF generado", f"Reporte guardado como:\n{pdf_file}")
        
        
        time.sleep(0.5) 
        if os.path.exists(res['img_plot']):
            os.remove(res['img_plot'])
    
    except KeyError as ke:
        messagebox.showerror("Error de Clave", f"Falta un dato devuelto por el análisis: {str(ke)}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error durante el análisis:\n{str(e)}")


# -------------------
#  GUI
# -------------------
root = tk.Tk()
root.title("QA - Planicidad y Simetría")
root.geometry("700x550")

tk.Label(
    root,
    text="Análisis de perfil - Simetría y Planicidad",
    font=("Arial", 12, "bold")
).pack(pady=10)

tk.Button(
    root,
    text="Seleccionar archivo y analizar",
    command=ejecutar_analisis,
    width=30,
    bg="#e1e1e1"
).pack(pady=10)

texto_resultado = tk.Text(root, width=80, height=12, font=("Consolas", 10))
texto_resultado.pack(padx=10, pady=10)

tk.Label(root, text="Notas del análisis (plan, detector, observaciones):").pack()

notas_input = tk.Text(root, width=80, height=5)
notas_input.pack(padx=10, pady=5)

root.mainloop()
