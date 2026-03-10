import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(page_title="Monte Carlo Option Pricing", layout="wide")

st.title("Monte Carlo Option Pricing Engine by Krish Jariwala")

st.markdown("Visual tool for pricing European options using Geometric Brownian Motion.")

# --- Sidebar Inputs ---
st.sidebar.header("Option Parameters")

ticker = st.sidebar.text_input("Ticker Symbol", value="^NSEI")
st.sidebar.caption("Use .NS for Indian stocks (e.g., RELIANCE.NS). ^NSEI is NIFTY 50.")

strike_price = st.sidebar.number_input("Strike Price (K)", value=22000.0, step=100.0)
time_to_maturity_days = st.sidebar.number_input("Time to Maturity (Days)", value=30, step=1)
risk_free_rate = st.sidebar.number_input("Risk-Free Rate (%)", value=7.0, step=0.1) / 100.0

st.sidebar.header("Simulation Parameters")
num_simulations = st.sidebar.slider("Number of Simulations", min_value=100, max_value=20000, value=1000, step=100)
num_steps = st.sidebar.slider("Number of Time Steps", min_value=10, max_value=252, value=252, step=10)

option_type = st.sidebar.radio("Option Type", ("Call", "Put"))

# --- Data Fetching ---
@st.cache_data(ttl=900)
def fetch_data(ticker_symbol):
    try:
        data = yf.download(ticker_symbol, period="1y", progress=False)
        return data
    except Exception as e:
        return pd.DataFrame()

with st.spinner(f"Fetching data for {ticker}..."):
    hist_data = fetch_data(ticker)

if hist_data.empty:
    st.error(f"Failed to fetch data for {ticker}. Rate Limit Achieved. Please try after some time")
    st.stop()

# Helper to safely extract close prices
def get_close_prices(data, ticker_symbol):
    if 'Close' in data.columns:
        if isinstance(data.columns, pd.MultiIndex):
            # yfinance > 0.2.x with multiindex
            return data['Close'][ticker_symbol]
        else:
            return data['Close']
    else:
        # Fallback if standard 'Close' isn't explicitly there but can be inferred
        return data.iloc[:, 3]

close_prices = get_close_prices(hist_data, ticker)
close_prices = close_prices.dropna()

if len(close_prices) == 0:
    st.error(f"Not enough data to compute spot price for {ticker}.")
    st.stop()

spot_price = float(close_prices.iloc[-1])
returns = np.log(close_prices / close_prices.shift(1)).dropna()

# Calculate historical volatility (annualized)
historical_volatility = float(returns.std() * np.sqrt(252))

st.sidebar.markdown("---")
use_historical_vol = st.sidebar.checkbox("Use Historical Volatility", value=True)

if use_historical_vol:
    volatility = st.sidebar.number_input("Volatility (σ)", value=historical_volatility, format="%.4f", disabled=True)
else:
    # use 0.0001 to prevent ZeroDivisionError or weirdness in user input
    volatility = st.sidebar.number_input("Volatility (σ)", min_value=0.0001, max_value=5.0, value=historical_volatility, format="%.4f")

st.markdown(f"**Current Spot Price ($S_0$):** ₹{spot_price:,.2f}  |  **Historical Volatility:** {historical_volatility*100:.2f}%")

# --- Monte Carlo Engine ---
T = time_to_maturity_days / 365.25
if T <= 0:
    st.error("Time to maturity must be greater than 0.")
    st.stop()

dt = T / num_steps
S0 = spot_price
K = strike_price
r = risk_free_rate
sigma = volatility

st.markdown("---")

if st.button("Run Simulation", type="primary"):
    with st.spinner("Running Monte Carlo ..."):
        # Precompute constants
        drift = (r - 0.5 * sigma**2) * dt
        vols = sigma * np.sqrt(dt)

        # Generate standard normal random variables
        Z = np.random.standard_normal((num_simulations, num_steps))

        # Shape: (num_simulations, num_steps + 1)
        price_paths = np.zeros((num_simulations, num_steps + 1))
        price_paths[:, 0] = S0

        for t in range(1, num_steps + 1):
            price_paths[:, t] = price_paths[:, t-1] * np.exp(drift + vols * Z[:, t-1])
        
        # Calculate payoffs at maturity
        final_prices = price_paths[:, -1]
        
        if option_type == "Call":
            payoffs = np.maximum(final_prices - K, 0)
        else:
            payoffs = np.maximum(K - final_prices, 0)

        # Discount to present value
        discounted_payoffs = payoffs * np.exp(-r * T)
        
        # Option Price and metrics
        option_price = np.mean(discounted_payoffs)
        std_error = np.std(discounted_payoffs) / np.sqrt(num_simulations)
        
        # Black-Scholes Formula for comparison
        d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == "Call":
            bs_price = S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            bs_price = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)

        col1, col2, col3 = st.columns(3)
        col1.metric("Monte Carlo Price", f"₹ {option_price:,.2f}", delta=f"SE: ±₹{std_error:.2f}", delta_color="off")
        col2.metric("Black-Scholes Price", f"₹ {bs_price:,.2f}")
        col3.metric("Difference", f"₹ {option_price - bs_price:,.2f}")

        # --- Visualizations ---
        st.subheader("Simulated Asset Price Paths")
        
        # Plot a subset of paths to avoid overwhelming the browser
        num_paths_to_plot = min(150, num_simulations)
        time_array = np.linspace(0, T, num_steps + 1)
        
        fig_paths = go.Figure()
        for i in range(num_paths_to_plot):
            fig_paths.add_trace(go.Scatter(
                x=time_array, 
                y=price_paths[i, :], 
                mode='lines', 
                line=dict(width=1), 
                opacity=0.3, 
                showlegend=False,
                hoverinfo='skip'
            ))
            
        fig_paths.add_hline(y=K, line_dash="dash", line_color="red", annotation_text="Strike Price", annotation_position="bottom right")
        fig_paths.update_layout(
            xaxis_title="Time (Years)",
            yaxis_title="Asset Price",
            template="plotly_dark",
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_paths, use_container_width=True)

        # Histogram of final prices
        st.subheader("Distribution of Final Asset Prices")
        fig_hist = go.Figure(data=[go.Histogram(x=final_prices, nbinsx=60, marker_color='#1f77b4', opacity=0.8)])
        fig_hist.add_vline(x=K, line_dash="dash", line_color="red", annotation_text="Strike Price")
        fig_hist.add_vline(x=S0, line_dash="dash", line_color="white", annotation_text="Initial Spot")
        fig_hist.update_layout(
            xaxis_title="Final Asset Price at Maturity",
            yaxis_title="Frequency",
            template="plotly_dark",
            bargap=0.05,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_hist, use_container_width=True)
