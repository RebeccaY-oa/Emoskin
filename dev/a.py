import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pathlib

parent_path = pathlib.Path(__file__).parent.parent

data = pd.read_excel(parent_path / "Results" / "fixations_by_shade.xlsx")

data = data.sort_values("count", ascending=False)

plt.figure()
plt.scatter(data["count"], data["Moyenne de Fixation count"])
plt.plot()
plt.show()
plt.savefig(parent_path / "Results" / "test.png")
