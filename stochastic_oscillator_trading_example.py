# What is the ‘Stochastic Oscillator’
# The stochastic oscillator is a momentum indicator comparing the closing price of 
# a security to the range of its prices over a certain period of time. 
# The sensitivity of the oscillator to market movements is reducible by adjusting 
# that time period or by taking a moving average of the result.


#import relevant modules
import pandas as pd
import numpy as np
import csv
import datetime
from datetime import datetime, date, time
from dateutil.parser import parse
import matplotlib.pyplot as plt
import json
import requests

# read csv data into dataframe and convert dates to epoch timestamp

df = pd.read_csv("update2015111120180806.csv")
df.Date = pd.to_datetime(df.Date)
# print(df)

# print out first 5 rows of data DataFrame to check in correct format
# print(df.head())

#############################################################################
k = 90
d = 20
ds = 12
dss = 48

#Create the "L14" column in the DataFrame
df['L'] = df['bitcoin_Low'].rolling(window = k).min()
 
#Create the "H14" column in the DataFrame
df['H'] = df['bitcoin_High'].rolling(window = k).max()
 
#Create the "%K" column in the DataFrame
df['%K'] = 100*((df['bitcoin_Close'] - df['L']) / (df['H'] - df['L']) )
 
#Create the "%D" column in the DataFrame
df['%D'] = df['%K'].rolling(window = d).mean()

#Create the "%DS" column in the DataFrame
df['%DS'] = df['%D'].rolling(window = ds).mean()

#Create the "%DSS" column in the DataFrame
df['%DSS'] = df['%DS'].rolling(window = dss).mean()

print(df)

#############################################################################
#Create a plot showing Bitcoin price over time, along with visual representation of the Stochastic Oscillator
# fig, axes = plt.subplots(nrows=2, ncols=1,figsize=(20,10))

# df['bitcoin_Close'].plot(ax=axes[0]); axes[0].set_title('Bitcoin Price')
# df[['%K','%D']].plot(ax=axes[1]); axes[1].set_title('Oscillator')
# plt.show()


t  = df['Date']
y1 = df['bitcoin_Close']
y2 = df['L']
y3 = df['H']
s1 = df['%K']
s2 = df['%D']
s3 = df['%DS']
s4 = df['%DSS']

ax1 = plt.subplot(211)
plt.plot(t,y1,'.-')
plt.plot(t,y2)
plt.plot(t,y3)
plt.title('Bitcoin Price')

ax2 = plt.subplot(212)
plt.plot(t,s1)
plt.plot(t,s2)
plt.plot(t,s3)
plt.plot(t,s4)
plt.title('Oscillator')

plt.show()

#############################################################################

#Create a column in the DataFrame showing "TRUE" if sell entry signal is given and "FALSE" otherwise.
#A sell is initiated when the %K line crosses down through the %D line and the value of the oscillator is above 70
# df['Sell Entry'] = ((df['%K'] < df['%D']) & (df['%K'].shift(1) > df['%D'].shift(1))) & (df['%D'] > 70)
 
#Create a column in the DataFrame showing "TRUE" if sell exit signal is given and "FALSE" otherwise.
#A sell exit signal is given when the %K line crosses back up through the %D line
# df['Sell Exit'] = ((df['%K'] > df['%D']) & (df['%K'].shift(1) > df['%D'].shift(1))) 

#Create a placeholder column to polulate with short positions (-1 for short and 0 for flat) using boolean values created above 
# df['Short'] = np.nan 
# df.loc[df['Sell Entry'],'Short'] = -1 
# df.loc[df['Sell Exit'],'Short'] = 0 

#Set initial position on day 1 to flat 
# df.loc[0,'Short'] = 0 

#Forward fill the position column to represent the holding of positions through time 
# df['Short'] = df['Short'].fillna(method='pad') 

#Create a column in the DataFrame showing "TRUE" if buy entry signal is given and "FALSE" otherwise. 
#A buy is initiated when the %D line crosses above the %DS line 
df['Buy Entry'] = ((df['%D'] > df['%DS']) & (df['%D'].shift(1) < df['%DS'].shift(1))) 
 
#Create a column in the DataFrame showing "TRUE" if buy exit signal is given and "FALSE" otherwise.
#A buy exit signal is given when the %D line crosses back down through the %DS line
df['Buy Exit'] = ((df['%D'] < df['%DS']) & (df['%D'].shift(1) > df['%DS'].shift(1)))
 
#create a placeholder column to polulate with long positions (1 for long and 0 for flat) using boolean values created above
df['Long'] = np.nan 
df.loc[df['Buy Entry'],'Long'] = 1 
df.loc[df['Buy Exit'],'Long'] = 0 
 
#Set initial position on day 1 to flat
df.loc[0,'Long'] = 0 
 
#Forward fill the position column to represent the holding of positions through time
df['Long'] = df['Long'].fillna(method='pad')
 
#Add Long and Short positions together to get final strategy position (1 for long, -1 for short and 0 for flat)
df['Position'] = df['Long'] 

# print(df)
	
# df['Position'].plot(figsize=(20,10))
# plt.show()

#############################################################################

#Set up a column holding the daily bitcoin returns
df['Market_Returns'] = df['bitcoin_Close'].pct_change()
df['cum_mkt_returns'] = (1 + df['Market_Returns']).cumprod()
 
#Create column for Strategy Returns by multiplying the daily bitcoin returns by the position that was held at close
#of business the previous day
df['Strategy_Returns'] = df['Market_Returns'] * df['Position'].shift(1)
df['cum_strategy_returns'] = (1 + df['Strategy_Returns']).cumprod()

# print(df)
df.to_csv("result.csv",encoding='utf-8', index=False)
 
#Finally plot the strategy returns versus bitcoin returns
df[['cum_strategy_returns','cum_mkt_returns']].plot()
plt.show()