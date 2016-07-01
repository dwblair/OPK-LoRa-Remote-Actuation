import time, glob
import serial, yaml

DELAY_TIME = 1.0
VBAT_PIN = 9 #D9 aka A7 on Feather M0 is connect to the JST battery input

port = glob.glob("/dev/ttyACM*")[0]
ser = serial.Serial(port, baudrate=115200)

def exchange_yaml(cmd):
    ser.write(cmd.encode())
    lines = []
    while ser.inWaiting():
        line = ser.readline()
        line = line.strip("\r\n")
        print(line)
        if not line.startswith("#"):
            lines.append(line)
    doc = "\n".join(lines)
    reply = yaml.load(doc)
    return reply

outfile = open("output.csv","w")



try:
    while True:
        try:
            reply = exchange_yaml("ANALOG.READ? %d\n" % VBAT_PIN)
            time.sleep(DELAY_TIME)
            print reply
            if not reply is None:
                data = reply['ANALOG']
                val = data['value']
                data['battery_voltage'] = 2*3.3*val/1024.0
                print "# computed battery voltage:",data['battery_voltage']
                outfile.write("{recv_timestamp},{RSSI},{'battery_voltage'}\n".format(**data))
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

