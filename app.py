import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Multi-Bagger Sniper 🎯", layout="wide")

st.title("🎯 Multi-Bagger Sniper v2")
st.markdown("Fundamental Analysis + All-Time High (ATH) Breakout Scanner")

def get_stock_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # 1. Technicals: ATH Calculation
        hist = stock.history(period="max")
        if hist.empty: return None
        ath = hist['High'].max()
        current_price = hist['Close'].iloc[-1]
        dist_from_ath = ((ath - current_price) / ath) * 100
        
        # 2. Fundamentals: Using .get() to avoid KeyErrors
        info = stock.info
        # yfinance often uses 'returnOnAssets' or 'returnOnEquity' for Indian firms
        roce = info.get('returnOnAssets', 0) * 100 
        mcap = info.get('marketCap', 0) / 10**7 # Cr
        debt_to_equity = info.get('debtToEquity', 0) / 100
        
        return {
            "Ticker": ticker_symbol,
            "Price": round(current_price, 2),
            "ATH": round(ath, 2),
            "Dist from ATH (%)": round(dist_from_ath, 2),
            "ROCE %": round(roce, 2),
            "Debt/Equity": round(debt_to_equity, 2),
            "MCap (Cr)": int(mcap),
            "Status": "🔥 BREAKOUT" if dist_from_ath <= 1.5 else "⌛ Near ATH" if dist_from_ath <= 5 else "Consolidating"
        }
    except Exception:
        return None

# Sidebar
st.sidebar.header("Scanner Configuration")
tickers_raw = st.sidebar.text_area("Enter NSE Tickers (e.g. HAL.NS, BEL.NS)", "KEI.NS, KPITTECH.NS, HAL.NS")

if st.sidebar.button("Run Sniper Scan"):
    ticker_list = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    results = []
    
    with st.spinner(f"Analyzing {len(ticker_list)} stocks..."):
        for t in ticker_list:
            data = get_stock_data(t)
            if data: results.append(data)
    
    if not results:
        st.error("No data found. Please check if tickers are correct (must end in .NS)")
    else:
        df = pd.DataFrame(results)
        
        # --- SAFE FILTERING ---
        # We check if columns exist before filtering to avoid KeyError
        if 'ROCE %' in df.columns:
            sniper_picks = df[(df['ROCE %'] > 15) & (df['Dist from ATH (%)'] < 5)]
            
            st.subheader("🚀 High-Conviction Sniper Picks")
            if not sniper_picks.empty:
                st.dataframe(sniper_picks.sort_values(by="Dist from ATH (%)"))
            else:
                st.info("No stocks currently match the '15% ROCE + <5% from ATH' criteria.")
            
            st.subheader("📋 All Scanned Stocks")
            st.dataframe(df)
        else:
            st.warning("Could not retrieve fundamental data for these tickers. Displaying price data only.")
            st.dataframe(df)
