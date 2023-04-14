/**
 * @file main.cpp
 * @author Jasper Paterson
 * @brief To be run on an Arduino Nano. Send button presses to OBS via python script and light up correct LED
 */

#include "Arduino.h"

#define NUM_BUTTONS 4
#define DELAY 100 // milliseconds

int buttons[] = { 5, 4, 3, 2 }; // pin numbers corresponding to scene index 0-3
int leds[] = { 11, 10, 9, 8 };

int reads[NUM_BUTTONS];

unsigned long lastButtonTime = 0;

void setup() {
  for (int i = 0; i < NUM_BUTTONS; ++i) pinMode(buttons[i], INPUT);
  for (int i = 0; i < NUM_BUTTONS; ++i) pinMode(leds[i], OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // read button inputs
  for (int i = 0; i < NUM_BUTTONS; ++i) reads[i] = digitalRead(buttons[i]);

  // if a button is pressed, send data to host
  if (millis() - lastButtonTime > DELAY) {
    for (int i = 0; i < NUM_BUTTONS; ++i) {
      if (reads[i] == HIGH) {
        Serial.write(i);
        lastButtonTime = millis(); 
        break;
      }
    }
  }

  // receive scene number from host and light up that LED 
  if (Serial.available() > 0) {
    int scene = Serial.read();
    for (int i = 0; i < NUM_BUTTONS; ++i) {
      if (scene == i) {
        digitalWrite(leds[i], HIGH);
        for (int j = 0; j < NUM_BUTTONS; ++j) {
          if (j != i) digitalWrite(leds[j], LOW);
        }
        break;
      }
    }
  }
}