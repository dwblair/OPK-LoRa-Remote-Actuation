import pandas as pd # nice data utilities
import os
import numpy as np
import matplotlib.pyplot as plt # getting specific plotting functions



fname = '2016-06-18_PVD_LoRa_Track-160619-131701.csv' #this file is created by running gpx_to_csv.py
gps_track = pd.read_table(fname, 
                          header = 0,
                          sep    = ',',
                          names  = ['time','lat','lon','ele','x:speed']
                         );



radio_log = pd.read_table('2016-06-18_PVD_LoRa_range_test.csv',
                          header = 0,
                          sep    = ',',
                          names  = ['millis','rssi']
                         );

gps_seconds   = gps_track.time - gps_track.time[0]
radio_seconds = (radio_log.millis - radio_log.millis[0])/1e3

avg_sRs = []    #this will hold the RSSI signal average over the interval
std_sRs = []    #this will hold the RSSI signal standard deviation over the interval
group_sRs = []  #used to temporarily group data in an interval
iR = 0          #index into radio data array
#each GPS time will be the righthand bound of the interval
tR = radio_seconds[iR]
for tG in gps_seconds:
    while tR < tG :
        iR += 1  #move the interval to the right
        tR = radio_seconds[iR]
        group_sRs.append(radio_log.rssi[iR])
    #finish calculating this interval
    if len(group_sRs) == 0: #empty interval means radio dropout
        avg_sRs.append(np.NaN)
        std_sRs.append(0)
    else:
        avg_sRs.append(np.mean(group_sRs))
        std_sRs.append(np.std(group_sRs))
    #begin new interval
    group_sRs = []

avg_sRs = np.array(avg_sRs)
std_sRs = np.array(std_sRs)
print(len(avg_sRs))
fig = plt.figure(figsize=(8,2))
plt.errorbar(gps_seconds, avg_sRs, yerr = std_sRs, fmt = '.')

# save the data by extending the pandas dataframe

gps_track['RSSI'] = avg_sRs
gps_track['RSSI_err'] = std_sRs
#generate new filename
base, ext = os.path.splitext(fname)
new_fname = "%s_GPS-RSSI.csv" % base
gps_track.to_csv(new_fname)
