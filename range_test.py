import time, glob
import serial, yaml

DELAY_TIME = 1.0

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

def cmd_gen():
    while True:
        yield "LED.ON\n".encode()
        yield "LED.OFF\n".encode()

gCmd = cmd_gen()

try:
    while True:
        try:
            ser.write(gCmd.next())
            time.sleep(DELAY_TIME)
            reply = exchange_yaml("LED?\n")
            time.sleep(DELAY_TIME)
            print reply
            if not reply is None:
                data = reply['LED']
                outfile.write("{recv_timestamp},{RSSI}\n".format(**data))
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

