# streamlit_app.py

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime
import re  # For sanitizing names

# Suppress SettingWithCopyWarning
pd.options.mode.chained_assignment = None

# Set the page configuration
st.set_page_config(
    page_title="Market Indices & Sector ETFs Performance",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title of the App
st.title("📈 Market Indices, Sector ETFs & Top 10 USA Stocks Performance Dashboard")

# Define Tabs
tabs = st.tabs([
    "Performance Overview", 
    "Sector ETFs (USA)", 
    "Top 10 USA Stocks YTD", 
    "FTSE MIB Italy", 
    "Additional Insights"
])

# Define tickers for Performance Overview (USA)
tickers_usa = {
    # Major Indices
    "Nasdaq Composite": "^IXIC",
    "QQQ (Invesco QQQ Trust)": "QQQ",
    "S&P 500": "^GSPC",
    "FTSE MIB (Italy)": "FTSEMIB.MI",
    
    # Additional Popular ETFs
    "iShares MSCI EAFE ETF": "EFA",
    "Vanguard FTSE Emerging Markets ETF": "VWO",
    "SPDR S&P MidCap 400 ETF": "MDY",
    "iShares Russell 2000 ETF": "IWM",
    "Vanguard Total Stock Market ETF": "VTI",
    "iShares MSCI Emerging Markets ETF": "EEM",
    "iShares Core U.S. Aggregate Bond ETF": "AGG",
}

# Define Sector ETFs for USA
sector_etfs_usa = {
    "Technology": "XLK",
    "Health Care": "XLV",
    "Financial": "XLF",
    "Consumer Discretionary": "XLY",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
}

# Define Top 10 USA Stocks per Sector with Interpretive Names
sectors_top10_usa = {
    "Technology": [
        "Apple (AAPL)", "Microsoft (MSFT)", "Alphabet (GOOGL)", "Amazon (AMZN)", "NVIDIA (NVDA)",
        "Meta Platforms (META)", "Adobe (ADBE)", "Intel (INTC)", "Cisco Systems (CSCO)", "Salesforce (CRM)"
    ],
    "Health Care": [
        "Johnson & Johnson (JNJ)", "Pfizer (PFE)", "UnitedHealth Group (UNH)", "Merck & Co. (MRK)", "Abbott Laboratories (ABT)",
        "Thermo Fisher Scientific (TMO)", "Amgen (AMGN)", "Eli Lilly (LLY)", "Bristol-Myers Squibb (BMY)", "Gilead Sciences (GILD)"
    ],
    "Financial": [
        "JPMorgan Chase (JPM)", "Bank of America (BAC)", "Wells Fargo (WFC)", "Citigroup (C)", "Goldman Sachs (GS)",
        "Morgan Stanley (MS)", "BlackRock (BLK)", "American Express (AXP)", "U.S. Bancorp (USB)", "Bank of New York Mellon (BK)"
    ],
    "Consumer Discretionary": [
        "Amazon (AMZN)", "Tesla (TSLA)", "Home Depot (HD)", "Nike (NKE)", "Starbucks (SBUX)",
        "McDonald's (MCD)", "Lowe's (LOW)", "Target (TGT)", "Booking Holdings (BKNG)", "Disney (DIS)"
    ],
    "Industrials": [
        "Boeing (BA)", "Honeywell (HON)", "General Electric (GE)", "3M (MMM)", "Caterpillar (CAT)",
        "Union Pacific (UNP)", "Deere & Company (DE)", "Lockheed Martin (LMT)", "United Parcel Service (UPS)", "FedEx (FDX)"
    ],
    "Energy": [
        "Exxon Mobil (XOM)", "Chevron (CVX)", "ConocoPhillips (COP)", "Schlumberger (SLB)", "Valero Energy (VLO)",
        "Phillips 66 (PSX)", "ONEOK (OKE)", "Marathon Oil (MRO)", "Kinder Morgan (KMI)", "EOG Resources (EOG)"
    ],
    "Materials": [
        "Linde plc (LIN)", "Air Products (APD)", "Ecolab (ECL)", "Sherwin-Williams (SHW)", "Freeport-McMoRan (FCX)",
        "Newmont Corporation (NEM)", "DuPont de Nemours (DD)", "Progressive Corporation (PFG)", "Archer-Daniels-Midland (ADM)", "Ball Corporation (BLL)"
    ],
    "Utilities": [
        "NextEra Energy (NEE)", "Duke Energy (DUK)", "Southern Company (SO)", "Exelon Corporation (EXC)", "American Electric Power (AEP)",
        "Dominion Energy (D)", "Public Service Enterprise Group (PEG)", "Xcel Energy (XEL)", "CenterPoint Energy (CNP)", "Consolidated Edison (ED)"
    ],
    "Real Estate": [
        "American Tower (AMT)", "Prologis (PLD)", "Simon Property Group (SPG)", "Crown Castle International (CCI)", "Realty Income (O)",
        "Equinix (EQIX)", "Public Storage (PSA)", "Digital Realty Trust (DLR)", "Vornado Realty Trust (VNO)", "Weyerhaeuser (WY)"
    ],
}

# Define Sector Tickers for FTSE MIB Italy (Replace with actual Italian sector ETFs if available)
sector_etfs_europe_it = {
    "Technology": "EXV1.DE",  # Example ETF ticker, replace with actual if different
    "Health Care": "EXV4.DE",
    "Financial": "EXV6.DE",
    "Consumer Discretionary": "EXV7.DE",
    "Industrials": "EXV9.DE",
    "Energy": "EXV2.DE",
    "Materials": "EXV8.DE",
    "Utilities": "EXV3.DE",
    "Real Estate": "EXV5.DE",
}

# Define Top 10 European Stocks per Sector (Example)
sectors_top10_europe = {
    "Technology": [
        "ASML Holding (ASML)", "SAP SE (SAP)", "Siemens AG (SIE)", "Infineon Technologies (IFX)", "STMicroelectronics (STM)",
        "Nokia (NOKIA.HE)", "Dassault Systèmes (DSY.PA)", "Amadeus IT Group (AMS.MC)", "Adyen NV (ADYEY)"
    ],
    "Health Care": [
        "Roche Holding (ROG.SW)", "Novartis AG (NOVN.SW)", "Sanofi (SAN.PA)", "GlaxoSmithKline (GSK.L)", "AstraZeneca (AZN.L)",
        "Bayer AG (BAYN.DE)", "Merck KGaA (MRK.DE)", "Novo Nordisk (NOVO-B.CO)", "Boehringer Ingelheim", "Lundbeck (LUN.CO)"
    ],
    "Financial": [
        "BNP Paribas (BNP.PA)", "ING Groep (INGA.AS)", "Santander Bank (SAN.MC)", "Deutsche Bank (DBK.DE)", "UBS Group (UBSG.SW)",
        "Unicredit (UCG.MI)", "AXA (CS.PA)", "Intesa Sanpaolo (ISP.MI)", "Allianz SE (ALV.DE)", "Credit Suisse (CSGN.SW)"
    ],
    "Consumer Discretionary": [
        "LVMH Moët Hennessy Louis Vuitton (MC.PA)", "Volkswagen AG (VOW3.DE)", "BMW AG (BMW.DE)", "Ferrari NV (RACE.MI)", "Adidas AG (ADS.DE)",
        "Pernod Ricard (RI.PA)", "Hugo Boss (BOSS.DE)", "Ferrero Group", "Kering (KER.PA)", "Heineken NV (HEINY.AS)"
    ],
    "Industrials": [
        "Siemens AG (SIE)", "Airbus SE (AIR.PA)", "BASF SE (BAS.DE)", "Daimler AG (DAI.DE)", "Thales Group (HO.PA)",
        "Rolls-Royce Holdings (RR.L)", "Bosch Group", "Schneider Electric (SU.PA)", "Saint-Gobain (SGO.PA)", "SKF AB (SKF-B.ST)"
    ],
    "Energy": [
        "Royal Dutch Shell (RDSA.AS)", "BP plc (BP.L)", "TotalEnergies SE (TTE.PA)", "Equinor ASA (EQNR.OL)", "Eni SpA (E)",
        "Repsol SA (REP.MC)", "Petrobras (PETR4.SA)", "ConocoPhillips (COP)", "Gazprom PAO (GAZP.MM)", "Petronas"
    ],
    "Materials": [
        "BASF SE (BAS.DE)", "Rio Tinto Group (RIO.L)", "ArcelorMittal (MT.AS)", "Glencore plc (GLEN.L)", "LyondellBasell Industries",
        "Norsk Hydro (NHY.OL)", "Vitol Group", "HeidelbergCement (HEI.DE)", "CRH plc (CRH.L)", "Covestro AG (1COV.DE)"
    ],
    "Utilities": [
        "Iberdrola SA (IBE.MC)", "Enel SpA (ENEL.MI)", "EDF (EDF.PA)", "Engie SA (ENGI.PA)", "E.ON SE (EOAN.DE)",
        "RWE AG (RWE.DE)", "Vattenfall AB", "Fortum Oyj (FORTUM.HE)", "Orsted (ORSTED.CO)", "National Grid plc (NG.L)"
    ],
    "Real Estate": [
        "Unibail-Rodamco-Westfield (URW.AS)", "Vonovia SE (VNA.DE)", "Leg Immobilien AG (LEG.DE)", "Land Securities Group (LAND.L)", "British Land Company (BLND.L)",
        "Klépierre (LI.PA)", "Simon Property Group (SPG)", "Daito Trust Construction (1841.T)", "Gecina (GFC.PA)", "Vonovia SE (VNA.DE)"
    ],
}

# Function to fetch data
@st.cache_data
def fetch_data(ticker, start_date=None, end_date=None):
    """
    Fetches historical data for a given ticker.
    :param ticker: Stock ticker symbol
    :param start_date: Start date for data retrieval
    :param end_date: End date for data retrieval
    :return: DataFrame with Date and Close price
    """
    try:
        if start_date and end_date:
            data = yf.download(ticker, start=start_date, end=end_date)
        else:
            data = yf.download(ticker, period="max")
        if data.empty:
            st.warning(f"No data returned for ticker: {ticker}")
            return pd.DataFrame()
        data.reset_index(inplace=True)
        # Ensure 'Date' is of datetime type
        data['Date'] = pd.to_datetime(data['Date'])
        return data[['Date', 'Close']]
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

# Function to sanitize trace names
def sanitize_name(name):
    """
    Sanitize the trace name by ensuring it's a string and removing unwanted characters.
    :param name: Original name input
    :return: Sanitized name string
    """
    if name is None:
        return "Unknown"
    
    # Ensure the name is a string
    try:
        name = str(name)
    except Exception as e:
        st.error(f"Error converting name to string: {e}")
        return "Invalid Name"
    
    # Remove any characters that are not alphanumeric or spaces
    sanitized = re.sub(r'[^\w\s]', '', name)
    # Replace multiple spaces with a single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized.strip()

# Helper function to get first day of current year
def get_first_day_of_year():
    today = datetime.today()
    return datetime(today.year, 1, 1)

# Performance Overview Tab (USA & FTSE MIB Italy)
with tabs[0]:
    st.header("📊 Performance of Major Indices and ETFs (USA & Italy)")
    
    # Sidebar for date range selection
    st.sidebar.header("Select Date Range for Performance Overview")
    end_date_perf = datetime.today()
    start_date_perf = get_first_day_of_year()
    
    user_start_date_perf = st.sidebar.date_input("Start date", start_date_perf, key='perf_start')
    user_end_date_perf = st.sidebar.date_input("End date", end_date_perf, key='perf_end')
    
    if user_start_date_perf > user_end_date_perf:
        st.sidebar.error("Error: Start date must be before end date.")
    else:
        # Fetch and merge data for USA and Italy indices/ETFs
        merged_data_perf = pd.DataFrame()
        fetched_tickers_perf = []
        for name, ticker in tickers_usa.items():
            data = fetch_data(ticker, start_date=user_start_date_perf, end_date=user_end_date_perf)
            if data.empty:
                st.warning(f"No data fetched for {name} ({ticker}). Skipping...")
                continue
            data = data.rename(columns={'Close': name})
            merged_data_perf = pd.merge(merged_data_perf, data, on='Date', how='outer') if not merged_data_perf.empty else data
            fetched_tickers_perf.append(name)
        
        if merged_data_perf.empty:
            st.warning("No data available for the selected date range.")
        else:
            # Sort by Date and forward-fill missing values
            merged_data_perf.sort_values('Date', inplace=True)
            merged_data_perf.fillna(method='ffill', inplace=True)
            
            # Drop duplicates if any and reset index
            try:
                merged_data_perf = merged_data_perf.drop_duplicates(subset='Date').reset_index(drop=True)
            except KeyError as e:
                st.error(f"Error dropping duplicates: {e}")
                st.stop()
            
            # Diagnostic: Display columns and data snapshot before further processing
            st.write("### Columns in `merged_data_perf` before standardization:")
            st.write(merged_data_perf.columns.tolist())

            st.write("### Data Snapshot of `merged_data_perf` before standardization:")
            st.write(merged_data_perf.head())
            
            # Standardize column names: strip spaces and ensure consistent casing
            merged_data_perf.columns = merged_data_perf.columns.str.strip()
            merged_data_perf.columns = merged_data_perf.columns.str.title()  # Converts 'date' to 'Date'

            # Reset index to ensure 'Date' is a column
            merged_data_perf = merged_data_perf.reset_index(drop=True)

            # If the DataFrame has a MultiIndex, flatten it
            if isinstance(merged_data_perf.columns, pd.MultiIndex):
                merged_data_perf.columns = [' '.join(col).strip() for col in merged_data_perf.columns.values]

            # Verify the presence of 'Date' column after corrections
            if 'Date' not in merged_data_perf.columns:
                st.error("Error: 'Date' column is missing after merging. Please check the data sources.")
                st.stop()

            # Diagnostic: Display columns and data snapshot after standardization
            st.write("### Columns in `merged_data_perf` after standardization:")
            st.write(merged_data_perf.columns.tolist())

            st.write("### Data Snapshot of `merged_data_perf` after standardization:")
            st.write(merged_data_perf.head())

            # Normalize the data to start at 100 for comparison
            normalized_data_perf = merged_data_perf.copy()
            for column in normalized_data_perf.columns[1:]:
                initial_value = normalized_data_perf[column].iloc[0]
                if initial_value == 0 or pd.isna(initial_value):
                    st.warning(f"Initial value for {column} is 0 or NaN. Skipping normalization.")
                    normalized_data_perf[column] = 0
                else:
                    normalized_data_perf[column] = (normalized_data_perf[column] / initial_value) * 100
            
            # Determine available tickers in the merged DataFrame
            available_tickers_perf = [ticker for ticker in fetched_tickers_perf if ticker in normalized_data_perf.columns]
            if not available_tickers_perf:
                st.warning("No tickers available after merging.")
            else:
                # Multiselect for selecting which tickers to display
                selected_tickers_perf = st.multiselect(
                    "Select Tickers to Display",
                    options=available_tickers_perf,
                    default=available_tickers_perf
                )
                
                if not selected_tickers_perf:
                    st.warning("No tickers selected to display.")
                else:
                    # Ensure selected tickers are present in the DataFrame
                    selected_tickers_perf = [ticker for ticker in selected_tickers_perf if ticker in normalized_data_perf.columns]
                    
                    # Filter data based on selection
                    filtered_data_perf = normalized_data_perf[['Date'] + selected_tickers_perf]
                    
                    # Create Plotly figure
                    fig_perf = go.Figure()
                    
                    for column in filtered_data_perf.columns[1:]:
                        trace_name = sanitize_name(column)
                        fig_perf.add_trace(go.Scatter(
                            x=filtered_data_perf['Date'],
                            y=filtered_data_perf[column],
                            mode='lines',
                            name=trace_name
                        ))
                    
                    # Update layout for better aesthetics
                    fig_perf.update_layout(
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
                    
                    st.plotly_chart(fig_perf, use_container_width=True)
                    
                    # Optional: Display the merged data
                    with st.expander("Show Data Table"):
                        st.dataframe(merged_data_perf.set_index('Date'))
