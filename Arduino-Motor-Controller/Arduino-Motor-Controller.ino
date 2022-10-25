
/* Hardware Configuration:
    - Add jumper to set SpinEnable to PIN_X_LIM
    - Add jumper to set SpinDir to A-DIR
    - Configure max current potentiometer on each driver to 0.8A
        https://ardufocus.com/howto/a4988-motor-current-tuning/
        Make sure to confirm sensing resitor value
        Vref = 0.8A * 8 * 0.1ohm = 0.64V
    - Attach Neopixel Jumpers
        - 5V to 5V
        - GND to GND
        - DIN to SDA

   Hardware Notes:
    - Stepper Motor (17HS4023):
        - NEMA 17
        - 1.8° step angle -> 200 steps/rev
        - Rated Voltage: 4.1V
        - Rated Current: 1.0A
        - Max 1400 PPS
*/

#include <Adafruit_NeoPixel.h>
#include <FastGPIO.h>

#include "command.h"

// Motor Driver Properties
#define MAX_PPS 1000
#define PULSE_WIDTH_US (1000000 / MAX_PPS / 2)
#define PULSE_WIDTH_COMPENSATION_OFFSET_US 40

// A4988 Shield
#define PIN_A4988_EN 8  // enable pin across all drivers
#define PIN_Y_DIR 6     // BR
#define PIN_A_DIR 13    // FR
#define PIN_X_DIR 5     // BL
#define PIN_Z_DIR 7     // BR
#define PIN_Y_STP 3
// #define PIN_A_STP 12
#define PIN_X_STP 2
#define PIN_Z_STP 4

#define PIN_RX 0  // Serial
#define PIN_TX 1  // Serial

#define PIN_X_LIM 9            // NC
#define PIN_Y_LIM 10           // NC
#define PIN_Z_LIM 11           // NC
#define PIN_RESET_ABORT A0     // NC
#define PIN_FEED_HOLD A1       // NC
#define PIN_CYCLE_START A2     // NC
#define PIN_COOLANT_ENABLE A3  // NC
#define PIN_SCL A4             // NC
#define PIN_SDA A5             // Using as Neopixel Data

#define PIN_A_STP PIN_X_LIM

// Neopixels
#define PIN PIN_SDA
#define NUMPIXELS 4

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// [-1000, 1000]
uint16_t _velocity_fl = 0;
uint16_t _velocity_fr = 0;
uint16_t _velocity_bl = 0;
uint16_t _velocity_br = 0;

// FL, FR, BL, BR
uint32_t _last_pulse_us[4] = {0, 0, 0, 0};
bool _pulse_high[4]        = {false, false, false, false};

uint8_t _tx_data[32];

void
setup() {
	uint8_t i;

	Command_Initialize();

	pinMode(PIN_A4988_EN, OUTPUT);

	// start reset
	digitalWrite(PIN_A4988_EN, HIGH);

	FastGPIO::Pin<PIN_Y_DIR>::setOutputLow();
	FastGPIO::Pin<PIN_A_DIR>::setOutputLow();
	FastGPIO::Pin<PIN_X_DIR>::setOutputLow();
	FastGPIO::Pin<PIN_Z_DIR>::setOutputLow();
	FastGPIO::Pin<PIN_Y_STP>::setOutputLow();
	FastGPIO::Pin<PIN_A_STP>::setOutputLow();
	FastGPIO::Pin<PIN_X_STP>::setOutputLow();
	FastGPIO::Pin<PIN_Z_STP>::setOutputLow();

	pinMode(PIN_X_LIM, INPUT);
	pinMode(PIN_Y_LIM, INPUT);
	pinMode(PIN_Z_LIM, INPUT);
	pinMode(PIN_RESET_ABORT, INPUT);
	pinMode(PIN_FEED_HOLD, INPUT);
	pinMode(PIN_CYCLE_START, INPUT);
	pinMode(PIN_COOLANT_ENABLE, INPUT);
	pinMode(PIN_SCL, INPUT);
	pinMode(PIN_SDA, INPUT);

	pixels.begin();
	for (i = 0; i < NUMPIXELS; i++) {
		pixels.setPixelColor(i, pixels.Color(255, 255, 255));
		pixels.setBrightness(255);
	}
	pixels.show();

	delay(50);

	// end reset
	digitalWrite(PIN_A4988_EN, LOW);
}

void
task_motor_control() {
	// FL, FR, BL, BR
	uint16_t speed[4];
	bool digital_output[4];
	uint32_t time_micros = micros();
	uint8_t i;

	speed[0] = abs(_velocity_fl);
	speed[1] = abs(_velocity_fr);
	speed[2] = abs(_velocity_bl);
	speed[3] = abs(_velocity_br);

	// Set direction
	FastGPIO::Pin<PIN_Z_DIR>::setOutput(_velocity_fl < 0 ? HIGH : LOW);
	FastGPIO::Pin<PIN_X_DIR>::setOutput(_velocity_fr > 0 ? HIGH : LOW);
	FastGPIO::Pin<PIN_A_DIR>::setOutput(_velocity_bl < 0 ? HIGH : LOW);
	FastGPIO::Pin<PIN_Y_DIR>::setOutput(_velocity_br > 0 ? HIGH : LOW);

	for (i = 0; i < 4; i++) {
		speed[i] = constrain(speed[i], 0, 1000);

		if (speed[i] == 0) {
			digital_output[i] = false;
		} else {
			// is it time to pulse?
			// or is the pulse high and it's time to turn it off?
			if (time_micros - _last_pulse_us[i] +
			            PULSE_WIDTH_COMPENSATION_OFFSET_US >=
			        PULSE_WIDTH_US * 2 * 1000 / speed[i] &&
			    !_pulse_high[i]) {
				digital_output[i] = true;
				_last_pulse_us[i] = time_micros;
			} else if (_pulse_high[i] &&
			           time_micros - _last_pulse_us[i] >= PULSE_WIDTH_US) {
				digital_output[i] = false;
			} else {
				digital_output[i] = _pulse_high[i];
			}
		}
	}

	// Set outputs
	FastGPIO::Pin<PIN_Z_STP>::setOutput(digital_output[0] ? HIGH : LOW);
	FastGPIO::Pin<PIN_X_STP>::setOutput(digital_output[1] ? HIGH : LOW);
	FastGPIO::Pin<PIN_A_STP>::setOutput(digital_output[2] ? HIGH : LOW);
	FastGPIO::Pin<PIN_Y_STP>::setOutput(digital_output[3] ? HIGH : LOW);

	_pulse_high[0] = digital_output[0];
	_pulse_high[1] = digital_output[1];
	_pulse_high[2] = digital_output[2];
	_pulse_high[3] = digital_output[3];
}

void
loop() {
	int rv;
	Packet packet;
	bool send_ack = false;

	Command_readToQueue();
	rv = Command_parseQueue(&packet);

	if (rv == 0) {
		Serial.println("kekw");
        Serial.write(packet.header);
        Serial.write(packet.length);
        Serial.flush();
		if (packet.header == CMD_HEADER_SET_VELOCITY &&
		    packet.length == CMD_LENGTH_SET_VELOCITY) {
			int16_t velocity_forward   = packet.data[0] << 8 | packet.data[1];
			int16_t velocity_right     = packet.data[2] << 8 | packet.data[3];
			int16_t velocity_clockwise = packet.data[4] << 8 | packet.data[5];

			velocity_forward   = constrain(velocity_forward, -1000, 1000);
			velocity_right     = constrain(velocity_right, -1000, 1000);
			velocity_clockwise = constrain(velocity_clockwise, -1000, 1000);

			// calculate mecanum wheel velocities
			_velocity_fl =
			    velocity_forward + velocity_right + velocity_clockwise;
			_velocity_fr =
			    velocity_forward - velocity_right - velocity_clockwise;
			_velocity_bl =
			    velocity_forward - velocity_right + velocity_clockwise;
			_velocity_br =
			    velocity_forward + velocity_right - velocity_clockwise;

			send_ack = true;
		} else if (packet.header == CMD_HEADER_REQUEST_ACK &&
		           packet.length == CMD_LENGTH_REQUEST_ACK) {
			send_ack = true;
		}
	}

	if (send_ack) {
		packet.header = CMD_HEADER_ACK;
		packet.length = CMD_LENGTH_ACK;
		packet.data   = _tx_data;

		Command_sendData(&packet);
	}

	task_motor_control();
}
