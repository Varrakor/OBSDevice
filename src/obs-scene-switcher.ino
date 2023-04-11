#include "Keyboard.h"

#define NUM_BUTTONS 4
#define DELAY 100 // milliseconds

int buttons[] = { 5, 4, 3, 2 }; // pin numbers corresponding to scene index 0-3
int leds[] = { 11, 10, 9, 8 };

int modeButton = 7; // this is an interrupt pin
int modeLED = 6;

int mode = 0; // Serial or HID

int reads[NUM_BUTTONS];

unsigned long lastButtonTime = 0;

/**
  Toggle mode between Serial and HID.
  Serial is more customisable whereas HID works without needing to run the accompaying python script.
*/
void toggleMode() {
  if (millis() - lastButtonTime > DELAY) {
    mode = 1 - mode;
    if (mode == 0) digitalWrite(modeLED, HIGH); // mode LED on for Serial
    else digitalWrite(modeLED, LOW);
    lastButtonTime = millis();
  }
  while(digitalRead(modeButton));
}

void setup() {
  for(int i = 0; i < NUM_BUTTONS; ++i) pinMode(buttons[i], INPUT);
  for(int i = 0; i < NUM_BUTTONS; ++i) pinMode(leds[i], OUTPUT);

  pinMode(modeButton, INPUT);
  pinMode(modeLED, OUTPUT);

  digitalWrite(modeLED, HIGH); // start in Serial mode

  Serial.begin(9600);
  Keyboard.begin();

  attachInterrupt(digitalPinToInterrupt(modeButton), toggleMode, RISING);
}

void loop() {
  // read button inputs
  for(int i = 0; i < NUM_BUTTONS; ++i) reads[i] = digitalRead(buttons[i]);

  // if a button is pressed, send data to host
  if (millis() - lastButtonTime > DELAY) {
    for(int i = 0; i < NUM_BUTTONS; ++i) {
      if(reads[i] == HIGH) {
        if (mode == 0) Serial.write(i);
        else Keyboard.write('0'+ i); // ASCII value 
        lastButtonTime = millis(); 
        break;
      }
    }
  }

  // receive scene number from host and light up that LED 
  if (Serial.available() > 0) {
    int scene = Serial.read();
    for(int i = 0; i < NUM_BUTTONS; ++i) {
      if (scene == i) {
        digitalWrite(leds[i], HIGH);
        for(int j = 0; j < NUM_BUTTONS; ++j) {
          if(j != i) digitalWrite(leds[j], LOW);
        }
        break;
      }
    }
  }
}