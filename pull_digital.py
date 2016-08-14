
import argparse
import time, glob
from lora_gateway import LoRaGateway
import json

parser = argparse.ArgumentParser(description='Read from serial and echomessage')

parser.add_argument('-d', '--device', default=glob.glob("/dev/ttyACM*")[0], help='path to serial device')

parser.add_argument('-r', '--rate', default=115200, help='rate of serial communication',type=int)

parser.add_argument('-o', '--outfile', default='output.csv', help='output file')

args = parser.parse_args()

port = args.device

rate = args.rate

outfile=str(args.outfile)

DELAY_TIME = 1.0

LG = LoRaGateway(port,rate)
outfile = open(outfile,"w")

led_state = False

try:
    LG.digital_read(10)
    time.sleep(DELAY_TIME)
    pkt = LG.pkt
    if not pkt is None:
        info = pkt.copy()
        
        rssi=pkt['RSSI']
        state=pkt['data']['state']
        pin=pkt['data']['pin']
        #print rssi,state,pin
        
        print json.dumps(pkt)
        
        #print(pkt['RSSI'],pkt['data'])
        
        outfile.write("{recv_timestamp},{RSSI},{data}\n".format(**info))
        outfile.flush()
    else:
        #chill out for a bit
        time.sleep(5)
except Exception as exc:
    print "# WARNING caught exception: %s" % exc
finally:
    outfile.close()

