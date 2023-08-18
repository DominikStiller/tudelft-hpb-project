import os
from pathlib import Path
from typing import Union

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sb


def set_plotting_theme(force_light=False):
    dark = plt.rcParams["figure.facecolor"] == "black"
    if force_light:
        dark = False

    plt.style.use("default")
    sb.set(
        context="paper",
        style="white",
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
            "font.sans-serif": "Nimbus Sans",
            # "axes.titleweight": "bold",
            # "axes.labelweight": "light",
            # "font.weight": "light",
            # "mathtext.default": "regular",
            "figure.figsize": (12, 3),
            "axes.axisbelow": False,
            "xtick.bottom": True,
            "ytick.left": True,
            "xtick.top": True,
            "ytick.right": True,
            "xtick.minor.bottom": False,
            "ytick.minor.left": False,
            "xtick.minor.top": False,
            "ytick.minor.right": False,
            "xtick.direction": "in",
            "ytick.direction": "in",
        },
    )

    if dark:
        # For example, due to VS Code dark theme
        plt.style.use("dark_background")


def save_plot(plots_folder: Union[Path, str], name: str, fig=None, type="pdf"):
    if isinstance(plots_folder, str):
        plots_folder = Path(plots_folder)

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
    x_major_locator=None,
    y_major_locator=None,
    x_minor_locator=None,
    y_minor_locator=None,
    tight_layout=True,
    zeroline=False,
    major_grid=False,
    minor_grid=False,
):
    fig = plt.gcf()
    for ax in fig.axes:
        if hasattr(ax, "_colorbar"):
            continue

        if zeroline:
            ax.axhline(0, linewidth=1.5, c="black")

        x_major_locator_ax = x_major_locator
        if not x_major_locator_ax:
            if ax.get_xscale() == "log":
                x_major_locator_ax = matplotlib.ticker.LogLocator()
            else:
                x_major_locator_ax = matplotlib.ticker.AutoLocator()

        y_major_locator_ax = y_major_locator
        if not y_major_locator_ax:
            if ax.get_yscale() == "log":
                y_major_locator_ax = matplotlib.ticker.LogLocator()
            else:
                y_major_locator_ax = matplotlib.ticker.AutoLocator()

        ax.get_xaxis().set_major_locator(x_major_locator_ax)
        ax.get_yaxis().set_major_locator(y_major_locator_ax)

        x_minor_locator_ax = x_minor_locator
        if not x_minor_locator_ax:
            if ax.get_xscale() == "log":
                x_minor_locator_ax = matplotlib.ticker.LogLocator(
                    base=10, subs="auto", numticks=100
                )
            else:
                x_minor_locator_ax = matplotlib.ticker.AutoMinorLocator()

        y_minor_locator_ax = y_minor_locator
        if not y_minor_locator_ax:
            if ax.get_yscale() == "log":
                y_minor_locator_ax = matplotlib.ticker.LogLocator(
                    base=10, subs="auto", numticks=100
                )
            else:
                y_minor_locator_ax = matplotlib.ticker.AutoMinorLocator()

        ax.get_xaxis().set_minor_locator(x_minor_locator_ax)
        ax.get_yaxis().set_minor_locator(y_minor_locator_ax)

        if major_grid:
            ax.grid(visible=True, which="major", linewidth=1.0, linestyle="-.")
            ax.set_axisbelow(True)
        if minor_grid:
            ax.grid(visible=True, which="minor", linewidth=0.5, linestyle=":")

    if tight_layout:
        fig.tight_layout(pad=0.1, h_pad=0.4, w_pad=0.4)


set_plotting_theme()
