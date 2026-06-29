import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analizar(archivo):
    perfil = pd.read_csv(archivo)
    perfil = perfil[['cm', 'CU']].sort_values(by='cm').reset_index(drop=True)

    # Valor central
    idx_centro = (perfil['cm'] - 0).abs().idxmin()

    # CORRECCIÓN: Usamos .loc para mezclar el índice de fila con el nombre string de la columna
    val_cent = perfil.loc[idx_centro, 'CU']
    x_cent = perfil.loc[idx_centro, 'cm']

    # Tamaño del campo geométrico (FWHM al 50 % de la dosis)
    perfil_FWHM = perfil[perfil['CU'] >= (val_cent * 0.5)]
    field_size = np.abs(perfil_FWHM['cm'].iloc[0]) + np.abs(perfil_FWHM['cm'].iloc[-1])

    # -------------------
    # Planicidad
    # -------------------
    umbral_plan = (field_size / 2) * 0.8
    perfil_plan = perfil[np.abs(perfil['cm']) <= umbral_plan]

    Dmax = np.max(perfil_plan['CU'])
    Dmin = np.min(perfil_plan['CU'])
    planicidad = 100 * (Dmax - Dmin) / (Dmax + Dmin)

    # -------------------
    # Simetría puntual
    # -------------------
    puntos_positivos = perfil_plan[perfil_plan['cm'] > 0]
    lista_asimetrias = []

    for _, fila in puntos_positivos.iterrows():
        cm_pos = fila['cm']
        dosis_pos = fila['CU']
        
        # Buscar el punto simétrico más cercano en el lado negativo (-cm)
        idx_simetrico = (perfil_plan['cm'] - (-cm_pos)).abs().idxmin()
        dosis_neg = perfil_plan.loc[idx_simetrico, 'CU']
        
        # Guardar la asimetría puntual de este par de puntos
        asimetria_punto = (abs(dosis_pos - dosis_neg) / val_cent) * 100
        lista_asimetrias.append(asimetria_punto)

    simetria_puntual_max = np.max(lista_asimetrias) if lista_asimetrias else 0.0

    # -------------------
    # Simetría por áreas
    # -------------------
    # Para la simetría por áreas del 80%, usamos el mismo perfil_plan (que ya está acotado al área útil)
    mitad = len(perfil_plan) // 2

    area_izq = np.trapz(
        perfil_plan['CU'].iloc[:mitad],
        perfil_plan['cm'].iloc[:mitad]
    )
    area_der = np.trapz(
        perfil_plan['CU'].iloc[mitad:],
        perfil_plan['cm'].iloc[mitad:]
    )

    Sarea = 100 * (abs(area_izq) - abs(area_der)) / (abs(area_izq) + abs(area_der))

    # -------------------
    # Generación del Gráfico
    # -------------------
    plt.figure(figsize=(8, 5))
    plt.plot(perfil['cm'], perfil['CU'], label='Perfil')

    # CORRECCIÓN: Usamos las variables x_cent y val_cent que ya calculamos correctamente arriba
    plt.plot(x_cent, val_cent, '.', markersize=12, label=f'Central = {val_cent:.2f} CU')
    
    plt.axvline(-umbral_plan, linestyle='--', color='red', alpha=0.7)
    plt.axvline(umbral_plan, linestyle='--', color='red', alpha=0.7)

    plt.fill_between(
        perfil_plan['cm'],
        perfil_plan['CU'],
        alpha=0.3,
        label='Zona 80%'
    )

    plt.xlabel('cm')
    plt.ylabel('CU')
    plt.title('Perfil analizado')
    plt.grid(True)
    plt.legend()

    nombre_base = os.path.basename(archivo).replace(".csv", "").replace(".txt", "")
    img_plot = f"{nombre_base}_grafico.png"
    plt.savefig(img_plot, dpi=200, bbox_inches="tight")
    plt.close()

    # resultados en un diccionario 
    return {
        "planicidad": planicidad,
        "simetria_puntual_max": simetria_puntual_max,
        "Sarea": Sarea,
        "img_plot": img_plot,
        "field_size": field_size
    }