# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 09:43:42 2016

@author: matt-666
"""

from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import time


class analyse_temp_data(object):
    
    def __init__(self, filename):
        self.dataset = pd.read_csv(filename) # Load in csv file

    def clean_data(self):
        
        # Filter for city equal to 'New York' and country equal to 'United States' 
        city_data_US_py = self.dataset[(self.dataset['City'] == 'New York') & 
                                       (self.dataset['Country'] == 'United States')]

        # Select only 'datetime' and 'AverageTemperature' columns
        city_data_US_py = city_data_US_py[['dt', 'AverageTemperature']]

        # Remove NaN values
        city_data_US_py = city_data_US_py[city_data_US_py['AverageTemperature'].notnull()]

        # Convert datetime column to a pandas datetime series object 
        city_data_US_py['dt'] = pd.Series(pd.to_datetime(city_data_US_py['dt']))
        
        # Make new column as the year of the dt column
        city_data_US_py['year'] = city_data_US_py['dt'].dt.year
        
        # Group by year and take the mean
        self.AvgTemp_US_py = city_data_US_py.groupby('year').mean()

        # Create new column of the year
        self.AvgTemp_US_py.index.name = 'Year'
        self.AvgTemp_US_py.reset_index(inplace=True)
        
    def regress(self):
        '''
        Use scipy lingress function to perform linear regression      
        ''' 
        slope, intercept, r_val, p_val, std_err = stats.linregress(self.AvgTemp_US_py['Year'], \
                                                                       self.AvgTemp_US_py['AverageTemperature'])

        # Create regression line
        self.regressLine = intercept + self.AvgTemp_US_py['Year']*slope
        
        # Regression using Theil-Sen with 95% confidence intervals 
        self.res = stats.theilslopes(self.AvgTemp_US_py['AverageTemperature'], self.AvgTemp_US_py['Year'], 0.95)

        
    def plot(self):
        '''
        Plot the data plus regression line
        '''
        # Scatter plot the temperature
        plt.figure()
        plt.scatter(self.AvgTemp_US_py['Year'], self.AvgTemp_US_py['AverageTemperature'], 
                    s = 3, label = 'Average Teamperature')
        
        # Add least squares regression line
        plt.plot(self.AvgTemp_US_py['Year'], self.regressLine, label = 'Least squares regression line'); 
        
        # Add Theil-Sen regression line
        plt.plot(self.AvgTemp_US_py['Year'], self.res[1] + self.res[0] * self.AvgTemp_US_py['Year'], 
                 'r-', label = 'Theil-Sen regression line')
        
        # Add Theil-Sen confidence intervals
        plt.plot(self.AvgTemp_US_py['Year'], self.res[1] + self.res[2] * self.AvgTemp_US_py['Year'], 
                 'r--', label = 'Theil-Sen 95% confidence degree')
        plt.plot(self.AvgTemp_US_py['Year'], self.res[1] + self.res[3] * self.AvgTemp_US_py['Year'], 
                 'r--')
        
        # Add legend, axis limits and save to png
        plt.legend(loc = 'upper left')
        plt.ylim(7,14); plt.xlim(1755, 2016)
        plt.savefig('pythonRegression.png')


if __name__ == '__main__':
    start_time = time.time() # Start timer
    filename = 'data/GlobalLandTemperaturesByCity.csv'
    
    data_analysis = analyse_temp_data(filename) # initialize with file
    data_analysis.clean_data()                  # clean, filter, and aggregate
    data_analysis.regress()                     # linear regression with bands
    data_analysis.plot()                        # plot
    print 'Elapsed time = %.2f seconds' % (time.time() - start_time)
