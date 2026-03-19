import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Multi-Bagger Sniper 🎯", layout="wide")

st.title("🎯 Multi-Bagger Sniper: Fundamental + ATH Breakout")
st.markdown("Scanning for companies with **High ROCE** that are breaking out of **All-Time Highs**.")

def get_technical_status(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        # Fetch max history to find true ATH
        hist = stock.history(period="max")
        if hist.empty: return None
        
        ath = hist['High'].max()
        current_price = hist['Close'].iloc[-1]
        dist_from_ath = ((ath - current_price) / ath) * 100
        
        # Fundamental Check
        info = stock.info
        roce = info.get('returnOnAssets', 0) * 100 
        mcap = info.get('marketCap', 0) / 10**7
        
        return {
            "Ticker": ticker_symbol,
            "Price": round(current_price, 2),
            "ATH": round(ath, 2),
            "Dist from ATH (%)": round(dist_from_ath, 2),
            "ROCE %": round(roce, 2),
            "MCap (Cr)": int(mcap),
            "Status": "🔥 BREAKOUT" if dist_from_ath <= 1 else "⌛ Near ATH" if dist_from_ath <= 5 else "Boring"
        }
    except Exception as e:
        return None

# Sidebar Ticker List (Example: Nifty Next 50 or Midcap 100)
tickers_input = st.sidebar.text_area("NSE Tickers", "KEI.NS, KPITTECH.NS, HAL.NS, MAZDOCK.NS, BEL.NS")

if st.sidebar.button("Scan for Breakouts"):
    results = []
    progress_bar = st.progress(0)
    ticker_list = [t.strip() for t in tickers_input.split(",")]
    
    for i, t in enumerate(ticker_list):
        data = get_technical_status(t)
        if data:
            results.append(data)
        progress_bar.progress((i + 1) / len(ticker_list))
    
    df = pd.DataFrame(results)
    
    # Filter for the "Sniper" Quality
    sniper_picks = df[(df['ROCE %'] > 15) & (df['Dist from ATH (%)'] < 5)]
    
    st.subheader("🚀 High-Conviction Breakouts")
    st.dataframe(sniper_picks.sort_values(by="Dist from ATH (%)"))
    
    st.subheader("all Scanned Stocks")
    st.table(df)
