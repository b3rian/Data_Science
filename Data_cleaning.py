# This is my first data cleaning project in pandas

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
 
# Load the data
df = pd.read_csv('data.csv')

# Inspect the data
print(df.head())
print(df.info())
print(df.describe())

# Handle missing values
df = df.dropna()  # Drop rows with missing values
# or
df = df.fillna(method='ffill')  # Forward fill missing values

# Remove duplicates
df = df.drop_duplicates()

# Convert data types
df['column_name'] = df['column_name'].astype('int')

# Handle outliers
q1 = df['column_name'].quantile(0.25)
q3 = df['column_name'].quantile(0.75)
iqr = q3 - q1
df = df[(df['column_name'] >= (q1 - 1.5 * iqr)) & (df['column_name'] <= (q3 + 1.5 * iqr))]

# Normalize/standardize data
df['column_name'] = (df['column_name'] - df['column_name'].mean()) / df['column_name'].std()

# Save the cleaned data
df.to_csv('cleaned_data.csv', index=False)



