#include <PacketCommand.h>
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>
#include "pCmd_RHRD_RF95_module.h"

#include <SerialCommand.h>

//#include <FreqCount.h>

//uncomment for debugging messages
//#define DEBUG

#ifdef DEBUG
  #define DEBUG_PORT Serial
#endif

#define LED_pin 13   // Arduino LED on board

//Serial Interface for Testing over FDTI
SerialCommand sCmd(Serial);

#define PACKETCOMMAND_MAX_COMMANDS 20
#define PACKETCOMMAND_INPUT_BUFFER_SIZE 32
#define PACKETCOMMAND_OUTPUT_BUFFER_SIZE 32
PacketCommand pCmd_RHRD(PACKETCOMMAND_MAX_COMMANDS,
                        PACKETCOMMAND_INPUT_BUFFER_SIZE,
                        PACKETCOMMAND_OUTPUT_BUFFER_SIZE);

#define BASESTATION_ADDRESS 1
#define DEFAULT_REMOTE_ADDRESS 2
//******************************************************************************
// Setup
void setup() {
  pinMode(LED_pin, OUTPUT);      // Configure the onboard LED for output
  digitalWrite(LED_pin, LOW);     // default to LED off
  //FreqCount.begin(1000); //this is the gateing interval/duration of measurement
  
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // Setup callbacks for SerialCommand commands
  sCmd.addCommand("LED?",        LED_sCmd_query_handler);         // reads input frequency
  sCmd.addCommand("LED.ON",      LED_ON_sCmd_action_handler);          // Turns LED on
  sCmd.addCommand("LED.OFF",     LED_OFF_sCmd_action_handler);         // Turns LED off
  //sCmd.addCommand("FREQ1.READ?", FREQ1_READ_sCmd_query_handler);         // reads input frequency
  sCmd.setDefaultHandler(UNRECOGNIZED_sCmd_handler);      // Handler for command that isn't matched  (says "What?")
  #ifdef DEBUG
  DEBUG_PORT.println(F("# SerialCommand Ready"));
  #endif
  
  // Setup callbacks for PacketCommand requests
  //pCmd_RHRD.addCommand((byte*) "\xFF\x11","FREQ1.READ?", NULL);
  pCmd_RHRD.addCommand((byte*) "\xFF\x40","LED?",      NULL);
  pCmd_RHRD.addCommand((byte*) "\xFF\x41","LED.ON",      NULL);
  pCmd_RHRD.addCommand((byte*) "\xFF\x42","LED.OFF",     NULL);
  //Setup callbacks for PacketCommand replies
  //pCmd_RHRD.addCommand((byte*) "\x11","FREQ1!",          FREQ1_pCmd_reply_handler);
  pCmd_RHRD.addCommand((byte*) "\x40","LED!",            LED_pCmd_reply_handler);
  //pCmd.registerDefaultHandler(unrecognized);                          // Handler for command that isn't matched  (says "What?")
  pCmd_RHRD.registerRecvCallback(pCmd_RHRD_recv_callback);
  pCmd_RHRD.registerSendCallback(pCmd_RHRD_send_callback);
  
  //configure the pCmd_RHRD_RF95_module
  pCmd_RHRD_module_setup(BASESTATION_ADDRESS,
                         PCMD_RHRD_DEFAULT_FREQUENCY,
                         PCMD_RHRD_DEFAULT_TX_POWER,
                         PCMD_RHRD_DEFAULT_NUM_RETRIES
                         );
                         
  //configure the default node address
  pCmd_RHRD.setOutputToAddress(DEFAULT_REMOTE_ADDRESS);
}

//******************************************************************************
// Main Loop

void loop() {
  int num_bytes = sCmd.readSerial();      // fill the buffer
  
  if (num_bytes > 0){
    sCmd.processCommand();  // process the command
  }
  
  //process incoming radio packets
  pCmd_RHRD_module_proccess_input(pCmd_RHRD);
  
  delay(10);
}

//******************************************************************************
// SerialCommand handlers

//void FREQ1_READ_sCmd_query_handler(SerialCommand this_sCmd) {
//  pCmd_RHRD.resetOutputBuffer();
//  pCmd_RHRD.setupOutputCommandByName("FREQ1.READ?");
//  pCmd_RHRD.send();
//}

void LED_sCmd_query_handler(SerialCommand this_sCmd) {
  pCmd_RHRD.resetOutputBuffer();
  pCmd_RHRD.setupOutputCommandByName("LED?");
  pCmd_RHRD.send();
}

void LED_ON_sCmd_action_handler(SerialCommand this_sCmd) {
  pCmd_RHRD.resetOutputBuffer();
  pCmd_RHRD.setupOutputCommandByName("LED.ON");
  pCmd_RHRD.send();
}

void LED_OFF_sCmd_action_handler(SerialCommand this_sCmd) {
  pCmd_RHRD.resetOutputBuffer();
  pCmd_RHRD.setupOutputCommandByName("LED.OFF");
  pCmd_RHRD.send();
}


// This gets set as the default handler, and gets called when no other command matches.
void UNRECOGNIZED_sCmd_handler(SerialCommand this_sCmd) {
  SerialCommand::CommandInfo command = this_sCmd.getCurrentCommand();
  Serial.print(F("# Did not recognize \""));
  Serial.print(command.name);
  Serial.println(F("\" as a command."));
}
//******************************************************************************
// PacketCommand handlers

//void FREQ1_pCmd_reply_handler(PacketCommand& this_pCmd){
//  uint32_t count;
//  this_pCmd.unpack_uint32(count);
//  PacketCommand::InputProperties input_props = this_pCmd.getInputProperties();
//  //CSV
//  Serial.println(count);
//  //YAML
//  Serial.println(F("---"));
//  Serial.println(F("FREQ1:"));
//  Serial.print(F("  count:          "));Serial.println(count);
//  Serial.print(F("  recv_timestamp: "));Serial.println(input_props.recv_timestamp);
//  Serial.print(F("  from_addr:      "));Serial.println(input_props.from_addr);
//  Serial.print(F("  RSSI:           "));Serial.println(input_props.RSSI);
//}

void LED_pCmd_reply_handler(PacketCommand& this_pCmd){
  bool state;
  this_pCmd.unpack_byte((byte&) state);  //updated by reference
  PacketCommand::InputProperties input_props = this_pCmd.getInputProperties();
  //CSV
  //Serial.println(state);
  //YAML
  Serial.println(F("---"));
  Serial.println(F("LED:"));
  Serial.print(F("  state:          "));Serial.println(state);
  Serial.print(F("  recv_timestamp: "));Serial.println(input_props.recv_timestamp);
  Serial.print(F("  from_addr:      "));Serial.println(input_props.from_addr);
  Serial.print(F("  RSSI:           "));Serial.println(input_props.RSSI);
}

