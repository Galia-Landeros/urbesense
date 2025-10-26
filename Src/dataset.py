import pandas as pd
import random
from datetime import datetime

zonas= ["Zona 1", "Zona 2", "Zona 3", "Zona 4" , "Zona 5"]

data = []
for zona in zonas:
    CO2 = random.randint(20, 60)
    ruido = random.randint(30, 70)
    IAC = round(random.uniform(0.2, 1.0), 2)
    temperatura = random.randint(15, 35)  # °C
    seguridad=round(random.uniform(0.2, 1.0), 2)
    impacto=round((1-((IAC+seguridad)/2))*100, 2)

    data.append([zona, CO2, ruido, IAC, temperatura, seguridad, impacto])
#Dataframe
df= pd.DataFrame(data, columns=["zona","CO2" , "ruido", "IAC", "temperatura", "seguridad", "impacto"])

def clasificar_impacto(valor):
    if valor < 20:
        return "Muy bajo"
    elif valor < 40:
        return "Bajo"
    elif valor < 60:
        return "Moderado"
    elif valor < 80:
        return "Alto"
    else:
        return "Muy alto"
    
df["nivel de impacto"] = df ["impacto"].apply(clasificar_impacto)

df.to_csv("dataset.csv", index=False)

print ("dataset generado correcto")
print(df)


#import streamlit as st