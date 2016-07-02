from collections import OrderedDict
import serial, yaml

class LoRaGateway(object):
    def __init__(self,
                 port, baudrate = 115200, timeout = 0.1, endl = "\n",
                 retries = 5,
                 ):
        self._ser = serial.Serial(port, baudrate = baudrate, timeout = timeout)
        self.endl = endl
        self.retries = retries
        self.pkt = None
        
    def _send_command(self, cmd):
        #remove any surrounding whitespace append the correct endl characters
        cmd = cmd.strip() + self.endl
        self._ser.write(cmd.encode())
        
    def _yaml_query(self, cmd, retries=None):
        if retries is None:
            retries = self.retries
        for i in range(1 + retries):
            self._send_command(cmd)
            doc = yaml.load(self._ser) #note this will always take at least one timeout period
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
        else:
            raise IOError("yaml_query failed max retries")
        
    def digital_read(self, pin):
        cmd = "DIGITAL.READ? %d" % pin
        pkt = self._yaml_query(cmd)
        assert(pkt['type'] == 'DIGITAL')
        return pkt['data']['state']  #return only the state value
        
    def digital_write(self, pin, state):
        state = bool(state)
        cmd = "DIGITAL.WRITE %d %d" % (pin,state)
        self._send_command(cmd)
        
    def analog_read(self, pin):
        cmd = "ANALOG.READ? %d" % pin
        pkt = self.yaml_query(cmd)
        assert(pkt['type'] == 'ANALOG')
        return pkt['data']['value'] #return only the state value
        
    def analog_write(self, pin, value):
        cmd = "ANALOG.WRITE %d %d" % (pin,value)
        self._send_command(cmd)

################################################################################
if __name__ == "__main__":
    import glob, time
    port = glob.glob("/dev/ttyACM*")[0]
    LG = LoRaGateway(port)
    #FIXME put test code here
    
