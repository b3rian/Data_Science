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



