import os
import datetime
from fpdf import FPDF

def generar_pdf(field_size, planicidad, simetria, Sarea, img_plot, notas, ruta_salida):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Reporte Planicidad y Simetría", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Resultados:", ln=True)



    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Tamaño de campo (FWHM): {field_size:.3f} cm", ln=True)
    pdf.cell(0, 10, f"Planicidad: {planicidad:.3f} %", ln=True)
    pdf.cell(0, 10, f"Simetría puntual: {simetria:.3f} %", ln=True)
    pdf.cell(0, 10, f"Simetría por areas: {Sarea:.3f} %", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Tolerancia: 2%, Nivel de Acción: 3%", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Planicidad: {'OK' if planicidad < 2 else 'REVISAR'}", ln=True)
    pdf.cell(0, 10, f"Simetría puntual: {'OK' if abs(simetria) < 2 else 'REVISAR'}", ln=True)
    pdf.cell(0, 10, f"Simetría por areas: {'OK' if abs(Sarea) < 2 else 'REVISAR'}", ln=True)
    pdf.ln(5)

    # Insertar Imagen
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Gráfico del perfil:", ln=True)
    pdf.image(img_plot, x=10, w=180)
    pdf.ln(5)

    # Insertar Notas
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Notas:", ln=True)
    pdf.set_font("Arial", "", 11)

    if notas:
        for linea in notas.split("\n"):
            pdf.multi_cell(0, 8, linea)
    else:
        pdf.cell(0, 10, "Sin notas", ln=True)   
    
    pdf.output(ruta_salida)
    
    return ruta_salida  