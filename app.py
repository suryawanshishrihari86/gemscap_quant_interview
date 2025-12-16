import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go

from ingestion import BinanceIngestor
from analytics import (
    compute_hedge_ratio,
    compute_spread,
    compute_zscore,
    adf_test
)

st.set_page_config(layout="wide")
st.title("Real-Time Pairs Trading Analytics")

# ======================
# Configuration
# ======================
symbols = ["BTCUSDT", "ETHUSDT"]

@st.cache_resource
def start_ingestion():
    ingestor = BinanceIngestor(symbols)
    ingestor.start()
    return ingestor

ingestor = start_ingestion()

# ======================
# Sidebar Controls
# ======================
st.sidebar.header("Controls")
z_threshold = st.sidebar.slider("Z-Score Alert Threshold", 1.0, 3.0, 2.0)
rolling_window = st.sidebar.slider("Rolling Window", 20, 100, 50)
corr_window = st.sidebar.slider("Correlation Window", 10, 60, 30)

# Allow some time for data collection
time.sleep(3)

btc = pd.DataFrame(ingestor.data["BTCUSDT"])
eth = pd.DataFrame(ingestor.data["ETHUSDT"])

if len(btc) < 50 or len(eth) < 50:
    st.warning("Collecting live market data...")
    st.stop()

# ======================
# Time Alignment
# ======================
btc = btc.sort_values("time")
eth = eth.sort_values("time")

df = pd.merge_asof(
    btc,
    eth,
    on="time",
    direction="nearest",
    suffixes=("_btc", "_eth")
)

df = df.dropna()

if len(df) < rolling_window:
    st.warning("Waiting for sufficient aligned data...")
    st.stop()

# ======================
# Analytics
# ======================
hedge = compute_hedge_ratio(df["price_eth"], df["price_btc"])
df["spread"] = compute_spread(df["price_btc"], df["price_eth"], hedge)
df["zscore"] = compute_zscore(df["spread"], window=rolling_window)

df["rolling_corr"] = (
    df["price_btc"]
    .rolling(corr_window)
    .corr(df["price_eth"])
)

adf_result = adf_test(df["spread"])

# ======================
# Normalized Prices
# ======================
df["btc_norm"] = df["price_btc"] / df["price_btc"].iloc[0]
df["eth_norm"] = df["price_eth"] / df["price_eth"].iloc[0]

# ======================
# Visualization
# ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Normalized Price Series")
    fig = go.Figure()
    fig.add_scatter(x=df["time"], y=df["btc_norm"], name="BTC (Normalized)")
    fig.add_scatter(x=df["time"], y=df["eth_norm"], name="ETH (Normalized)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Spread & Z-Score")
    fig2 = go.Figure()
    fig2.add_scatter(x=df["time"], y=df["spread"], name="Spread")
    fig2.add_scatter(x=df["time"], y=df["zscore"], name="Z-Score")
    st.plotly_chart(fig2, use_container_width=True)

# ======================
# Rolling Correlation
# ======================
st.subheader("Rolling Correlation")
fig3 = go.Figure()
fig3.add_scatter(
    x=df["time"],
    y=df["rolling_corr"],
    name="BTC-ETH Correlation"
)
st.plotly_chart(fig3, use_container_width=True)

# ======================
# Statistical Summary
# ======================
st.subheader("Statistical Summary")
st.write(f"**Hedge Ratio (OLS):** {hedge:.4f}")
st.write(f"**ADF p-value:** {adf_result['p-value']:.4f}")

if adf_result["Stationary"]:
    st.success("Spread appears mean-reverting (Stationary).")
else:
    st.warning("Spread is not stationary in this time window.")

latest_z = df["zscore"].iloc[-1]
if abs(latest_z) > z_threshold:
    st.error(f"Z-Score Alert Triggered: {latest_z:.2f}")
else:
    st.success(f"Z-Score Normal: {latest_z:.2f}")
