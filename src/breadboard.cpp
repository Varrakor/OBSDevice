#include <Arduino.h>
#include <Keypad.h>

// ----- lEDs -----

#define NUM_SCENES 8

#define DATA_PIN 10
#define LATCH_PIN 11
#define CLOCK_PIN 12

byte bytes[] = { 0xFF, 0xFF };

/**
 * @param key 0-7 is scene LED
 * 8, 9 is stream/record on, off
 * 10, 11 is mute on, off
 */
void writeLED(int key) {
  digitalWrite(LATCH_PIN, LOW);
  
  // scenes
  if (key >= 0 && key < NUM_SCENES) {
    bytes[0] = 0xFF;
    bitClear(bytes[0], key);
  }

  else if (key == 8) bitClear(bytes[1], 0); // stream on
  else if (key == 9) bitSet(bytes[1], 0); // stream on
  else if (key == 10) bitClear(bytes[1], 1); // mute on
  else if (key == 11) bitSet(bytes[1], 1); // mute off
  
  shiftOut(DATA_PIN, CLOCK_PIN, MSBFIRST, bytes[0]);
  shiftOut(DATA_PIN, CLOCK_PIN, MSBFIRST, bytes[1]);

  digitalWrite(LATCH_PIN, HIGH);
}

void setupLEDs() {
  pinMode(DATA_PIN, OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  writeLED(-1);
}

// ----- keypad -----

#define ROWS 4
#define COLS 4

char keys[ROWS][COLS] = { { 'a', 'b', 'c', 'd' }, { 'e', 'f', 'g', 'h' }, { 'i', 'j', 'k', 'l' }, { 'm', 'n', 'o', 'p' } };

byte rowPin[COLS] = { 9, 8, 7, 6 };  // connect to L1-L4
byte colPin[ROWS] = { 5, 4, 3, 2 };  // connect to R1-R4

Keypad keypad = Keypad(makeKeymap(keys), rowPin, colPin, ROWS, COLS);

// ----- rotor -----

#define ROTOR_CLK 15
#define ROTOR_DT 16

#define FIDELITY 2

int counter = 0; 
int lastState = 0;

int aState;
int aLastState; 

void setupRotor() {
  pinMode(ROTOR_CLK, INPUT);
  pinMode(ROTOR_DT, INPUT);
  aLastState = digitalRead(ROTOR_CLK); 
}

/**
 * @return int -1 if rotor state has decremented, 1 if state has incremented, 0 if unchanged.
 */
int getRotor() {
  int val = 0;
  aState = digitalRead(ROTOR_CLK);

  if (aState != aLastState) {
    if (digitalRead(ROTOR_DT) != aState) ++counter; 
    else --counter; 

    if (abs(counter - lastState) >= FIDELITY) {
      val = counter > lastState ? 1 : -1;
      lastState = counter;
    }
  } 
  aLastState = aState;
  return val;
}

// -----------------

void setup() {
  Serial.begin(9600);
  setupLEDs();
  setupRotor();
  
}

void loop() {
  // leds
  if (Serial.available() > 0) {
    int key = Serial.read();
    writeLED(key);
  }

  // keypad
  int key = keypad.getKey() - 'a';
  if (key >= 0) Serial.write(key); // 0-15 from keypad

  // rotor
  int rotor = getRotor();
  if (rotor < 0) Serial.write(16); // 16 is rotor decrement
  else if (rotor > 0) Serial.write(17); // 17 is rotor increment
}

