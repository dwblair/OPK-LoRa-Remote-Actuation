import pandas as pd # nice data utilities
import os, sys
import numpy as np
import matplotlib.pyplot as plt # getting specific plotting functions



fname1 = sys.argv[1]
fname2 = sys.argv[2]
print "GPS file (.csv):",fname1
print "RSSI log (.csv):",fname2

gps_track = pd.read_table(fname1, 
                          header = 0,
                          sep    = ',',
                          names  = ['time','lat','lon','ele','x:speed']
                         );



radio_log = pd.read_table(fname2,
                          header = 0,
                          sep    = ',',
                          names  = ['timestamp','rssi']
                         );

gps_seconds   = gps_track.time - gps_track.time[0]
radio_seconds = radio_log.timestamp - radio_log.timestamp[0]

avg_sRs = []    #this will hold the RSSI signal average over the interval
std_sRs = []    #this will hold the RSSI signal standard deviation over the interval
group_sRs = []  #used to temporarily group data in an interval
iR = 0          #index into radio data array
#each GPS time will be the righthand bound of the interval
tR = radio_seconds[iR]
for tG in gps_seconds:
    print tG,iR,tR
    try:
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
    except KeyError, exc:
        print "Warning caught exception: ", exc

avg_sRs = np.array(avg_sRs)
std_sRs = np.array(std_sRs)
print(len(avg_sRs))
fig = plt.figure(figsize=(8,2))
plt.errorbar(gps_seconds, avg_sRs, yerr = std_sRs, fmt = '.')

# save the data by extending the pandas dataframe

gps_track['RSSI'] = avg_sRs
gps_track['RSSI_err'] = std_sRs
#generate new filename
base, ext = os.path.splitext(fname1)
new_fname = "%s_GPS-RSSI.csv" % base
gps_track.to_csv(new_fname)
