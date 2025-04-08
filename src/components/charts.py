# src/components/charts.py

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def plot_time_series(data, title, y_label, color):
    """Plots a simple time-series chart for monitoring trends."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data["timestamp"], data["value"], color=color, linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("Timestamp")
    ax.set_ylabel(y_label)
    ax.grid(True)
    st.pyplot(fig)
