# src/components/charts.py


import streamlit as st
import pandas as pd

def plot_time_series(df: pd.DataFrame, x_col: str, y_cols: list):
    """Plots time series data using Streamlit's line_chart."""
    if df is None or df.empty:
        st.write("No data available to plot.")
        return
    if x_col not in df.columns:
        st.error(f"X-axis column '{x_col}' not found in DataFrame.")
        return

    # Ensure the x-column is set as index for st.line_chart
    try:
        df_plot = df.set_index(x_col)
    except KeyError:
         st.error(f"Cannot set index with column '{x_col}'. Already index?")
         df_plot = df # Assume it might already be indexed

    # Check if y_cols exist
    valid_y_cols = [col for col in y_cols if col in df_plot.columns]
    if not valid_y_cols:
        st.error(f"None of the specified Y-axis columns {y_cols} found.")
        return

    # Plot using Streamlit's built-in chart
    st.line_chart(df_plot[valid_y_cols])

    # You could replace st.line_chart with Plotly or Altair for more customization:
    # import plotly.express as px
    # fig = px.line(df, x=x_col, y=valid_y_cols, title="Sensor Readings Over Time")
    # st.plotly_chart(fig, use_container_width=True)