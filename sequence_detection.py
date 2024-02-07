# -*- coding: utf-8 -*-
"""sequence detection

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fzne0GvLA6JN2IF1IQKfEmrRfjl2LksZ
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

# Load your dataset (assuming it's stored in a CSV file)
dataframe = pd.read_csv('dummy_dataset.csv')

# Convert the 'date' column to datetime objects
dataframe['date'] = pd.to_datetime(dataframe['date'])

# Set the 'date' column as the index
dataframe.set_index('date', inplace=True)

# Extract the 'data' column for your dataset
dataset = dataframe['data'].values
dataset = dataset.astype('float32')

# Normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(dataset.reshape(-1, 1))

# Split the dataset into train and test sets
train_size = int(len(dataset) * 0.70)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size], dataset[train_size:len(dataset)]

# Create dataset matrix for training and testing
look_back = 3
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)

# Reshape the input data to be 3D (samples, time steps, features)
trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))
testX = np.reshape(testX, (testX.shape[0], testX.shape[1], 1))

# Define and compile the LSTM model
batch_size = 1
model = Sequential()
model.add(LSTM(4, batch_input_shape=(batch_size, look_back, 1), stateful=True))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
for i in range(2):
    model.fit(trainX, trainY, epochs=1, batch_size=batch_size, verbose=2, shuffle=False)
    model.reset_states()

# Make predictions
trainPredict = model.predict(trainX, batch_size=batch_size)
model.reset_states()
testPredict = model.predict(testX, batch_size=batch_size)

# Inverse transform predictions to the original scale
trainPredict = scaler.inverse_transform(trainPredict)
trainY = scaler.inverse_transform([trainY])
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform([testY])

# Calculate RMSE
trainScore = np.sqrt(mean_squared_error(trainY[0], trainPredict[:, 0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = np.sqrt(mean_squared_error(testY[0], testPredict[:, 0]))
print('Test Score: %.2f RMSE' % (testScore))

# Create year-month labels
year_month_labels = [ts.strftime('%Y-%b') for ts in dataframe.index]

# Plot the results
plt.plot(year_month_labels, scaler.inverse_transform(dataset), label='Original Data')
plt.plot(year_month_labels[look_back:len(trainPredict) + look_back], trainPredict, label='Train Predictions')
plt.plot(year_month_labels[len(trainPredict) + (look_back * 2) + 1:len(dataset) - 1], testPredict, label='Test Predictions')
plt.xlabel('Year-Month')
plt.ylabel('Scaled Values')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.legend()
plt.show()

