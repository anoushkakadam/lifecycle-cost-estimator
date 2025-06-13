
# 🔧 Lifecycle Cost Estimator (NPV-Based)

A Streamlit app to estimate and compare the total cost of ownership (TCO) of industrial equipment over its lifecycle using Net Present Value (NPV).

## 🌐 Live App

View App Here [Lifecycle Cost Estimator (NPV-Based)](https://lifecycle-cost-estimator-anoushkakadam.streamlit.app/)

## 📦 Features
- Manual cost calculator for a single equipment
- CSV upload to compare multiple equipment lifecycle costs
- NPV logic with discount rate
- CSV and PDF export for reporting

## 🚀 How to Run

```bash
pip install -r requirements.txt
streamlit run lifecycle_estimator.py
```

## 📁 Sample CSV Format

```csv
Equipment,Initial Cost,Maintenance Cost,Maintenance Interval,Replacement Cost,Replacement Interval,Reuse Rate,Operating Life,Downtime Cost,Discount Rate
Diesel Generator,500000,15000,6,250000,5,20,10,10000,6
Gas Engine,600000,12000,4,200000,4,15,12,8000,5
Battery Bank,800000,10000,12,300000,6,30,8,5000,7
```

## 🌐 Live Demo

Coming soon...
