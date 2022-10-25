#include "Arduino.h"
#include "command.h"

#define RX_BUFFER_SIZE 128

static uint8_t _rxQueue[RX_BUFFER_SIZE];
static uint8_t _rxQueue_head;
static uint8_t _rxQueue_length;

void
Command_Initialize() {
	Serial.begin(115200);

	_rxQueue_head   = 0;
	_rxQueue_length = 0;
}

void
Command_sendData(Packet *packet) {
	int checkSum = 0;
	int i;

	Serial.write(0xFE);
	checkSum += 0xFE;

	Serial.write(packet->header);
	checkSum += packet->header;

	Serial.write(packet->length);
	checkSum += packet->length;

	for (i = 0; i < packet->length; i++) {
		Serial.write(packet->data[i]);
		checkSum += packet->data[i];
	}

	Serial.write(checkSum);
}

void
Command_readToQueue() {
	uint8_t index;

	while (Serial.available() > 0 && _rxQueue_length < RX_BUFFER_SIZE) {
		index           = (_rxQueue_head + _rxQueue_length) % RX_BUFFER_SIZE;
		_rxQueue[index] = Serial.read();
		_rxQueue_length++;
	}
}

int
Command_parseQueue(Packet *packet) {
	int rv;
	uint8_t header;
	uint8_t target_id;
	uint8_t length;
	uint8_t checkSum;
	uint8_t checkSumCalc;
	uint8_t index;
	int i = 0;

	// find start of a packet
	while (_rxQueue_length > 0 && _rxQueue[_rxQueue_head] != 0xFE) {
		// pop the head
		_rxQueue_head = (_rxQueue_head + 1) % RX_BUFFER_SIZE;
		_rxQueue_length--;
	}

	if (_rxQueue_length < 4) {
		rv = 1;
		goto exit;
	}

	header = _rxQueue[(_rxQueue_head + 1) % RX_BUFFER_SIZE];
	length = _rxQueue[(_rxQueue_head + 2) % RX_BUFFER_SIZE];

	if (length > 10)
		length = 10;

	// ensure packet is long enough
	if (_rxQueue_length < (length + 4)) {
		rv = 1;
		goto exit;
	}

	checkSum     = _rxQueue[(_rxQueue_head + 3 + length) % RX_BUFFER_SIZE];
	checkSumCalc = 0;

	for (index = 0; index < length + 3; index++) {
		checkSumCalc += _rxQueue[(_rxQueue_head + index) % RX_BUFFER_SIZE];
	}

	if (checkSum != checkSumCalc) {
		// pop the head
		// the next iteration will find the start of the next packet
		_rxQueue_head = (_rxQueue_head + 1) % RX_BUFFER_SIZE;
		_rxQueue_length--;


		rv = 1;

		goto exit;
	}

	// packet valid, copy to return struct
	packet->header = header;
	packet->length = length;
	for (i = 0; i < packet->length; i++) {
		packet->data[i] = _rxQueue[(_rxQueue_head + 3 + i) % RX_BUFFER_SIZE];
	}

	// pop the entire packet from the queue
	_rxQueue_head = (_rxQueue_head + 4 + length) % RX_BUFFER_SIZE;
	_rxQueue_length -= 4 + length;

	rv = 0;

exit:

	return rv;
}
