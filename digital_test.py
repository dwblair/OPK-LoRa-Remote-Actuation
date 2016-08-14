import time, glob
from lora_gateway import LoRaGateway
import json

DELAY_TIME = 1.0

port = glob.glob("/dev/ttyACM*")[0]

LG = LoRaGateway(port)
outfile = open("output.csv","w")

led_state = False

try:
    while True:
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
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print "# WARNING caught exception: %s" % exc
finally:
    outfile.close()

