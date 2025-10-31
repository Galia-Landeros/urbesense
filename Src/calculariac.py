import pandas as pd
import random

zonas=["Zona 1", "Zona 2", "Zona 3", "Zona 4", "Zona 5"]

w1, w2, w3, w4 = 0.3, 0.3, 0.3, 0.1

def calcular_iac(co2, ruido, temp, seguridad):
    co2_norm = (co2 - 20)/ (60 -20)
    ruido_norm= (ruido -30) / (70-30)
    temp_norm= (temp - 15) / (35 - 15)
    iac= w1*co2_norm + w2*ruido_norm + w3*temp_norm + w4*seguridad
    return round (iac,2)

def calcular_impacto(iac, seguridad):
    return round((1-((iac+seguridad)/2))*100,2)

data=[]

for zona in zonas:
    co2 = random.randint(20,60)
    ruido= random.randint(30,70)
    temp =random.randint (15, 35)
    seguridad = round(random.uniform(0.2,1),2)

    iac= calcular_iac(co2, ruido, temp, seguridad)
    impacto= calcular_impacto(iac,seguridad)

    data.append([zona, co2, ruido, temp,seguridad,iac,impacto])

df= pd.DataFrame(data, columns=["zona", "CO2", "ruido","temperatura","seguridad","IAC","impacto"])

df.to_csv("dataset_simulacion.csv", index=False)

print("csv generado correctamente")
print (df)

