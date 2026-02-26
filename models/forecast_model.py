# models/forecast_model.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input


def lstm_predict(symbol, hist, forecast_days=[7, 30]):
    
    # Ensure proper historical data

    if hist is None or hist.empty:
        return None

    if "Date" in hist.columns:
        hist["Date"] = pd.to_datetime(hist["Date"])
        hist = hist.set_index("Date")

    hist.index = pd.to_datetime(hist.index)
    hist = hist.sort_index()

    # Prepare data (Close only)

    data = hist['Close'].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    time_step = 100

    # Create sequences

    X, y = [], []
    for i in range(time_step, len(data_scaled)):
        X.append(data_scaled[i-time_step:i, 0])
        y.append(data_scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # Build model

    model = Sequential([
        Input(shape=(time_step, 1)),
        LSTM(50, return_sequences=True),
        LSTM(50),
        Dense(1)
    ])

    model.compile(loss='mse', optimizer='adam')

    model.fit(X, y, epochs=10, batch_size=64, verbose=0)

    # Forecast future

    temp_input = data_scaled[-time_step:].flatten().tolist()

    predictions = []

    for _ in range(max(forecast_days)):
        x_input = np.array(temp_input[-time_step:]).reshape(1, time_step, 1)
        yhat = model.predict(x_input, verbose=0)[0][0]

        temp_input.append(yhat)
        predictions.append(yhat)

    predictions = scaler.inverse_transform(
        np.array(predictions).reshape(-1, 1)
    ).flatten()

    return {
        "7_day": predictions[:7],
        "30_day": predictions[:30]
    }