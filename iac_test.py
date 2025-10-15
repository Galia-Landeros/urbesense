
import pandas as pd

df = pd.read_csv("data_zonas.csv")

df["IAC"] = (
    0.3 * df["co2"] / df["co2"].max() +
    0.3 * df["ruido"] / df["ruido"].max() +
    0.3 * df["movimiento"] / df["movimiento"].max()+
    0.1 * df["temperatura"] / df["temperatura"].max()
)

print(df)
