from xml.dom.minidom import parseString
from datetime import datetime
from dateutil import tz
import os

#convert from GPS time (UTC) to our local time zone
from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/New_York')  #Eastern Standard Time (EST)

fname = './2016-06-18_PVD_LoRa_Track-160619-131701.gpx'
doc = open(fname).read()
dom = parseString(doc)

pts = dom.getElementsByTagName('trkpt')

csv_lines = []
for pt in pts:
    line = []
    #timestamp
    time_str = pt.getElementsByTagName("time")[0].firstChild.data
    gps_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_dt = gps_dt.replace(tzinfo=from_zone)
    est_dt = utc_dt.astimezone(to_zone)
    ts = est_dt.strftime("%s") #convert to Unix Epoch seconds
    line.append(ts)
    #lattitude
    line.append(pt.attributes['lat'].value)
    #longitude
    line.append(pt.attributes['lon'].value)
    #elevation
    line.append(pt.getElementsByTagName("ele")[0].firstChild.data)
    #speed
    line.append(pt.getElementsByTagName("x:speed")[0].firstChild.data)
    #format and append line
    csv_lines.append(",".join(line))
    
#finish up by smashing all the lines together
csv_string = "\n".join(csv_lines)

#save the data in a suitably named file
base, ext = os.path.splitext(fname)
csv_filename = "%s.csv" % base
outfile = open(csv_filename, 'w')
outfile.write(csv_string)
outfile.close()
