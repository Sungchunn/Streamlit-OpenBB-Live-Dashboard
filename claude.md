# OpenBB Streamlit Dashboard

A Streamlit dashboard application that uses OpenBB's live API to fetch yfinance data and create interactive visualizations.

## Project Structure

```
OpenBB/
├── app.py                 # Main Streamlit application
├── streamlit_project/     # Streamlit components and modules
│   └── __init__.py
├── tests/                 # Test files
├── .venv/                # Virtual environment
└── claude.md             # This documentation file
```

## Environment Setup

### Virtual Environment
The project uses a Python virtual environment located in `.venv/`

### Installed Packages
Key packages installed:
- `openbb==4.4.5` - OpenBB Platform core
- `openbb-yfinance==1.4.7` - OpenBB yfinance integration
- `yfinance==0.2.58` - Yahoo Finance API
- `streamlit` (to be confirmed/installed)

### OpenBB Extensions
Multiple OpenBB extensions are available:
- openbb-equity, openbb-crypto, openbb-economy
- openbb-technical, openbb-quantitative
- openbb-news, openbb-derivatives
- And many more for comprehensive financial data access

## Commands

### Development Commands
```bash
# Activate virtual environment (REQUIRED)
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Install additional missing dependencies if needed
pip install plotly

# Run Streamlit dashboard
streamlit run app.py

# Run in background/headless mode
streamlit run app.py --server.headless=true --server.port=8501

# Run tests
python -m pytest tests/

# Check installed packages
pip list | grep -E "(streamlit|openbb|yfinance)"
```

### ⚠️ Important Setup Notes
- **Always activate the virtual environment** before running the app: `source .venv/bin/activate`
- The application was successfully tested and runs without errors
- Fixed UTF-8 encoding issue in emoji characters

### Application URLs
When running the application:
- **Local URL**: http://localhost:8501
- **Network URL**: http://10.5.50.129:8501 (for local network access)
- **External URL**: http://171.96.189.234:8501 (for external access)

### OpenBB API Usage
```python
# Basic OpenBB setup
from openbb import obb

# Get stock data
data = obb.equity.price.historical("AAPL", period="1y")

# Get financial statements
financials = obb.equity.fundamental.income("AAPL")

# Get technical indicators
technicals = obb.technical.sma(data, window=20)
```

### Streamlit Components
```python
# Basic Streamlit structure
import streamlit as st
import plotly.express as px

st.title("OpenBB Financial Dashboard")
st.sidebar.selectbox("Select Stock", ["AAPL", "GOOGL", "MSFT"])
st.plotly_chart(fig)
```

## Implemented Features ✅

1. **Stock Data Visualization**
   - ✅ Historical price charts (Candlestick & Line charts)
   - ✅ Volume analysis
   - ✅ Technical indicators (SMA 20/50, RSI, MACD)

2. **Financial Metrics**
   - ✅ Key company metrics display
   - ✅ Financial ratios and statistics
   - ✅ Real-time price metrics

3. **Market Analysis**
   - ✅ Price summary statistics
   - ✅ Technical analysis charts
   - ✅ Company news integration

4. **Interactive Elements**
   - ✅ Stock symbol input
   - ✅ Time period selection (1d to 5y)
   - ✅ Chart type selection (candlestick/line)
   - ✅ Feature toggles (volume, technicals, metrics, news)
   - ✅ Data refresh functionality
   - ✅ Raw data viewer

## Dashboard Components

### Files Created
- `app.py` - Main Streamlit application
- `streamlit_project/data_fetcher.py` - OpenBB data integration
- `streamlit_project/visualizations.py` - Chart generation and display
- `requirements.txt` - Dependencies list

### Key Features
- **Live Data**: Real-time data from Yahoo Finance via OpenBB
- **Caching**: Smart caching for improved performance
- **Error Handling**: Robust error handling and user feedback
- **Responsive Design**: Mobile-friendly layout
- **Progress Indicators**: Loading progress bars
- **Interactive Charts**: Plotly-based interactive visualizations

## Development Notes

- OpenBB Platform is already installed with comprehensive extensions
- yfinance is available both standalone and through OpenBB
- Project structure supports modular development
- Virtual environment is configured and ready

## Next Steps

1. Set up Streamlit application structure
2. Implement OpenBB data fetching functions
3. Create interactive dashboard components
4. Add data visualization with Plotly
5. Implement user controls and filters