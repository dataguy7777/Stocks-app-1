# Performance Overview Tab (USA & FTSE MIB Italy)
with tabs[0]:
    st.header("📊 Performance of Major Indices and ETFs (USA & Italy)")
    
    # Sidebar for date range selection
    st.sidebar.header("Select Date Range for Performance Overview")
    end_date_perf = datetime.today()
    start_date_perf = get_first_day_of_year()
    
    user_start_date_perf = st.sidebar.date_input("Start date", start_date_perf)
    user_end_date_perf = st.sidebar.date_input("End date", end_date_perf)
    
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
            merged_data_perf = merged_data_perf.drop_duplicates(subset='Date').reset_index(drop=True)
            
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
