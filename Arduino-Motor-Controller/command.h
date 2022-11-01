
#ifndef COMMAND_H_
#define COMMAND_H_

#include <stdbool.h>
#include <stdint.h>

#define CMD_HEADER_ACK 0x01
#define CMD_HEADER_SET_VELOCITY 0xA0
#define CMD_HEADER_REQUEST_ACK 0xA1
#define CMD_HEADER_SET_LIGHT 0xA2

#define CMD_LENGTH_ACK 0u
#define CMD_LENGTH_SET_VELOCITY 6u      // [forward -1000-1000] [right -1000-1000] [clockwise -1000-1000]
#define CMD_LENGTH_REQUEST_ACK  0u
#define CMD_LENGTH_SET_LIGHT  3u   // [r 0-255, g 0-255, b 0-255]

typedef struct Packet {
    uint8_t header;
    uint8_t length;
    uint8_t *data;
} Packet;

void
Command_Initialize(void);

void
Command_sendData(Packet *packet);

void
Command_readToQueue(void);

int
Command_parseQueue(Packet *packet);

#endif /* COMMAND_H_ */
