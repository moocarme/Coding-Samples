# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 09:43:42 2016

@author: matt-666
"""

from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import time

# Start timer
start_time = time.time()

# Load in csv file
city_data_py = pd.read_csv('data/GlobalLandTemperaturesByCity.csv') 

# Filter for city equal to 'New York'
city_data_US_py = city_data_py[city_data_py['City'] == 'New York']

# Filter for country equal to 'United States' 
city_data_US_py = city_data_US_py[city_data_US_py['Country'] == 'United States']  

# Select only 'datetime' and 'AverageTemperature' columns
city_data_US_py = city_data_US_py [['dt', 'AverageTemperature']]

# Remove NaN values
city_data_US_py = city_data_US_py[city_data_US_py['AverageTemperature'].notnull()]

# Convert datetime column to a pandas datetime series object 
city_data_US_py['dt'] = pd.Series(pd.to_datetime(city_data_US_py['dt']))

# Make new column as the year of the dt column
city_data_US_py['year'] = city_data_US_py['dt'].dt.year

# Group by year and take the mean
AvgTemp_US_py = city_data_US_py.groupby('year').mean()

# Create new column of the year
AvgTemp_US_py.index.name = 'Year'
AvgTemp_US_py.reset_index(inplace=True)

# Use scipy lingress function to perform linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(AvgTemp_US_py['Year'], \
    AvgTemp_US_py['AverageTemperature'])

# Create regression line
regressLine = intercept + AvgTemp_US_py['Year']*slope

# Regression using Theil-Sen with 95% confidence intervals 
res = stats.theilslopes(AvgTemp_US_py['AverageTemperature'], AvgTemp_US_py['Year'], 0.95)

# Scatter plot the temperature
plt.clf()
plt.scatter(AvgTemp_US_py['Year'], AvgTemp_US_py['AverageTemperature'], s = 3, label = 'Average Teamperature')

# Add least squares regression line
plt.plot(AvgTemp_US_py['Year'], regressLine, label = 'Least squares regression line'); 

# Add Theil-Sen regression line
plt.plot(AvgTemp_US_py['Year'], res[1] + res[0] * AvgTemp_US_py['Year'], 'r-', label = 'Theil-Sen regression line')

# Add Theil-Sen confidence intervals
plt.plot(AvgTemp_US_py['Year'], res[1] + res[2] * AvgTemp_US_py['Year'], 'r--', label = 'Theil-Sen 95% confidence interval')
plt.plot(AvgTemp_US_py['Year'], res[1] + res[3] * AvgTemp_US_py['Year'], 'r--')

# Add legend, axis limits and save to png
plt.legend(loc = 'upper left')
plt.ylim(7,14); plt.xlim(1755, 2016)
plt.savefig('pythonRegress.png')

# End timer
end_time = time.time()
print('Elapsed time = ' + str(end_time - start_time) + 'seconds')
