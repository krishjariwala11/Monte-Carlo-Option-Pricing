# Monte Carlo Option Pricing Engine[![Open App](https://img.shields.io/badge/Open-Streamlit%20App-green)](https://monte-carlo-krish.streamlit.app)

An interactive visual tool for pricing European options using Monte Carlo simulations (Geometric Brownian Motion) and comparing results with the Black-Scholes model. Specifically tailored for the Indian stock market.

![Monte Carlo Simulation](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

- **Monte Carlo Simulation**: Simulates asset price paths using Geometric Brownian Motion.
- **Black-Scholes Comparison**: Provides a benchmark price using the standard Black-Scholes-Merton formula.
- **Dynamic Data Fetching**: Integration with `yfinance` to fetch real-time and historical data for Indian (NSE) and global tickers.
- **Interactive Visualizations**:
  - Simulated asset price paths over time.
  - Probability distribution of final asset prices at maturity.
- **Adjustable Parameters**: Customize strike price, time to maturity, risk-free rate, and simulation steps.
- **Volatility Analysis**: Option to use historical volatility or manual input.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/monte-carlo-option-pricing.git
    cd monte-carlo-option-pricing
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 💻 Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

Open your browser to the URL provided in the terminal (usually `http://localhost:8501`).

## 📊 How it Works

The engine uses **Geometric Brownian Motion (GBM)** to simulate the random walk of stock prices:

$$dS_t = r S_t dt + \sigma S_t dW_t$$

Where:
- $S_t$ is the stock price at time $t$.
- $r$ is the risk-free rate.
- $\sigma$ is the volatility.
- $dW_t$ is a Wiener process (Brownian motion).

By simulating thousands of possible price paths, we calculate the payoff for each path at maturity, average them, and discount the result to the present value to find the fair price of the option.

## 📝 Author

**Krish Jariwala**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
