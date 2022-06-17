# PyGTide: A Python module and wrapper for ETERNA PREDICT 
# to compute gravitational tides on Earth
import pygtide
import datetime as dt
import numpy as np

# create a PyGTide object
pt = pygtide.pygtide()

# define a start date
start = dt.datetime(2018,1,1)

# calculate the gravitational tides 
latitude = 49.00937
longitude = 8.40444
height = 120
duration = 31*24
samplerate = 3600

# set the recommended wave groups
# as implemented in the wrapper
pt.set_wavegroup()

#pt.reset_wavegroup()
pt.predict(latitude, longitude, height, start, duration, samplerate, tidalcompo=-1)

# retrieve the results as dataframe
data = pt.results()

# output
print(data.iloc[0:10, 0:3])

# convert from UTC to a different time zone
data['UTC'].dt.tz_convert('Europe/Berlin')
