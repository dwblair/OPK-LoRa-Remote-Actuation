import time, glob
from lora_gateway import LoRaGateway

DEBUG = True

DELAY_TIME = 1.0
VBAT_PIN = 9 #D9 aka A7 on Feather M0 is connect to the JST battery input

port = glob.glob("/dev/ttyACM*")[0]
LG = LoRaGateway(port)
outfile = open("output.csv","w")
try:
    while True:
        try:
            value = LG.analog_read(VBAT_PIN)
            time.sleep(DELAY_TIME)
            #get all the packet info
            pkt = LG.pkt
            info = pkt.copy()
            info['battery_voltage'] = 2*3.3*value/1024.0
            print("---")
            for k, v in info.items():
                print("%s: %s" % (k,v))
            outfile.write("{recv_timestamp},{RSSI},{battery_voltage}\n".format(**info))
            outfile.flush()
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print("# WARNING caught exception: %s" % exc)
            if DEBUG:
                raise
finally:
    outfile.close()

