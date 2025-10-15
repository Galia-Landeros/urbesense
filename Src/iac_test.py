from pathlib import Path 
import pandas as pd
import sys

base = Path(__file__).resolve().parent.parent
csv_path = base /"data" / "dataprueba.csv"

print("resolved csv path:", csv_path)
if not csv_path.exists():
    print("file does not exist:", csv_path)
    sys.exit(1)

df = pd.read_csv(csv_path)

df["IAC"] = (
    0.3 * df["co2"] / df["co2"].max() +
    0.3 * df["ruido"] / df["ruido"].max() +
    0.3 * df["movimiento"] / df["movimiento"].max()+
    0.1 * df["temperatura"] / df["temperatura"].max()
)

print(df)
