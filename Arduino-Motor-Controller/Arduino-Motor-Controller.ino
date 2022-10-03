


/* Hardware Configuration:
    - Add jumper to set SpinEnable to A-STEP
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
*/

#include <Adafruit_NeoPixel.h>

// A4988 Shield
#define PIN_A4988_EN 8 // enable pin across all drivers
#define PIN_Y_DIR 6    // FL
#define PIN_A_DIR 13   // FR
#define PIN_X_DIR 5    // BL
#define PIN_Z_DIR 7    // BR
#define PIN_Y_STP 3
#define PIN_A_STP 12
#define PIN_X_STP 2
#define PIN_Z_STP 4

#define PIN_RX 0 // Serial
#define PIN_TX 1 // Serial

#define PIN_X_LIM 9           // input
#define PIN_Y_LIM 10          // input
#define PIN_Z_LIM 11          // input
#define PIN_RESET_ABORT A0    // input
#define PIN_FEED_HOLD A1      // input
#define PIN_CYCLE_START A2    // input
#define PIN_COOLANT_ENABLE A3 // input
#define PIN_SCL A4            // input
#define PIN_SDA A5            // input

// Neopixels
#define PIN PIN_SDA
#define NUMPIXELS 4

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {

}

void loop() {
}
