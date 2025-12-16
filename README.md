# Real-Time Pairs Trading Analytics – Gemscap

This project ingests live Binance Futures data and performs
pairs trading analytics in real time.

## Features
- Live BTC & ETH price streaming
- Hedge ratio via OLS regression
- Spread and Z-score computation
- ADF test for stationarity
- Real-time alerts

## Run
pip install -r requirements.txt  
streamlit run app.py

## Architecture
WebSocket → Ingestion → Analytics → Streamlit UI → Alerts

## AI Usage
ChatGPT was used to assist with structuring and debugging.
