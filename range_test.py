import time, glob
from lora_gateway import LoRaGateway

DELAY_TIME = 1.0

port = glob.glob("/dev/ttyACM*")[0]

LG = LoRaGateway(port)
outfile = open("output.csv","w")

led_state = False
try:
    while True:
        try:
            led_state ^= True #toggle LED state
            LG.set_LED(led_state)
            time.sleep(DELAY_TIME)
            LG.get_LED()
            time.sleep(DELAY_TIME)
            #get all the packet info
            pkt = LG.pkt
            if not pkt is None:
                info = pkt.copy()
                print("---")
                for k, v in info.items():
                    print("%s: %s" % (k,v))
                outfile.write("{recv_timestamp},{RSSI}\n".format(**info))
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

