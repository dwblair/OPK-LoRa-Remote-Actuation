#include <PacketCommand.h>
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>

//******************************************************************************
#ifndef PCMD_RHRD_RF95_MODULE_INCLUDE
#define PCMD_RHRD_RF95_MODULE_INCLUDE

//uncomment for debugging messages
//#define DEBUG

#ifdef DEBUG
  #define DEBUG_PORT Serial
#endif

//******************************************************************************
// Setup

#define PCMD_RHRD_DEFAULT_FREQUENCY 915
#define PCMD_RHRD_DEFAULT_TX_POWER 23
#define PCMD_RHRD_DEFAULT_NUM_RETRIES 10
#define PCMD_RHRD_DEFAULT_TIMEOUT 2000

void pCmd_RHRD_module_setup(uint8_t this_address,
                            unsigned int radio_frequency,
                            unsigned int tx_power,
                            unsigned int num_retries,
                            uint16_t timeout_millis
                            );


void radiosleep();
void radiowake();

//******************************************************************************
extern PacketShared::STATUS pCmd_status;
bool pCmd_RHRD_module_proccess_input(PacketCommand& this_pCmd);
//******************************************************************************
// PacketCommand callbacks
bool pCmd_RHRD_recv_callback(PacketCommand& this_pCmd);
bool pCmd_RHRD_send_callback(PacketCommand& this_pCmd);


#endif /*PCMD_RHRD_RF95_MODULE_INCLUDE*/
//******************************************************************************
