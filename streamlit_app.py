# Streamlit app to display performance of major indices, sector ETFs, and top 10 USA stocks per sector with Plotly

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Set the page configuration
st.set_page_config(
    page_title="Market Indices & Sector ETFs Performance",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title of the App
st.title("📈 Market Indices, Sector ETFs & Top 10 USA Stocks Performance Dashboard")

# Create Tabs
tabs = st.tabs(["Performance Overview", "Sector ETFs", "Top 10 USA Stocks YTD", "Additional Insights"])

# Define tickers
tickers = {
    # Major Indices
    "Nasdaq Composite (^IXIC)": "^IXIC",
    "QQQ (Invesco QQQ Trust)": "QQQ",
    "S&P 500 (^GSPC)": "^GSPC",
    "FTSE MIB (^FTMIB)": "^FTMIB",
    
    # Sector ETFs
    "Technology Select Sector SPDR Fund (XLK)": "XLK",
    "Health Care Select Sector SPDR Fund (XLV)": "XLV",
    "Financial Select Sector SPDR Fund (XLF)": "XLF",
    "Consumer Discretionary Select Sector SPDR Fund (XLY)": "XLY",
    "Industrials Select Sector SPDR Fund (XLI)": "XLI",
    "Energy Select Sector SPDR Fund (XLE)": "XLE",
    "Materials Select Sector SPDR Fund (XLB)": "XLB",
    "Utilities Select Sector SPDR Fund (XLU)": "XLU",
    "Real Estate Select Sector SPDR Fund (XLRE)": "XLRE",
    
    # Additional Popular ETFs
    "iShares MSCI EAFE ETF (EFA)": "EFA",
    "Vanguard FTSE Emerging Markets ETF (VWO)": "VWO",
    "SPDR S&P MidCap 400 ETF (MDY)": "MDY",
    "iShares Russell 2000 ETF (IWM)": "IWM",
    "Vanguard Total Stock Market ETF (VTI)": "VTI",
    "iShares MSCI Emerging Markets ETF (EEM)": "EEM",
    "iShares Core U.S. Aggregate Bond ETF (AGG)": "AGG",
}

# Define Top 10 USA Stocks per Sector
sectors_top10 = {
    "Technology": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "ADBE", "INTC", "CSCO", "CRM"
    ],
    "Health Care": [
        "JNJ", "PFE", "UNH", "MRK", "ABT",
        "TMO", "AMGN", "LLY", "BMY", "GILD"
    ],
    "Financial": [
        "JPM", "BAC", "WFC", "C", "GS",
        "MS", "BLK", "AXP", "USB", "BK"
    ],
    "Consumer Discretionary": [
        "AMZN", "TSLA", "HD", "NKE", "SBUX",
        "MCD", "LOW", "TGT", "BKNG", "DIS"
    ],
    "Industrials": [
        "BA", "HON", "GE", "MMM", "CAT",
        "UNP", "DE", "LMT", "UPS", "FDX"
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "VLO",
        "PSX", "OKE", "MRO", "KMI", "EOG"
    ],
    "Materials": [
        "LIN", "APD", "ECL", "SHW", "FCX",
        "NEM", "DD", "PFG", "ADM", "BLL"
    ],
    "Utilities": [
        "NEE", "DUK", "SO", "EXC", "AEP",
        "D", "PEG", "XEL", "CNP", "ED"
    ],
    "Real Estate": [
        "AMT", "PLD", "SPG", "CCI", "O",
        "EQIX", "PSA", "DLR", "VNO", "WY"
    ],
}

@st.cache_data
def fetch_data(ticker, start_date=None, end_date=None):
    """
    Fetches historical data for a given ticker.
    :param ticker: Stock ticker symbol
    :param start_date: Start date for data retrieval
    :param end_date: End date for data retrieval
    :return: DataFrame with Date and Close price
    """
    if start_date and end_date:
        data = yf.download(ticker, start=start_date, end=end_date)
    else:
        data = yf.download(ticker, period="max")
    data.reset_index(inplace=True)
    return data[['Date', 'Close']]

# Performance Overview Tab
with tabs[0]:
    st.header("📊 Performance of Major Indices and ETFs")
    
    # Sidebar for date range selection
    st.sidebar.header("Select Date Range")
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)  # Default to 1 year
    
    user_start_date = st.sidebar.date_input("Start date", start_date)
    user_end_date = st.sidebar.date_input("End date", end_date)
    
    if user_start_date > user_end_date:
        st.sidebar.error("Error: Start date must be before end date.")
    else:
        # Fetch and merge data
        merged_data = pd.DataFrame()
        for name, ticker in tickers.items():
            data = fetch_data(ticker, start_date=user_start_date, end_date=user_end_date)
            data = data.rename(columns={'Close': name})
            if merged_data.empty:
                merged_data = data
            else:
                merged_data = pd.merge(merged_data, data, on='Date', how='inner')
        
        if merged_data.empty:
            st.warning("No data available for the selected date range.")
        else:
            # Normalize the data to start at 100 for comparison
            normalized_data = merged_data.copy()
            for column in normalized_data.columns[1:]:
                normalized_data[column] = (normalized_data[column] / normalized_data[column].iloc[0]) * 100
            
            # Create Plotly figure
            fig = go.Figure()
            
            for column in normalized_data.columns[1:]:
                fig.add_trace(go.Scatter(
                    x=normalized_data['Date'],
                    y=normalized_data[column],
                    mode='lines',
                    name=column
                ))
            
            # Update layout for better aesthetics
            fig.update_layout(
                title="Performance Comparison (Normalized to 100)",
                xaxis_title="Date",
                yaxis_title="Normalized Price",
                hovermode="x unified",
                template="plotly_dark",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Optional: Display the merged data
            with st.expander("Show Data Table"):
                st.dataframe(merged_data.set_index('Date'))

# Sector ETFs Tab
with tabs[1]:
    st.header("🔍 Sector ETFs Performance")
    
    # Sidebar for date range selection
    st.sidebar.header("Select Date Range for Sector ETFs")
    end_date_sectors = datetime.today()
    start_date_sectors = end_date_sectors - timedelta(days=365)  # Default to 1 year
    
    user_start_date_sectors = st.sidebar.date_input("Start date (Sector ETFs)", start_date_sectors, key='sector_start')
    user_end_date_sectors = st.sidebar.date_input("End date (Sector ETFs)", end_date_sectors, key='sector_end')
    
    if user_start_date_sectors > user_end_date_sectors:
        st.sidebar.error("Error: Start date must be before end date for Sector ETFs.")
    else:
        # Filter sector ETFs from tickers
        sector_tickers = {name: ticker for name, ticker in tickers.items() if 'Select Sector' in name}
        
        # Fetch and merge sector ETF data
        merged_sector_data = pd.DataFrame()
        for name, ticker in sector_tickers.items():
            data = fetch_data(ticker, start_date=user_start_date_sectors, end_date=user_end_date_sectors)
            data = data.rename(columns={'Close': name})
            if merged_sector_data.empty:
                merged_sector_data = data
            else:
                merged_sector_data = pd.merge(merged_sector_data, data, on='Date', how='inner')
        
        if merged_sector_data.empty:
            st.warning("No data available for the selected date range for Sector ETFs.")
        else:
            # Normalize the data to start at 100 for comparison
            normalized_sector_data = merged_sector_data.copy()
            for column in normalized_sector_data.columns[1:]:
                normalized_sector_data[column] = (normalized_sector_data[column] / normalized_sector_data[column].iloc[0]) * 100
            
            # Create Plotly figure for Sector ETFs
            fig_sectors = go.Figure()
            
            for column in normalized_sector_data.columns[1:]:
                fig_sectors.add_trace(go.Scatter(
                    x=normalized_sector_data['Date'],
                    y=normalized_sector_data[column],
                    mode='lines',
                    name=column
                ))
            
            # Update layout for better aesthetics
            fig_sectors.update_layout(
                title="Sector ETFs Performance Comparison (Normalized to 100)",
                xaxis_title="Date",
                yaxis_title="Normalized Price",
                hovermode="x unified",
                template="plotly_dark",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_sectors, use_container_width=True)
            
            # Optional: Display the merged sector ETF data
            with st.expander("Show Sector ETFs Data Table"):
                st.dataframe(merged_sector_data.set_index('Date'))

# Top 10 USA Stocks YTD Tab
with tabs[2]:
    st.header("📈 Top 10 USA Stocks Year-To-Date (YTD) Performance")
    
    # Define YTD date range
    current_year = datetime.today().year
    ytd_start = datetime(current_year, 1, 1)
    ytd_end = datetime.today()
    
    # Sidebar for YTD date range selection (optional customization)
    st.sidebar.header("Select Date Range for YTD Performance")
    user_start_ytd = st.sidebar.date_input("Start date (YTD)", ytd_start, key='ytd_start')
    user_end_ytd = st.sidebar.date_input("End date (YTD)", ytd_end, key='ytd_end')
    
    if user_start_ytd > user_end_ytd:
        st.sidebar.error("Error: Start date must be before end date for YTD Performance.")
    else:
        # Iterate through each sector
        for sector, stock_list in sectors_top10.items():
            st.subheader(f"🔹 {sector} Sector - Top 10 USA Stocks")
            
            # Fetch and merge data for the sector
            merged_sector_stocks = pd.DataFrame()
            for stock in stock_list:
                data = fetch_data(stock, start_date=user_start_ytd, end_date=user_end_ytd)
                data = data.rename(columns={'Close': stock})
                if merged_sector_stocks.empty:
                    merged_sector_stocks = data
                else:
                    merged_sector_stocks = pd.merge(merged_sector_stocks, data, on='Date', how='inner')
            
            if merged_sector_stocks.empty:
                st.warning(f"No data available for the {sector} sector in the selected date range.")
                continue
            
            # Normalize the data to start at 100 for comparison
            normalized_sector_stocks = merged_sector_stocks.copy()
            for column in normalized_sector_stocks.columns[1:]:
                normalized_sector_stocks[column] = (normalized_sector_stocks[column] / normalized_sector_stocks[column].iloc[0]) * 100
            
            # Create Plotly figure for sector stocks
            fig_sector_stocks = go.Figure()
            
            for column in normalized_sector_stocks.columns[1:]:
                fig_sector_stocks.add_trace(go.Scatter(
                    x=normalized_sector_stocks['Date'],
                    y=normalized_sector_stocks[column],
                    mode='lines',
                    name=column
                ))
            
            # Update layout for better aesthetics
            fig_sector_stocks.update_layout(
                title=f"{sector} Sector Top 10 Stocks YTD Performance (Normalized to 100)",
                xaxis_title="Date",
                yaxis_title="Normalized Price",
                hovermode="x unified",
                template="plotly_dark",
                height=600,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_sector_stocks, use_container_width=True)
            
            # Optional: Display the merged sector stocks data
            with st.expander(f"Show {sector} Sector Stocks Data Table"):
                st.dataframe(merged_sector_stocks.set_index('Date'))

# Additional Insights Tab
with tabs[3]:
    st.header("📊 Additional Insights")
    st.write("Content for Additional Insights goes here.")
    st.write("""
    ### Possible Enhancements:
    - **Statistical Metrics:** Display metrics such as CAGR, volatility, and correlations between indices and ETFs.
    - **Interactive Filters:** Allow users to select specific indices or ETFs to compare.
    - **Different Chart Types:** Incorporate other Plotly chart types like candlestick charts or bar charts.
    - **Download Options:** Enable users to download the displayed data or charts.
    - **Real-Time Data:** Implement periodic data refreshes to keep the dashboard up-to-date.
    """)
