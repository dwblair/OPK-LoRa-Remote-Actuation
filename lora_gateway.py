from collections import OrderedDict
import time
import serial, yaml

DEBUG = False
DEBUG = True

class LoRaGateway(object):
    def __init__(self,
                 port, baudrate = 115200, timeout = 5.0, endl = "\n",
                 retries = 5,
                 retry_delay = 1.0,
                 ):
        self._ser = serial.Serial(port, baudrate = baudrate, timeout = timeout)
        self.endl = endl
        self.retries = retries
        self.retry_delay = retry_delay
        self.pkt = None
        
    def _send_command(self, cmd):
        #remove any surrounding whitespace append the correct endl characters
        cmd = cmd.strip() + self.endl
        self._ser.write(cmd.encode())
        #check to see if command has succeeded
        while True:
            line = self._ser.readline()
            line = line.decode('utf-8') #needed for Python 3, bytes to string conversion
            if not line.startswith("#"):
                if line.startswith("OK"):
                    return True
                elif line.startswith("FAIL"):
                    return False
                else:
                    raise IOError("got invalid line in _send_command: %s" % line)
        
    def _parse_yaml(self):
        buff = []
        inside_doc = False
        while True:
            line = self._ser.readline()
            line = line.decode('utf-8') #needed for Python 3, bytes to string conversion
            if line == "": #timeout has occured
                print("# Warning timed-out waiting for serial.readline")
                return None
            line = line.strip("\r\n")
            print(line)
            if not line.startswith("#"):
                buff.append(line)
            if inside_doc:
                if line.startswith("---"):
                    inside_doc = True
                    print("#ending doc")
                    break
                elif line.startswith("..."):
                    inside_doc = False
                    print("#ending doc")
                    break
            elif line.startswith("---"):
                inside_doc = True
                print("#starting doc")
        buff = "\n".join(buff)
        doc = yaml.load(buff) #note this will always take at least one timeout period
        return doc
 
    def _yaml_query(self, cmd, retries=None):
        if retries is None:
            retries = self.retries
        #clear out the buffer
        self._ser.flush()
        for i in range(1 + retries):
            success = self._send_command(cmd)
            if not success:
                continue #cycle back for another try
            doc = self._parse_yaml()
            if not doc is None:
                self.pkt = OrderedDict()
                assert(len(doc.keys()) == 1)
                self.pkt['type'] = list(doc.keys())[0]
                info = doc[self.pkt['type']]
                self.pkt['from_addr']      = info.pop('from_addr')
                self.pkt['recv_timestamp'] = info.pop('recv_millis',0)/1000.0
                self.pkt['RSSI']           = info.pop('RSSI',0)
                self.pkt['retry_attempt']  = i
                self.pkt['data']           = info
                return self.pkt
            #got nothing or incomplete document, flush and try again
            self._ser.flush()
            time.sleep(self.retry_delay)
            if DEBUG:
                print("# Retry #%d" % (i+1))
        else:
            self.pkt = None
            raise IOError("yaml_query failed max retries")
        
    def digital_read(self, pin):
        cmd = "DIGITAL.READ? %d" % pin
        pkt = self._yaml_query(cmd)
        assert(pkt['type'] == 'DIGITAL')
        return bool(pkt['data']['state'])  #return only the state value
        
    def digital_write(self, pin, state):
        state = bool(state)
        cmd = "DIGITAL.WRITE %d %d" % (pin,state)
        self._send_command(cmd)
        
    def analog_read(self, pin):
        cmd = "ANALOG.READ? %d" % pin
        pkt = self._yaml_query(cmd)
        assert(pkt['type'] == 'ANALOG')
        return pkt['data']['value'] #return only the state value
        
    def analog_write(self, pin, value):
        cmd = "ANALOG.WRITE %d %d" % (pin,value)
        self._send_command(cmd)
        
    def set_LED(self,state):
        if state == "ON" or state is True:
            state = "ON"
        elif state == "OFF" or state is False:
            state = "OFF"
        else:
            raise ValueError("State must be either ['ON',True] or ['OFF',False]")
        cmd = "LED.%s" % state
        self._send_command(cmd)
        
    def get_LED(self):
        cmd = "LED?"
        pkt = self._yaml_query(cmd)
        assert(pkt['type'] == 'LED')
        return bool(pkt['data']['state']) #return only the state value

################################################################################
if __name__ == "__main__":
    import glob, time
    port = glob.glob("/dev/ttyACM*")[0]
    LG = LoRaGateway(port)
    #FIXME put test code here
    
