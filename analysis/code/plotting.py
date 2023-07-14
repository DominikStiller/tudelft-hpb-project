import os
from pathlib import Path
from typing import Union

import seaborn as sb
import matplotlib
import matplotlib.pyplot as plt


def set_plotting_theme():
    dark = plt.rcParams["figure.facecolor"] == "black"
    sb.set(
        context="paper",
        style="whitegrid",
        palette=[
            "#0C2340",
            "#A50034",
            "#00A6D6",
            "#EF60A3",
            "#FFB81C",
            "#EC6842",
            "#6F1D77",
            "#009B77",
        ],
        font_scale=1.7,
        font="sans-serif",
        rc={
            "font.family": "sans-serif",
            "lines.linewidth": 1.2,
            "font.sans-serif": "Lato",
            # "axes.titleweight": "bold",
            # "axes.labelweight": "light",
            # "font.weight": "light",
            "mathtext.default": "regular",
        },
    )
    if dark:
        # For example, due to VS Code dark theme
        plt.style.use("dark_background")


def save_plot(results_folder: Union[Path, str], name: str, fig=None, type="pdf"):
    if isinstance(results_folder, str):
        results_folder = Path(results_folder)

    plots_folder = "plots" / results_folder
    plots_folder.mkdir(parents=True, exist_ok=True)

    if fig is None:
        fig = plt.gcf()
    fig.savefig(
        os.path.join(plots_folder, f"{name}.{type}"),
        dpi=450,
        bbox_inches="tight",
        pad_inches=0.03,
    )


def format_plot(
    xlocator=None,
    ylocator=None,
    tight_layout=True,
    zeroline=False,
    xgrid=True,
    ygrid=True,
):
    fig = plt.gcf()
    for ax in fig.axes:
        if zeroline:
            ax.axhline(0, linewidth=1.5, c="black")

        xlocator_ax = xlocator
        if not xlocator_ax:
            if ax.get_xscale() == "log":
                xlocator_ax = matplotlib.ticker.LogLocator(
                    base=10, subs="auto", numticks=100
                )
            else:
                xlocator_ax = matplotlib.ticker.AutoMinorLocator()

        ylocator_ax = ylocator
        if not ylocator_ax:
            if ax.get_yscale() == "log":
                ylocator_ax = matplotlib.ticker.LogLocator(
                    base=10, subs="auto", numticks=100
                )
            else:
                ylocator_ax = matplotlib.ticker.AutoMinorLocator()

        ax.get_xaxis().set_minor_locator(xlocator_ax)
        ax.get_yaxis().set_minor_locator(ylocator_ax)

        if xgrid:
            ax.grid(visible=True, which="major", linewidth=1.0)
        if ygrid:
            ax.grid(visible=True, which="minor", linewidth=0.5, linestyle="-.")

    if tight_layout:
        fig.tight_layout(pad=0.1, h_pad=0.4, w_pad=0.4)


set_plotting_theme()
