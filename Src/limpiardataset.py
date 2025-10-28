import pandas as pd

def leer_datos(ruta):
    """
    Lee un archivo csv y devuelve un dataframe a pandas
    """
    print("Leyendo datos desde", ruta)
    df=pd.read_csv(ruta)
    print("Datos cargados correctamente. Filas:", len(df))
    return df

def limpiar_datos(df):
    """
    Limpia el dataset:
    - Elimina duplicados
    - Rellena valores nulos
    - Verifica que las columnas estén en rango
    """
    print("Limpiando datos")

    df=df.drop_duplicates()

    df=df.dropna()

    limites= {
        "CO2": (20, 60),
        "ruido" : (30, 70),
        "IAC": (0.2, 1.0),
        "temperatura": (15, 35),
        "seguridad": (0.2, 1.0),
        "impacto": (0, 100)
    }

    for col, (min_val, max_val) in limites.items():
        if col in df.columns:
            df= df[(df[col] >= min_val) & (df[col] <= max_val)]

    print ("Datos limpios. Filas finales:", len(df))
    return df


def procesar_dataset(ruta):
    df=leer_datos(ruta)
    df_limpio=limpiar_datos(df)
    return df_limpio



if __name__ == "__main__":
    ruta= "data/dataset.csv"
    datos_finales = procesar_dataset(ruta)
    print ("\n Resumen del dataset limpio:")
    print (datos_finales.describe())