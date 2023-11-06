"""Defines plotting capabilities."""

import matplotlib.pyplot as plt
import numpy as np

from .config import CONFIG
from .database import select_all_balances


def plot_aggregate_balance() -> None:
    """Plots the aggregate balance of all loans."""
    raw_balances: list[tuple[str, str]] = select_all_balances()
    timestamps = []
    balances = []
    for ts_str, bal_str in raw_balances:
        timestamps.append(ts_str)
        balances.append(float(bal_str.lstrip("$").replace(",", "")))

    x: np.ndarray = np.array(timestamps, dtype=np.datetime64)
    y: np.ndarray = np.array(balances)

    fig, ax = plt.subplots(figsize=CONFIG.plot_figure_size)

    ax.plot(x, y, "-o")

    plt.show()
