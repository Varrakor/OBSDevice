#include <Arduino.h>
#include <Encoder.h>
#include <ShiftRegister74HC595.h>

#define NUM_SCENES 8

#define LED_DATA_PIN 7
#define LED_LATCH_PIN 8
#define LED_CLOCK_PIN 9

ShiftRegister74HC595<2> sr(LED_DATA_PIN, LED_CLOCK_PIN, LED_LATCH_PIN);

void setLED(int key) {
  if (key >= 0 && key < NUM_SCENES) {
    for (int i = 0; i < NUM_SCENES; ++i) sr.set(i, HIGH);
    sr.set(key, LOW);
  }
  else if (key == 8 || key == 10) {
    sr.set(key == 8 ? 8 : 9, LOW);
  }
  else if (key == 9 || key == 11) {
    sr.set(key == 9 ? 8 : 9, HIGH);
  }
}

void setupLEDs() {
  sr.setAllHigh();
}

void setLEDs() {
  if (Serial.available() > 0) {
    int key = Serial.read();
    setLED(key);
  }
}

// ----- buttons -----

#define BUTTON_DATA_PIN 4
#define BUTTON_CLOCK_PIN 5
#define BUTTON_LATCH_PIN 6

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

// ----- rotary encoder -----

#define ENC_A 2 // the two interrupt pins
#define ENC_B 3

#define ENCODER_DEC 13
#define ENCODER_INC 14

Encoder Enc(ENC_A, ENC_B);

long pos = 0;

void setupEncoder() {
  pos = Enc.read();
}

void getEncoder() {
  long newPos = Enc.read();
  if (abs(newPos - pos) >= 2) {
    Serial.write(newPos < pos ? ENCODER_INC : ENCODER_DEC);
    pos = newPos;
  }
}

// -----------------

void setup() {
  Serial.begin(9600);
  setupLEDs();
  setupButtons();
  setupEncoder();
}

void loop() {
  setLEDs();
  getButtons();
  getEncoder();
}

