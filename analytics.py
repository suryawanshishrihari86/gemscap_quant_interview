import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

def compute_hedge_ratio(x, y):
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    return model.params[1]

def compute_spread(y, x, hedge_ratio):
    return y - hedge_ratio * x

def compute_zscore(series, window=50):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std

def adf_test(series):
    result = adfuller(series.dropna())
    return {
        "ADF Statistic": result[0],
        "p-value": result[1],
        "Stationary": result[1] < 0.05
    }
