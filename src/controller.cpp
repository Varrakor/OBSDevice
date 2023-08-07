#include <Arduino.h>

#define NUM_SCENES 8

#define LED_DATA_PIN 7
#define LED_LATCH_PIN 8
#define LED_CLOCK_PIN 9

uint16_t leds = 0xFFFF;

void setLED(int key) {
  if (key >= 0 && key < NUM_SCENES) {
    leds |= 0x00FF;
    bitClear(leds, key);
  }
  else if (key == 8 || key == 10) {
    bitClear(leds, key == 8 ? 8 : 9);
  }
  else if (key == 9 || key == 11) {
    bitSet(leds, key == 9 ? 8 : 9);
  }

  digitalWrite(LED_LATCH_PIN, LOW);
  shiftOut(LED_DATA_PIN, LED_CLOCK_PIN, MSBFIRST, (byte) ((leds >> 8) & 0x00FF));
  shiftOut(LED_DATA_PIN, LED_CLOCK_PIN, MSBFIRST, (byte) (leds & 0x00FF));
  digitalWrite(LED_LATCH_PIN, HIGH);
}

void setupLEDs() {
  Serial.begin(9600);
  pinMode(LED_LATCH_PIN, OUTPUT);
  pinMode(LED_DATA_PIN, OUTPUT);  
  pinMode(LED_CLOCK_PIN, OUTPUT);
  setLED(-1);
}

void setLEDs() {
  if (Serial.available() > 0) {
    int key = Serial.read();
    setLED(key);
  }
}

// ----- buttons -----

#define BUTTON_DATA_PIN 2
#define BUTTON_CLOCK_PIN 3
#define BUTTON_LATCH_PIN 4

uint16_t prevButtons = 0xFFFF;

#define PULSE_WIDTH 10 // microseconds
#define BUTTON_DEBOUNCE_TIME 100 // milliseconds

unsigned long lastButtonDebounce = 0;

void setupButtons() {
  pinMode(BUTTON_DATA_PIN, INPUT);
  pinMode(BUTTON_CLOCK_PIN, OUTPUT);
  pinMode(BUTTON_LATCH_PIN, OUTPUT);
  digitalWrite(BUTTON_LATCH_PIN, HIGH);
}

byte getByte() {
  byte b = 0xFF;
  for (int i = 7; i >= 0; i--) {
    if(!digitalRead(BUTTON_DATA_PIN)) {
      bitClear(b, i);
    }
    digitalWrite(BUTTON_CLOCK_PIN, HIGH);
    delayMicroseconds(PULSE_WIDTH);
    digitalWrite(BUTTON_CLOCK_PIN, LOW);
  }
  return b;
}

void getButtons() {
  digitalWrite(BUTTON_LATCH_PIN, LOW);    
  delayMicroseconds(PULSE_WIDTH);
  digitalWrite(BUTTON_LATCH_PIN, HIGH);

  uint16_t buttons = 0;
  for (int i = 8; i >= 0; i -= 8) {
    buttons |= ((uint16_t) getByte()) << i;
  }

  unsigned long time = millis();
  for (int i = 0; i < 16; i++) {
    if (
      !bitRead(buttons, i) &&
      bitRead(prevButtons, i) &&
      time - lastButtonDebounce > BUTTON_DEBOUNCE_TIME
    ) {
      Serial.write(i);
      lastButtonDebounce = time;
    }
  }
  prevButtons = buttons;
}

// ----- rotor -----

#define ROTOR_CLK 5
#define ROTOR_DT 6

#define FIDELITY 1

int counter = 0; 
int lastState = 0;

int aState;
int aLastState; 

#define ROTOR_DEBOUNCE_TIME 0 // milliseconds

unsigned long lastRotorDebounce = 0;

// keys
#define ROTOR_DEC 13
#define ROTOR_INC 14

void setupRotor() {
  pinMode(ROTOR_CLK, INPUT_PULLUP);
  pinMode(ROTOR_DT, INPUT_PULLUP);
  aLastState = digitalRead(ROTOR_CLK); 
}

void getRotor() {
  int val = 0;
  aState = digitalRead(ROTOR_CLK);
  unsigned long time = millis();

  if (aState != aLastState && time - lastRotorDebounce > ROTOR_DEBOUNCE_TIME) {
    if (digitalRead(ROTOR_DT) != aState) ++counter; 
    else --counter; 

    if (abs(counter - lastState) >= FIDELITY) {
      val = counter > lastState ? ROTOR_INC : ROTOR_DEC;
      lastState = counter;
    }
    lastRotorDebounce = time;
  } 
  aLastState = aState;
  if (val) Serial.write(val);
}

// -----------------

void setup() {
  Serial.begin(9600);
  setupLEDs();
  setupButtons();
  setupRotor();
}

void loop() {
  setLEDs();
  getButtons();
  getRotor();
}

