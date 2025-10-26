import pandas as pd

df= pd.read_csv("dataset.csv")

print("Validando datos")

duplicados= df.duplicated().sum()
if duplicados == 0:
    print("No hay filas duplicadas")
else:
    print(f"Se encontraron {duplicados} filas duplicadas")

def revisar_rangos(columna, minimo, maximo):
    fueraderango= df[(df[columna]< minimo)| (df[columna]> maximo)]
    if fueraderango.empty:
        print(f"{columna}: todos los valores están dentro de rango ({minimo}-{maximo}).")
    else:
        print(f"{columna}:{len(fueraderango)}valores fuera de rango  ({minimo}-{maximo}).")

revisar_rangos("CO2",20, 60 )
revisar_rangos("ruido", 30, 70 )
revisar_rangos("IAC",0.2, 1 )
revisar_rangos("temperatura",15, 35)
revisar_rangos("seguridad", 0.2,1)
revisar_rangos("impacto",0,100)

print("Resumen del dataset")
print(df.describe())
