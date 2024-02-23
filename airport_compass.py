import os
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

TOP_AIRPORTS: Final[int] = 30

# Getting airlines routes data:
routes = pd.read_csv(
    "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat",
    usecols=[0, 2, 4],
    names=["airline", "origin", "destination"],
)

# Selecting only top airports
top_airports = (
    routes.groupby("origin")
    .destination.count()
    .sort_values(ascending=False)
    .index[:TOP_AIRPORTS]
)

routes = routes.loc[routes.origin.isin(top_airports)]
# Getting airports data:
airports = pd.read_csv(
    "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv",
    usecols=["ident", "iata_code", "latitude_deg", "longitude_deg"],
)

# Merging routes with airports info:
df = routes
for direction in ("origin", "destination"):
    df = df.merge(
        airports.rename(columns=lambda x: x + f"_{direction}"),
        left_on=direction,
        right_on=f"iata_code_{direction}",
        how="left",
    )

# Getting initial bearing for each route:
df["angle"] = np.degrees(
    np.arctan2(
        df.latitude_deg_destination - df.latitude_deg_origin,
        df.longitude_deg_destination - df.longitude_deg_origin,
    )
)
# Aggregating final data:
res = df.groupby(["origin", "angle"]).destination.count()


# Plotting
plt.rcParams["font.sans-serif"] = "Roboto"
p = Path(f'/home/{os.getenv("USER")}/.local/share/fonts')
font_paths = list(p.glob("Roboto*.ttf"))
for font_path in font_paths:
    font_manager.fontManager.addfont(font_path)


plt.style.use("theme.mplstyle")
ncols = 5
nrows = len(top_airports) // ncols
fig, axes = plt.subplots(
    nrows=nrows,
    ncols=ncols,
    subplot_kw=dict(projection="polar"),
    figsize=(ncols * 1.9, nrows * 2.6),
)


for ax, airport in zip(axes.flatten(), top_airports):
    airport_data = res.loc[airport]
    ax.bar(
        np.radians(airport_data.index),
        airport_data.values,
        width=0.3,
        color="C2",
        alpha=0.5,
    )

    ax.set_title(f"{airport}\n", fontdict=dict(fontweight="bold"))
    ax.set_yticks([])
    ax.set_rlabel_position(90)
    ax.set_xticklabels(["E", "", "N", "", "W", "", "S", ""], fontdict=dict(fontsize=10))


fig.suptitle("Where is the traffic going?", fontsize=25, fontweight="bold")
fig.text(0.05, 0.005, "Made by Luciano Scarpulla")
fig.tight_layout(pad=3)
fig.savefig(f"Where is it going {TOP_AIRPORTS}.png", dpi=300)
