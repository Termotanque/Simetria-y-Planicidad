import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analizar(perfil, idx_pos=0, idx_dos=1, unidades_dist="cm"):
    
    if unidades_dist == "mm":
        perfil['pos'] = perfil['pos'] * 0.1
    # Ordenar por posicion
    perfil = perfil.sort_values(by='pos').reset_index(drop=True)    
    # Valor central
    idx_centro = (perfil['pos'] - 0).abs().idxmin()
    val_cent = perfil.loc[idx_centro, 'dos']
    x_cent = perfil.loc[idx_centro, 'pos']

    # Tamaño del campo geométrico (FWHM al 50 % de la dosis)
    perfil_FWHM = perfil[perfil['dos'] >= (val_cent * 0.5)]
    field_size = np.abs(perfil_FWHM['pos'].iloc[0]) + np.abs(perfil_FWHM['pos'].iloc[-1])

    # -------------------
    # Planicidad
    # -------------------
    umbral_plan = (field_size / 2) * 0.8
    perfil_plan = perfil[np.abs(perfil['pos']) <= umbral_plan]

    Dmax = np.max(perfil_plan['dos'])
    Dmin = np.min(perfil_plan['dos'])
    planicidad = 100 * (Dmax - Dmin) / (Dmax + Dmin)

    # -------------------
    # Simetría puntual
    # -------------------
    puntos_positivos = perfil_plan[perfil_plan['pos'] > 0]
    lista_asimetrias = []

    for _, fila in puntos_positivos.iterrows():
        cm_pos = fila['pos']
        dosis_pos = fila['dos']
        
        # Buscar el punto simétrico más cercano en el lado negativo (-cm)
        idx_simetrico = (perfil_plan['pos'] - (-cm_pos)).abs().idxmin()
        dosis_neg = perfil_plan.loc[idx_simetrico, 'dos']
        
        # Guardar la asimetría puntual de este par de puntos
        asimetria_punto = (abs(dosis_pos - dosis_neg) / val_cent) * 100
        lista_asimetrias.append(asimetria_punto)

    simetria_puntual_max = np.max(lista_asimetrias) if lista_asimetrias else 0.0

    # -------------------
    # Simetría por áreas
    # -------------------
    # Para la simetría por áreas del 80%
    mitad = len(perfil_plan) // 2

    area_izq = np.trapz(
        perfil_plan['dos'].iloc[:mitad],
        perfil_plan['pos'].iloc[:mitad]
    )
    area_der = np.trapz(
        perfil_plan['dos'].iloc[mitad:],
        perfil_plan['pos'].iloc[mitad:]
    )

    Sarea = 100 * (abs(area_izq) - abs(area_der)) / (abs(area_izq) + abs(area_der))

    # -------------------
    # Gráfico
    # -------------------
    plt.figure(figsize=(8, 5))
    plt.plot(perfil['pos'], perfil['dos'], label='Perfil')

    plt.plot(x_cent, val_cent, '.', markersize=12, label=f'Central = {val_cent:.2f} CU')
    
    plt.axvline(-umbral_plan, linestyle='--', color='red', alpha=0.7)
    plt.axvline(umbral_plan, linestyle='--', color='red', alpha=0.7)

    plt.fill_between(
        perfil_plan['pos'],
        perfil_plan['dos'],
        alpha=0.3,
        label='Zona 80%'
    )

    plt.xlabel('pos')
    plt.ylabel('dos')
    plt.title('Perfil analizado')
    plt.grid(True)
    plt.legend()

    img_plot = "perfil_analizado_grafico.png"
    plt.savefig(img_plot, dpi=200, bbox_inches="tight")
    plt.close()

    # resultados en un diccionario 
    return {
        "planicidad": planicidad,
        "simetria": simetria_puntual_max,
        "Sarea": Sarea,
        "img_plot": img_plot, 
        "field_size": field_size
    }