import os

import seaborn as sb
import matplotlib
import matplotlib.pyplot as plt


sb.set(
    context="paper",
    style="ticks",
    font_scale=1.6,
    font="sans-serif",
    rc={
        "lines.linewidth": 1.2,
        "axes.titleweight": "bold",
    },
)


def save_plot(results_folder: str, name: str, fig=None, type="pdf"):
    plots_folder = os.path.join(results_folder, "plots")
    os.makedirs(
        plots_folder,
        exist_ok=True,
    )

    if fig is None:
        fig = plt.gcf()
    fig.savefig(
        os.path.join(plots_folder, f"{name}.{type}"),
        dpi=450,
        bbox_inches="tight",
        pad_inches=0.01,
    )

    plt.close()


def format_plot(
    xlocator=matplotlib.ticker.AutoMinorLocator(),
    ylocator=matplotlib.ticker.AutoMinorLocator(),
    zeroline=False,
):
    fig = plt.gcf()
    for ax in fig.axes:
        if zeroline:
            ax.axhline(0, linewidth=1.5, c="black")

        ax.get_xaxis().set_minor_locator(xlocator)
        ax.get_yaxis().set_minor_locator(ylocator)
        ax.grid(visible=True, which="major", linewidth=1.0)
        ax.grid(visible=True, which="minor", linewidth=0.5, linestyle="-.")

    fig.tight_layout(pad=0.1, h_pad=0.4, w_pad=0.4)