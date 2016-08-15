# OPK-LoRa-Remote-Actuation

### Firmware prep
- Download all files into a directory
- Load "basestation_firmware/basetation_firmware.ino" onto the "base" M0 LoRa Feather
- Load "remote_firmware/remote_firmware.ino" onto the "remote" M0 LoRa Feather

### Hardware prep
- Power the "remote" node via battery or USB (avoid using USB from your laptop, as serial port conflicts seem to occur).
- Make sure no other programs are accessing serial ports currently (might not be necessary)
- Plug the "base" node into a USB port on your computer via microUSB cable

### Permissions

- Set file permissions so that 'blink_led' and 'pull_analog_sleep' are executable
- On Linux this can be done via:

```
chmod 755 filename
```
 
### Blinking LED

Try the command:

```bash 
sudo ./blink_led
``` 

### Analog readings

Try the command:

```bash
sudo ./pull_analog_sleep
```
